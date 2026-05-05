from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Cart, Event, Order, User


class UserModelTests(TestCase):
    def test_set_and_check_password(self):
        user = User(user_nickname='nick1', user_name='Name', user_email='a@b.com', user_age=30)
        user.set_password('secret123')
        user.save()

        self.assertTrue(user.check_password('secret123'))
        self.assertFalse(user.check_password('wrong'))

    def test_str_contains_fields(self):
        user = User(
            user_nickname='nick2',
            user_name='Full Name',
            user_email='e@e.com',
            user_age=25,
        )
        user.set_password('x')
        user.save()

        value = str(user)
        self.assertIn('nick2', value)
        self.assertIn('Full Name', value)
        self.assertIn('e@e.com', value)
        self.assertIn('25', value)

    def test_defaults_and_password_hashing(self):
        user = User(user_nickname='onlynick')
        user.set_password('pwd')
        user.save()

        self.assertEqual(user.user_name, '')
        self.assertEqual(user.user_email, '')
        self.assertEqual(user.user_age, 0)
        self.assertNotEqual(user.password, 'pwd')
        self.assertTrue(user.check_password('pwd'))


class EventModelTests(TestCase):
    def test_event_creation_and_str(self):
        event = Event.objects.create(
            title='Party',
            description='Desc',
            date=timezone.now() + timedelta(days=1),
            location='Hall',
            address='Street 1',
            max_participants=100,
        )

        self.assertEqual(str(event), 'Party')
        self.assertEqual(event.max_participants, 100)

    def test_date_is_datetime(self):
        event = Event.objects.create(
            title='Meet',
            description='Desc',
            date=timezone.now(),
            location='Office',
            address='Addr',
            max_participants=10,
        )

        self.assertIsInstance(event.date, datetime)


class UserAPITests(APITestCase):
    def setUp(self):
        self.user = User(
            user_nickname='existing',
            user_name='Exist',
            user_email='e@example.com',
            user_age=30,
        )
        self.user.set_password('secret')
        self.user.save()
        self.list_url = reverse('get_all_users')
        self.register_url = reverse('register')

    def test_get_users(self):
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_create_user_success(self):
        payload = {
            'user_nickname': 'newuser',
            'user_name': 'New User',
            'user_email': 'new@example.com',
            'user_age': 22,
            'password': 'pwd123',
        }
        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('user_nickname'), 'newuser')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(user_nickname='newuser').exists())

    def test_create_user_fail(self):
        payload = {'user_nickname': 'baduser', 'user_email': 'not-an-email', 'password': 'pwd'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 400)


class TicketPurchaseFlowTests(APITestCase):
    def setUp(self):
        self.user = User(
            user_nickname='buyer',
            user_name='Buyer',
            user_email='buyer@example.com',
            user_age=28,
        )
        self.user.set_password('secret')
        self.user.save()
        self.event = Event.objects.create(
            title='Tech Conference',
            description='Evento de tecnologia',
            date=timezone.now() + timedelta(days=10),
            location='Centro',
            address='Rua A, 100',
            max_participants=5,
        )

    def test_add_event_to_cart_and_checkout(self):
        add_url = reverse('add_to_cart', kwargs={'nick': self.user.user_nickname})
        checkout_url = reverse('checkout_cart', kwargs={'nick': self.user.user_nickname})
        orders_url = reverse('list_orders', kwargs={'nick': self.user.user_nickname})

        add_response = self.client.post(
            add_url,
            {'event_id': self.event.id, 'quantity': 2},
            format='json',
        )
        self.assertEqual(add_response.status_code, 201)
        self.assertEqual(len(add_response.data['items']), 1)
        self.assertEqual(add_response.data['items'][0]['quantity'], 2)

        checkout_response = self.client.post(checkout_url, {}, format='json')
        self.assertEqual(checkout_response.status_code, 201)
        self.assertEqual(checkout_response.data['status'], 'requested')
        self.assertEqual(len(checkout_response.data['items']), 1)
        self.assertEqual(checkout_response.data['items'][0]['quantity'], 2)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 0)

        orders_response = self.client.get(orders_url, format='json')
        self.assertEqual(orders_response.status_code, 200)
        self.assertEqual(len(orders_response.data), 1)

    def test_cannot_add_more_tickets_than_capacity(self):
        add_url = reverse('add_to_cart', kwargs={'nick': self.user.user_nickname})
        response = self.client.post(
            add_url,
            {'event_id': self.event.id, 'quantity': 6},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_cannot_checkout_empty_cart(self):
        checkout_url = reverse('checkout_cart', kwargs={'nick': self.user.user_nickname})
        response = self.client.post(checkout_url, {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'O carrinho está vazio.')
