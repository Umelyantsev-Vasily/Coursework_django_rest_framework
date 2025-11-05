from django.test import TestCase
from unittest.mock import patch, MagicMock
from bot.tasks import send_telegram_message
from users.models import User
from habits.models import Habit


class TelegramTasksTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='123456789'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Test place",
            time="12:00:00",
            action="Test action",
            is_pleasant=False,
            frequency=1,
            reward="Test reward",
            estimated_time=60,
            is_public=False
        )

    @patch('bot.tasks.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """Тест успешной отправки сообщения в Telegram"""
        # Настраиваем mock для успешного ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response

        # Вызываем задачу
        result = send_telegram_message(self.user.telegram_chat_id, "Test message")

        # Проверяем результат
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('bot.tasks.requests.post')
    def test_send_telegram_message_failure(self, mock_post):
        """Тест неудачной отправки сообщения в Telegram"""
        # Настраиваем mock для неудачного ответа
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'ok': False}
        mock_post.return_value = mock_response

        # Вызываем задачу
        result = send_telegram_message(self.user.telegram_chat_id, "Test message")

        # Проверяем результат
        self.assertFalse(result)
        mock_post.assert_called_once()

    def test_send_telegram_message_no_chat_id(self):
        """Тест отправки сообщения без telegram_chat_id"""
        user_no_chat = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
            # telegram_chat_id не установлен
        )

        result = send_telegram_message(user_no_chat.telegram_chat_id, "Test message")
        self.assertFalse(result)

    @patch('bot.tasks.requests.post')
    def test_send_telegram_message_exception(self, mock_post):
        """Тест исключения при отправке сообщения"""
        # Настраиваем mock для выброса исключения
        mock_post.side_effect = Exception("Connection error")

        result = send_telegram_message(self.user.telegram_chat_id, "Test message")

        self.assertFalse(result)
        mock_post.assert_called_once()
