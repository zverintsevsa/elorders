from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.files.base import ContentFile, File
from django.db.models.query import QuerySet
from OpenSSL import crypto
from pygost.gost34112012256 import GOST34112012256
from pygost.gost3410 import verify
from pygost.utils import hexenc

from .models import (Order, Comment, Group, Chat,
                    Message, UserOrder, PersonalGroup,
                    Signature, CA, UserProfile)
from .forms import (UserOrderAcceptedForm, TestForm,
                    OrderForm, OrderSignForm, MessageForm,
                    CommentForm, PersonalGroupForm)


class OrderSignView(generic.base.TemplateView, generic.edit.BaseFormView):
    form_class = OrderSignForm
    template_name = 'tcsystem/order_sign.html'

    def get(self, request, *args, **kwargs):
        if self.request.user in User.objects.filter(signature__order_id=self.kwargs['pk']):
            return super().get(request, *args, **kwargs)
        return redirect('tcsystem:order-detail', self.kwargs['pk'])

    def signature_is_correct(self):
        pass 

    def get_success_url(self):
        return reverse_lazy('tcsystem:order-detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.get(pk=self.kwargs['pk'])
        context['signature_list'] = Signature.objects.filter(order_id=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        if 'signature_file' in request.FILES:
            signature_file = request.FILES['signature_file'].file.read()
            signature = Signature.objects.filter(signer=self.request.user, order=self.kwargs['pk'])[0]
            signature.signature = signature_file
            signature.date = timezone.now()
            cert = UserProfile.objects.get(user_id=self.request.user).cert
            order_hash = Order.objects.get(pk=kwargs['pk']).order_hash
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
                if crypto.verify(
                    cert,
                    signature_file,
                    order_hash,
                    'sha256'
                ):
                    signature.is_correct = False
                else:
                    signature.is_correct = True
                signature.save()
            except:
                signature.is_correct = False
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': Signature.objects.filter(order_id=self.kwargs['pk']).get(signer=self.request.user)})
        return kwargs


class OrderDetailView(LoginRequiredMixin, generic.base.TemplateView):
    template_name = 'tcsystem/order_detail.html'

    def get_order(self):
        return Order.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('tcsystem:order-detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.get_order()
        context['recipient_list'] = self.get_order().userorder_set.all()
        context['is_recipient'] = self.request.user in User.objects.filter(userorder__order_id=self.get_order())
        context['comment_list'] = Comment.objects.filter(order=self.kwargs['pk'])
        context['signable'] = self.request.user in User.objects.filter(signature__order_id=self.kwargs['pk'])
        context['closable'] = self.get_order().author == self.request.user and not self.get_order().is_closed
        context['signature_list'] = Signature.objects.filter(order_id=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        if 'is_closed' in request.POST:
            order = self.get_order()
            order.is_closed = True
            order.save()
        if 'is_accepted' in request.POST:
            user_orders = UserOrder.objects.filter(user=self.request.user, order=self.kwargs['pk'])
            if user_orders:
                user_orders[0].is_accepted = True
                user_orders[0].save()
        if 'is_completed' in request.POST:
            user_orders = UserOrder.objects.filter(user=self.request.user, order=self.kwargs['pk'])
            if user_orders:
                user_orders[0].is_completed = True
                user_orders[0].save()

            to_close = True
            for user_order in UserOrder.objects.filter(order=self.kwargs['pk']):
                if not user_order.is_completed:
                    to_close = False
                    break
            if to_close:
                order = Order.objects.get(id=self.kwargs['pk'])
                order.is_closed = True
                order.save()

        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        if self.request.user in User.objects.filter(userorder__order_id=self.kwargs['pk']) or \
            self.request.user == Order.objects.get(pk=self.kwargs['pk']).author or \
            self.request.user in User.objects.filter(signature__order_id=self.kwargs['pk']):
            return super().get(request, *args, **kwargs)
        return redirect('tcsystem:your-orders')


class YourOrderListView(LoginRequiredMixin, generic.ListView):
    template_name = 'tcsystem/your_order_list.html'

    def get_queryset(self):
        return self.request.user.orders.all().order_by('-date')


class ForYouOrderListView(LoginRequiredMixin, generic.ListView):
    template_name = 'tcsystem/for_you_order_list.html'

    def get_queryset(self):
        return Order.objects.filter(userorder__user_id=self.request.user.id).order_by('-date')


class ForSigningOrderListView(LoginRequiredMixin, generic.ListView):
    template_name = 'tcsystem/for_signing_order_list.html'

    def get_queryset(self):
        return Order.objects.filter(signature__signer_id=self.request.user.id).order_by('-date')


class OrderCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = OrderForm
    template_name = 'tcsystem/order_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['personal_groups'] = PersonalGroup.objects.filter(creator=self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy('tcsystem:order-detail', args=(self.object.id,))

    def user_order_save(self, user):
        if not user in User.objects.filter(userorder__order_id=self.object.id):
            user_order = UserOrder()
            user_order.is_accepted = False
            user_order.is_completed = False
            user_order.user = user
            user_order.order = self.object
            user_order.save()

    def signer_save(self, user):
        if not user in User.objects.filter(signature__order_id=self.object.id):
            signature = Signature()
            signature.is_correct = False
            signature.order = self.object
            signature.signer = user
            signature.save()

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.date = timezone.now()
        form.instance.is_closed = False
        if not form.instance.title:
            form.instance.title = form.instance.text[:min(len(form.instance.text),20)] + '...'

        gost3411 = GOST34112012256()
        gost3411.update(str(form.instance.author).encode())
        gost3411.update(str(form.instance.date).encode())
        gost3411.update(str(form.instance.text).encode())
        form.instance.order_hash = hexenc(gost3411.digest())
        self.object = form.save()

        check_users = self.request.POST.getlist('check_users')
        for user_id in check_users:
            self.user_order_save(User.objects.get(pk=user_id))

        check_groups = self.request.POST.getlist('check_groups')
        for group_id in check_groups:
            for user in User.objects.filter(pmembers__id=group_id):
                self.user_order_save(user)

        self.signer_save(self.request.user)
        check_susers = self.request.POST.getlist('check_susers')
        for user_id in check_susers:
            self.signer_save(User.objects.get(pk=user_id))

        check_sgroups = self.request.POST.getlist('check_sgroups')
        for group_id in check_sgroups:
            for user in User.objects.filter(pmembers__id=group_id):
                self.signer_save(user)

        return HttpResponseRedirect(self.get_success_url())


class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = CommentForm
    template_name = 'tcsystem/comment_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.now()
        form.instance.order = Order.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tcsystem:order-detail', args=(self.kwargs['pk'], ))


class UserListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'tcsystem/user_list.html'


class GroupListView(LoginRequiredMixin, generic.base.TemplateView):
    template_name = 'tcsystem/group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['personal_groups'] = PersonalGroup.objects.filter(creator=self.request.user)
        return context


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'tcsystem/user_detail.html'


class GroupDetailView(LoginRequiredMixin, generic.DetailView):
    model = Group
    template_name = 'tcsystem/group_detail.html'


class PersonalGroupDetailView(LoginRequiredMixin, generic.DetailView):
    model = PersonalGroup
    template_name = 'tcsystem/personal_group_detail.html'


class PersonalGroupCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = PersonalGroupForm
    template_name = 'tcsystem/personal_group_create.html'

    def get_success_url(self):
        return reverse_lazy('tcsystem:personal-group-detail', args=(self.object.id,))

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class ChatListView(LoginRequiredMixin, generic.ListView):
    template_name = 'tcsystem/chat_list.html'

    def get_queryset(self):
        return QuerySet.union(self.request.user.to_first.all(), self.request.user.to_second.all())


class ChatView(LoginRequiredMixin, generic.edit.BaseCreateView, generic.base.TemplateResponseMixin):
    form_class = MessageForm
    template_name = 'tcsystem/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_list'] = Message.objects.filter(chat=self.kwargs['pk'])
        context['chat'] = Chat.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.date = timezone.now()
        form.instance.chat = Chat.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tcsystem:chat', args=(self.kwargs['pk'],))

    def get(self, request, *args, **kwargs):
        if self.request.user in User.objects.filter(to_first__id=self.kwargs['pk']) or \
            self.request.user in User.objects.filter(to_second__id=self.kwargs['pk']):
            return super().get(request, *args, **kwargs)
        return redirect('tcsystem:your-orders')


class OpenChatView(LoginRequiredMixin, generic.edit.BaseCreateView):
    model = Chat
    fields = []
    chat = None

    def get(self, request, *args, **kwargs):
        return redirect('tcsystem:user-detail', self.kwargs['pk'])

    def form_valid(self, form):
        first_user = self.request.user
        second_user = User.objects.get(pk=self.kwargs['pk'])
        self.chat = self.get_chat(first_user, second_user)
        if self.chat:
            return redirect('tcsystem:chat', self.chat.id)
        else:
            form.instance.first_user = first_user
            form.instance.second_user = second_user
            return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tcsystem:chat', args=(self.object.id,))

    def get_chat(self, first_user, second_user):
        chat = Chat.objects.filter(first_user=first_user).filter(second_user=second_user)
        if chat:
            return Chat.objects.filter(first_user=first_user).filter(second_user=second_user)[0]
        chat = Chat.objects.filter(first_user=second_user).filter(second_user=first_user)
        if chat:
            return Chat.objects.filter(first_user=second_user).filter(second_user=first_user)[0]
        return None


class GetOrderHashView(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        f = Order.objects.get(pk=kwargs['pk']).order_hash
        file_for_response = ContentFile(f)
        response = HttpResponse(file_for_response, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="hash"'
        return response
