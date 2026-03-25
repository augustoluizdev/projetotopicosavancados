from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Event
from rest_framework.test import APITestCase
from django.urls import reverse

# Aqui ficam os testes da nossa API. Os testes são importantes para garantir que a nossa API está funcionando corretamente e para evitar regressões no futuro. Eles são uma parte fundamental do desenvolvimento de software de qualidade.
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
        self.assertEqual(u.user_email, '')
        self.assertEqual(u.user_age, 0)
        self.assertNotEqual(u.password, 'pwd')
        self.assertTrue(u.check_password('pwd'))

# Aqui estão os testes para o modelo User. Eles testam a criação de um usuário, a definição e verificação de senha, a representação em string do usuário e os valores padrão dos campos. Esses testes ajudam a garantir que o modelo User está funcionando corretamente e que as senhas estão sendo armazenadas de forma segura.
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
        self.list_url = reverse('get_all_users')
        self.register_url = reverse('register')

    def test_get_users(self):
        resp = self.client.get(self.list_url, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)

    def test_create_user_success(self):
        payload = {
            'user_nickname': 'newuser',
            'user_name': 'New User',
            'user_email': 'new@example.com',
            'user_age': 22,
            'password': 'pwd123'
        }
        resp = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data.get('user_nickname'), 'newuser')
        self.assertNotIn('password', resp.data)
        self.assertTrue(User.objects.filter(user_nickname='newuser').exists())

    def test_create_user_fail(self):
        # Envia um email inválido para forçar falha de validação (400)
        payload = {'user_nickname': 'baduser', 'user_email': 'not-an-email', 'password': 'pwd'}
        resp = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(resp.status_code, 400)