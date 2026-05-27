from datetime import datetime, timedelta
from unittest.mock import patch

import pika
from django.test import override_settings
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Cart, Event, Order, ProcessedEvent, User
from .notifications import process_order_created_payload
from .order_events import build_order_created_event
from .queries.event_queries import EVENT_LIST_CACHE_KEY, get_event_item_cache_key
from .rabbitmq import RabbitMQPublisher


# Testes dos modelos: validam regras basicas antes de testar a API.
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
        self.assertEqual(event.sold_tickets, 0)
        self.assertEqual(event.available_tickets, 100)

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


# Testes da API de usuarios: cadastro, login e CRUD via ViewSet.
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
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_list_url = reverse('users-list')

    def user_detail_url(self, nick):
        return reverse('users-detail', kwargs={'nick': nick})

    def test_get_users(self):
        response = self.client.get(self.user_list_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_get_user_by_nickname(self):
        response = self.client.get(self.user_detail_url('existing'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_nickname'], 'existing')
        self.assertNotIn('password', response.data)

    def test_create_user_success(self):
        payload = {
            'user_nickname': 'newuser',
            'user_name': 'New User',
            'user_email': 'new@example.com',
            'user_age': 22,
            'password': 'pwd1234',
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
        self.assertIn('user_email', response.data)

    def test_login_success(self):
        payload = {'user_nickname': 'existing', 'password': 'secret'}
        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_nickname'], 'existing')
        self.assertNotIn('password', response.data)

    def test_login_wrong_password(self):
        payload = {'user_nickname': 'existing', 'password': 'wrong'}
        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_update_user(self):
        payload = {
            'user_nickname': 'existing',
            'user_name': 'Updated Name',
            'user_email': 'e@example.com',
            'user_age': 31,
        }
        response = self.client.put(self.user_detail_url('existing'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_name'], 'Updated Name')

    def test_delete_user(self):
        response = self.client.delete(self.user_detail_url('existing'), format='json')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(user_nickname='existing').exists())


# Testes da API de eventos: garantem que o front consiga criar, listar e editar eventos.
class EventAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.event_list_url = reverse('event-list')
        self.event = Event.objects.create(
            title='Initial Event',
            description='Initial event description',
            date=timezone.now() + timedelta(days=5),
            location='Room 1',
            address='Event Street, 10',
            max_participants=20,
        )

    def event_detail_url(self, pk):
        return reverse('event-detail', kwargs={'pk': pk})

    def event_payload(self, **overrides):
        payload = {
            'title': 'Updated Event',
            'description': 'Descricao atualizada',
            'date': (timezone.now() + timedelta(days=15)).isoformat(),
            'location': 'Auditorio Novo',
            'address': 'Rua Atualizada, 456',
            'max_participants': 80,
        }
        payload.update(overrides)
        return payload

    def test_list_events(self):
        response = self.client.get(self.event_list_url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_create_event(self):
        payload = {
            'title': 'Django Meetup',
            'description': 'Aprendizado sobre Django REST Framework',
            'date': (timezone.now() + timedelta(days=10)).isoformat(),
            'location': 'Auditorio',
            'address': 'Rua do Evento, 123',
            'max_participants': 50,
        }
        response = self.client.post(self.event_list_url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Django Meetup')

    def test_update_event(self):
        payload = self.event_payload()
        response = self.client.put(self.event_detail_url(self.event.pk), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Event')

    def test_delete_event(self):
        response = self.client.delete(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_list_events_cache_miss_then_hit(self):
        self.assertIsNone(cache.get(EVENT_LIST_CACHE_KEY))

        first_response = self.client.get(self.event_list_url, format='json')

        self.assertEqual(first_response.status_code, 200)
        self.assertIsNotNone(cache.get(EVENT_LIST_CACHE_KEY))

        Event.objects.filter(pk=self.event.pk).update(title='Changed outside cache')
        second_response = self.client.get(self.event_list_url, format='json')

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data[0]['title'], 'Initial Event')

    def test_retrieve_event_cache_miss_then_hit(self):
        cache_key = get_event_item_cache_key(self.event.pk)
        self.assertIsNone(cache.get(cache_key))

        first_response = self.client.get(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(first_response.status_code, 200)
        self.assertIsNotNone(cache.get(cache_key))

        Event.objects.filter(pk=self.event.pk).update(title='Changed outside cache')
        second_response = self.client.get(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data['title'], 'Initial Event')

    def test_create_event_invalidates_list_cache(self):
        self.client.get(self.event_list_url, format='json')
        self.assertIsNotNone(cache.get(EVENT_LIST_CACHE_KEY))

        response = self.client.post(
            self.event_list_url,
            self.event_payload(title='Created Event'),
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(cache.get(EVENT_LIST_CACHE_KEY))

    def test_update_event_invalidates_cache_and_next_read_returns_new_data(self):
        item_cache_key = get_event_item_cache_key(self.event.pk)
        self.client.get(self.event_list_url, format='json')
        self.client.get(self.event_detail_url(self.event.pk), format='json')
        self.assertIsNotNone(cache.get(EVENT_LIST_CACHE_KEY))
        self.assertIsNotNone(cache.get(item_cache_key))

        response = self.client.put(
            self.event_detail_url(self.event.pk),
            self.event_payload(title='Updated Cached Event'),
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(cache.get(EVENT_LIST_CACHE_KEY))
        self.assertIsNone(cache.get(item_cache_key))

        read_response = self.client.get(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.data['title'], 'Updated Cached Event')
        self.assertIsNotNone(cache.get(item_cache_key))

    def test_partial_update_event_invalidates_list_and_item_cache(self):
        item_cache_key = get_event_item_cache_key(self.event.pk)
        self.client.get(self.event_list_url, format='json')
        self.client.get(self.event_detail_url(self.event.pk), format='json')

        response = self.client.patch(
            self.event_detail_url(self.event.pk),
            {'title': 'Partially Updated Event'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(cache.get(EVENT_LIST_CACHE_KEY))
        self.assertIsNone(cache.get(item_cache_key))

        read_response = self.client.get(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.data['title'], 'Partially Updated Event')

    def test_delete_event_invalidates_list_and_item_cache(self):
        item_cache_key = get_event_item_cache_key(self.event.pk)
        self.client.get(self.event_list_url, format='json')
        self.client.get(self.event_detail_url(self.event.pk), format='json')
        self.assertIsNotNone(cache.get(EVENT_LIST_CACHE_KEY))
        self.assertIsNotNone(cache.get(item_cache_key))

        delete_response = self.client.delete(self.event_detail_url(self.event.pk), format='json')

        self.assertEqual(delete_response.status_code, 204)
        self.assertIsNone(cache.get(EVENT_LIST_CACHE_KEY))
        self.assertIsNone(cache.get(item_cache_key))

        detail_response = self.client.get(self.event_detail_url(self.event.pk), format='json')
        list_response = self.client.get(self.event_list_url, format='json')

        self.assertEqual(detail_response.status_code, 404)
        self.assertIsNone(cache.get(item_cache_key))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data, [])


# Testes do fluxo de compra: carrinho, checkout e historico de pedidos.
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

    @patch('api_rest.views.publish_order_created_event')
    def test_checkout_publishes_order_created_event_after_commit(self, publish_order_created_event):
        add_url = reverse('add_to_cart', kwargs={'nick': self.user.user_nickname})
        checkout_url = reverse('checkout_cart', kwargs={'nick': self.user.user_nickname})

        add_response = self.client.post(
            add_url,
            {'event_id': self.event.id, 'quantity': 2},
            format='json',
        )
        self.assertEqual(add_response.status_code, 201)

        with self.captureOnCommitCallbacks(execute=True):
            checkout_response = self.client.post(checkout_url, {}, format='json')

        self.assertEqual(checkout_response.status_code, 201)
        publish_order_created_event.assert_called_once()

        published_event = publish_order_created_event.call_args.args[0]
        self.assertTrue(published_event.event_id)
        self.assertEqual(published_event.order_id, checkout_response.data['id'])
        self.assertEqual(published_event.user_nickname, self.user.user_nickname)
        self.assertEqual(published_event.user_email, self.user.user_email)
        self.assertEqual(len(published_event.items), 1)
        self.assertEqual(published_event.items[0].event_id, self.event.id)
        self.assertEqual(published_event.items[0].title, self.event.title)
        self.assertEqual(published_event.items[0].quantity, 2)

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
        self.assertEqual(response.data['error'], 'O carrinho esta vazio.')


class OrderCreatedEventTests(TestCase):
    def test_build_order_created_event_from_order(self):
        user = User.objects.create(
            user_nickname='eventbuyer',
            user_name='Event Buyer',
            user_email='eventbuyer@example.com',
            user_age=28,
            password='hashed-password',
        )
        event = Event.objects.create(
            title='Backend Summit',
            description='Evento para testar payload de mensageria',
            date=timezone.now() + timedelta(days=7),
            location='Centro de Eventos',
            address='Rua B, 200',
            max_participants=50,
        )
        order = Order.objects.create(user=user)
        order.items.create(event=event, quantity=3)

        order_event = build_order_created_event(order)

        self.assertTrue(order_event.event_id)
        self.assertEqual(order_event.order_id, order.id)
        self.assertEqual(order_event.user_nickname, user.user_nickname)
        self.assertEqual(order_event.user_email, user.user_email)
        self.assertEqual(len(order_event.items), 1)
        self.assertEqual(order_event.items[0].event_id, event.id)
        self.assertEqual(order_event.items[0].title, event.title)
        self.assertEqual(order_event.items[0].quantity, 3)


class NotificationProcessingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_nickname='notifybuyer',
            user_name='Notify Buyer',
            user_email='notifybuyer@example.com',
            user_age=31,
            password='hashed-password',
        )
        self.order = Order.objects.create(user=self.user)

    def test_process_order_created_payload_updates_status_and_idempotency(self):
        payload = {
            'event_id': 'evt-123',
            'order_id': self.order.id,
            'user_nickname': self.user.user_nickname,
            'user_email': self.user.user_email,
            'created_at': self.order.created_at.isoformat(),
            'items': [],
        }

        with self.assertLogs('api_rest.notifications', level='INFO') as logs:
            result = process_order_created_payload(payload)

        self.assertEqual(result, Order.NotificationStatus.NOTIFICATION_SENT)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status_notificacao,
            Order.NotificationStatus.NOTIFICATION_SENT,
        )
        self.assertIsNotNone(self.order.data_processamento)
        self.assertTrue(ProcessedEvent.objects.filter(event_id='evt-123', order=self.order).exists())
        self.assertIn('"status": "notification_sent"', logs.output[0])
        self.assertIn(f'"order_id": {self.order.id}', logs.output[0])

    def test_duplicate_payload_is_discarded(self):
        payload = {'event_id': 'evt-duplicate', 'order_id': self.order.id}

        first_result = process_order_created_payload(payload)
        second_result = process_order_created_payload(payload)

        self.assertEqual(first_result, Order.NotificationStatus.NOTIFICATION_SENT)
        self.assertEqual(second_result, 'duplicate_discarded')
        self.assertEqual(ProcessedEvent.objects.filter(event_id='evt-duplicate').count(), 1)

    def test_order_status_endpoint(self):
        self.order.status_notificacao = Order.NotificationStatus.NOTIFICATION_SENT
        self.order.data_processamento = timezone.now()
        self.order.save(update_fields=['status_notificacao', 'data_processamento'])

        response = self.client.get(reverse('order_status', kwargs={'order_id': self.order.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['user_id'], self.user.user_nickname)
        self.assertEqual(response.data['status_notificacao'], 'notification_sent')


class ObservabilityAndResilienceTests(APITestCase):
    @override_settings(RABBITMQ_HEALTH_CHECK_ENABLED=False)
    def test_health_check_endpoint_is_accessible(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)

    def test_metrics_endpoint_is_accessible(self):
        response = self.client.get('/metrics')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'django', response.content)

    @patch('api_rest.rabbitmq.pika.BlockingConnection')
    def test_rabbitmq_publisher_retries_limited_attempts(self, blocking_connection):
        blocking_connection.side_effect = pika.exceptions.AMQPConnectionError('rabbit down')
        publisher = RabbitMQPublisher()

        with self.assertRaises(pika.exceptions.AMQPConnectionError):
            publisher.publish_order_created(build_order_created_event(self._make_order()))

        self.assertEqual(blocking_connection.call_count, 3)

    def _make_order(self):
        user = User.objects.create(
            user_nickname='retrybuyer',
            user_name='Retry Buyer',
            user_email='retrybuyer@example.com',
            user_age=33,
            password='hashed-password',
        )
        event = Event.objects.create(
            title='Retry Summit',
            description='Evento para teste de retry',
            date=timezone.now() + timedelta(days=3),
            location='Sala 2',
            address='Rua Retry, 10',
            max_participants=20,
        )
        order = Order.objects.create(user=user)
        order.items.create(event=event, quantity=1)
        return order
