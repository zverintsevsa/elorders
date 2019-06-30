from django.test import TestCase
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile, File
from django.core.files import File
from django.db.models.fields.files import FieldFile
from ..models import Order, UserOrder, Signature
from ..views import YourOrderListView, ForYouOrderListView, ForSigningOrderListView
from elorders.settings import MEDIA_ROOT
from django.db.models.query import QuerySet
from django.db.models.query import EmptyQuerySet

class YourOrderListViewTest(TestCase):


    def setUp(self):
        user_1 = User.objects.create(username='test-user-1')
        user_1.set_password('password-1')
        user_1.save()

        file_hash_1 = File(open(MEDIA_ROOT + '/test_file_1', 'w'))
        file_hash_1.write('Хеш-1')
        file_hash_1.close()
        file_hash_1.open('r')

        for i in range(2):
            Order.objects.create(
                title='Название-1',
                text='Текст-1',
                date=timezone.now(),
                author=user_1,
                order_hash=file_hash_1,
                is_closed=False
            )
        file_hash_1.close()


    def test_template(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:your-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tcsystem/your_order_list.html')

    def test_lists_all_orders(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:your-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('order_list' in resp.context)
        self.assertTrue( len(resp.context['order_list']) == 2)


class ForYouOrderListViewTest(TestCase):


    def setUp(self):
        user_1 = User.objects.create(username='test-user-1')
        user_1.set_password('password-1')
        user_1.save()

        file_hash_1 = File(open(MEDIA_ROOT + '/test_file_1', 'w'))
        file_hash_1.write('Хеш-1')
        file_hash_1.close()
        file_hash_1.open('r')

        order_1 = Order.objects.create(
            title='Название-1',
            text='Текст-1',
            date=timezone.now(),
            author=user_1,
            order_hash=file_hash_1,
            is_closed=False
        )
        file_hash_1.close()

        for i in range(2):
            UserOrder.objects.create(
                user=user_1,
                order=order_1,
                is_accepted=False,
                is_completed=False
            )


    def test_template(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:for-you-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tcsystem/for_you_order_list.html')

    def test_lists_all_orders(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:for-you-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('order_list' in resp.context)
        self.assertTrue( len(resp.context['order_list']) == 2)


class ForSigningOrderListViewTest(TestCase):


    def setUp(self):
        user_1 = User.objects.create(username='test-user-1')
        user_1.set_password('password-1')
        user_1.save()

        file_hash_1 = File(open(MEDIA_ROOT + '/test_file_1', 'w'))
        file_hash_1.write('Хеш-1')
        file_hash_1.close()
        file_hash_1.open('r')

        order_1 = Order.objects.create(
            title='Название-1',
            text='Текст-1',
            date=timezone.now(),
            author=user_1,
            order_hash=file_hash_1,
            is_closed=False
        )
        file_hash_1.close()

        for i in range(2):
            Signature.objects.create(
                signer=user_1,
                order=order_1,
                is_correct=False
            )


    def test_template(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:for-signing-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tcsystem/for_signing_order_list.html')

    def test_lists_all_orders(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:for-signing-orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('order_list' in resp.context)
        self.assertTrue( len(resp.context['order_list']) == 2)


class OrderDetailViewTest(TestCase):


    def setUp(self):
        user_1 = User.objects.create(username='test-user-1')
        user_1.set_password('password-1')
        user_1.save()

        file_hash_1 = File(open(MEDIA_ROOT + '/test_file_1', 'w'))
        file_hash_1.write('Хеш-1')
        file_hash_1.close()
        file_hash_1.open('r')

        order_1 = Order.objects.create(
            title='Название-1',
            text='Текст-1',
            date=timezone.now(),
            author=user_1,
            order_hash=file_hash_1,
            is_closed=False
        )
        file_hash_1.close()

        self.order_1 = order_1

        for i in range(2):
            UserOrder.objects.create(
                user=user_1,
                order=order_1,
                is_accepted=False,
                is_completed=False
            )

        Signature.objects.create(
            signer=user_1,
            order=order_1,
            is_correct=False
        )


    def test_template(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:order-detail', kwargs={'pk': self.order_1.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tcsystem/order_detail.html')

    def test_correct_order(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:order-detail', kwargs={'pk': self.order_1.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('order' in resp.context)
        self.assertEqual( resp.context['order'], self.order_1)

    def test_closable_and_signable(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:order-detail', kwargs={'pk': self.order_1.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('closable' in resp.context)
        self.assertTrue(resp.context['closable'])
        self.assertTrue('signable' in resp.context)
        self.assertTrue(resp.context['signable'])

    def test_recipients(self):
        login = self.client.login(username='test-user-1', password='password-1')
        resp = self.client.get(reverse('tcsystem:order-detail', kwargs={'pk': self.order_1.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_recipient' in resp.context)
        self.assertTrue(resp.context['is_recipient'])
        self.assertTrue('recipient_list' in resp.context)
        qs = QuerySet.difference(resp.context['recipient_list'], self.order_1.userorder_set.all())
        self.assertTrue(qs.count() == 0)