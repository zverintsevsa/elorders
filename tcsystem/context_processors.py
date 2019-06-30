from django.db.models import Q
# from django.template.context_processors import request

from . import models


def notifications(request):
    order_notifications = models.Order.objects.filter(
        userorder__user_id=request.user.id).order_by('-date')[0:9]
    message_notifications = models.Message.objects.filter(
        Q(chat__first_user_id=request.user.id) |
        Q(chat__second_user_id=request.user.id)).exclude(sender=request.user.id).order_by('-date')[0:3]
    return {'order_notifications': order_notifications, 'message_notifications': message_notifications}
