from django.forms import (ModelForm, ModelChoiceField,
                          ModelMultipleChoiceField, FileInput)
from mptt.forms import TreeNodeMultipleChoiceField

from .models import (UserOrder, Comment,
                     User, Order,
                     Group, PersonalGroup,
                     Signature, Message,
                     Comment, PersonalGroup)


class UserOrderAcceptedForm(ModelForm):

    class Meta:
        model = UserOrder
        fields = ['is_accepted', 'is_completed']


class TestForm(ModelForm):
    users = ModelChoiceField(queryset=User.objects.all())
    orders = ModelChoiceField(queryset=Order.objects.all())

    class Meta:
        model = Comment
        fields = ['text']


class MessageForm(ModelForm):

    class Meta:
        model = Message
        fields = ['text']
        labels = {'text': 'Текст'}


class PersonalGroupForm(ModelForm):

    class Meta:
        model = PersonalGroup
        fields = ['title', 'members']
        labels = {'title': 'Название', 'members': 'Члены группы'}


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Текст'}


class OrderForm(ModelForm):
    users = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Получатели'
    )
    groups = TreeNodeMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Группы'
    )
    personal_groups = ModelMultipleChoiceField(
        queryset=PersonalGroup.objects.all(),
        required=False,
        label='Ваши группы'
    )
    signers = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Подписанты'
    )

    class Meta:
        model = Order
        fields = ['text', 'title', 'users', 'groups',
                  'personal_groups', 'signers', 'number']
        labels = {'text': 'Текст', 'title': 'Название', 'number': 'Номер'}


class OrderSignForm(ModelForm):

    class Meta:
        model = Signature
        fields = ['signature']
        widgets = {'signature': FileInput()}
