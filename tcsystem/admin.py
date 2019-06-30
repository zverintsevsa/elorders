from django.contrib import admin

from .models import (Order, Comment, Group, Message, Chat,
                     UserOrder, PersonalGroup, Signature, UserProfile, CA)


admin.site.register(Order)
admin.site.register(Comment)
admin.site.register(Group)
admin.site.register(Message)
admin.site.register(Chat)
admin.site.register(UserOrder)
admin.site.register(PersonalGroup)
admin.site.register(Signature)
admin.site.register(UserProfile)
admin.site.register(CA)
