from django.test import TestCase
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile, File
from django.core.files import File
from django.db.models.fields.files import FieldFile
from ..models import Order, UserOrder, Signature, UserProfile, Comment
from ..views import YourOrderListView, ForYouOrderListView, ForSigningOrderListView
from elorders.settings import MEDIA_ROOT
from django.db.models.query import QuerySet
from django.db.models.query import EmptyQuerySet

class StrModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test-user', first_name='Андрей', last_name='Петров')
        user.set_password('password')
        user.save()

        user_profile = UserProfile.objects.create(user=user, middle_name='Сергеевич')
        user_profile.save()

        file_hash = File(open(MEDIA_ROOT + '/test_file_1', 'w'))
        file_hash.write('Хеш')
        file_hash.close()
        file_hash.open('r')

        order = Order.objects.create(
            title='Название',
            text='Текст',
            date=timezone.now(),
            author=user,
            order_hash=file_hash,
            is_closed=False
        )
        file_hash.close()

        UserOrder.objects.create(
            user=user,
            order=order,
            is_accepted=False,
            is_completed=False
        )

        Comment.objects.create(
            user=user,
            order=order,
            date=timezone.now(),
            text='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'
        )

    def test_str_order(self):
        self.assertEquals(str(Order.objects.get(id=1)), 'Название')

    def test_str_userprofile(self):
        self.assertEquals(str(UserProfile.objects.get(id=1)), 'Петров А. С.')

    def test_str_userorder(self):
        self.assertEquals(str(UserOrder.objects.get(id=1)), 'Петров А. С. - Название')

    def test_str_comment(self):
        self.assertEquals(str(Comment.objects.get(id=1)), 'Lorem ipsum dolor si...')

