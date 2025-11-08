from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class UserAPITest(APITestCase):
    def test_user_registration(self):
        """Тест регистрации пользователя - должен работать без аутентификации"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

        response = self.client.post('/api/register/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        """Тест аутентификации пользователя"""
        # Сначала создаем пользователя
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post('/api/token/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_set_telegram_chat_id(self):
        """Тест установки Telegram chat_id"""
        # Создаем и аутентифицируем пользователя
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)

        data = {'chat_id': '123456789'}

        response = self.client.post('/api/set-telegram-chat-id/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что chat_id сохранился
        user.refresh_from_db()
        self.assertEqual(user.telegram_chat_id, '123456789')
