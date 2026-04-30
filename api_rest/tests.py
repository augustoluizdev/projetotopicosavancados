<<<<<<< Updated upstream
from django.test import TestCase

# Create your tests here.
=======
﻿from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Event
from rest_framework.test import APITestCase
from django.urls import reverse

class UserModelTests(TestCase):
    def test_set_and_check_password(self):
        u = User(user_nickname='nick1', user_name='Name', user_email='a@b.com', user_age=30)
        u.set_password('secret123')
        u.save()
        self.assertTrue(u.check_password('secret123'))
        self.assertFalse(u.check_password('wrong'))

    def test_str_contains_fields(self):
        u = User(user_nickname='nick2', user_name='Full Name', user_email='e@e.com', user_age=25)
        u.set_password('x')
        u.save()
        s = str(u)
        self.assertIn('nick2', s)
        self.assertIn('Full Name', s)
        self.assertIn('e@e.com', s)
        self.assertIn('25', s)

    def test_defaults_and_password_hashing(self):
        u = User(user_nickname='onlynick')
        u.set_password('pwd')
        u.save()
        self.assertEqual(u.user_name, '')
        self.assertEqual(u.user_age, 0)
        self.assertNotEqual(u.password, 'pwd')
        self.assertTrue(u.check_password('pwd'))

class EventModelTests(TestCase):
    def test_event_creation_and_str(self):
        dt = timezone.now() + timedelta(days=1)
        ev = Event.objects.create(
            title='Party',
            description='Desc',
            date=dt,
            location='Hall',
            address='Street 1',
            max_participants=100
        )
        self.assertEqual(str(ev), 'Party')
        self.assertEqual(ev.max_participants, 100)

    def test_date_is_datetime(self):
        dt = timezone.now()
        ev = Event(
            title='Meet',
            description='Desc',
            date=dt,
            location='Office',
            address='Addr',
            max_participants=10
        )
        ev.save()
        self.assertIsInstance(ev.date, datetime)

class UserAPITests(APITestCase):
    def setUp(self):
        self.user = User(user_nickname='existing', user_name='Exist', user_email='e@example.com', user_age=30)
        self.user.set_password('secret')
        self.user.save()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_list_url = reverse('users-list')

    def user_detail_url(self, nick):
        return reverse('users-detail', kwargs={'nick': nick})

    def test_get_users(self):
        resp = self.client.get(self.user_list_url, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)

    def test_get_user_by_nickname(self):
        resp = self.client.get(self.user_detail_url('existing'), format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['user_nickname'], 'existing')
        self.assertNotIn('password', resp.data)

    def test_create_user_success(self):
        payload = {
            'user_nickname': 'newuser',
            'user_name': 'New User',
            'user_email': 'new@example.com',
            'user_age': 22,
            'password': 'pwd1234'
        }
        resp = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data.get('user_nickname'), 'newuser')
        self.assertNotIn('password', resp.data)
        self.assertTrue(User.objects.filter(user_nickname='newuser').exists())

    def test_create_user_fail(self):
        payload = {'user_nickname': 'baduser', 'user_email': 'not-an-email', 'password': 'pwd'}
        resp = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user_email', resp.data)

    def test_login_success(self):
        payload = {'user_nickname': 'existing', 'password': 'secret'}
        resp = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['user_nickname'], 'existing')
        self.assertNotIn('password', resp.data)

    def test_login_wrong_password(self):
        payload = {'user_nickname': 'existing', 'password': 'wrong'}
        resp = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)

    def test_update_user(self):
        payload = {
            'user_nickname': 'existing',
            'user_name': 'Updated Name',
            'user_email': 'e@example.com',
            'user_age': 31
        }
        resp = self.client.put(self.user_detail_url('existing'), payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['user_name'], 'Updated Name')

    def test_delete_user(self):
        resp = self.client.delete(self.user_detail_url('existing'), format='json')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(User.objects.filter(user_nickname='existing').exists())

class EventAPITests(APITestCase):
    def setUp(self):
        self.event_list_url = reverse('event-list')
        self.event = Event.objects.create(
            title='Initial Event',
            description='Initial event description',
            date=timezone.now() + timedelta(days=5),
            location='Room 1',
            address='Event Street, 10',
            max_participants=20
        )

    def event_detail_url(self, pk):
        return reverse('event-detail', kwargs={'pk': pk})

    def test_list_events(self):
        resp = self.client.get(self.event_list_url, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)

    def test_create_event(self):
        payload = {
            'title': 'Django Meetup',
            'description': 'Aprendizado sobre Django REST Framework',
            'date': (timezone.now() + timedelta(days=10)).isoformat(),
            'location': 'Auditório',
            'address': 'Rua do Evento, 123',
            'max_participants': 50
        }
        resp = self.client.post(self.event_list_url, payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['title'], 'Django Meetup')

    def test_update_event(self):
        payload = {
            'title': 'Updated Event',
            'description': 'Descrição atualizada',
            'date': (timezone.now() + timedelta(days=15)).isoformat(),
            'location': 'Auditório Novo',
            'address': 'Rua Atualizada, 456',
            'max_participants': 80
        }
        resp = self.client.put(self.event_detail_url(self.event.pk), payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Updated Event')

    def test_delete_event(self):
        resp = self.client.delete(self.event_detail_url(self.event.pk), format='json')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())
>>>>>>> Stashed changes
