from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from habits.models import Habit
from bot.tasks import send_telegram_message, send_habit_reminder, check_due_habits

User = get_user_model()


class TelegramTasksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            telegram_chat_id='123456789'
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='08:00:00',
            action='Бегать',
            duration=120
        )

    @patch('bot.tasks.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """Тест успешной отправки сообщения в Telegram"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = send_telegram_message('123456789', 'Тестовое сообщение')

        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('bot.tasks.requests.post')
    def test_send_telegram_message_failure(self, mock_post):
        """Тест неудачной отправки сообщения в Telegram"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = send_telegram_message('123456789', 'Тестовое сообщение')

        self.assertFalse(result)
        mock_post.assert_called_once()

    @patch('bot.tasks.send_telegram_message')
    def test_send_habit_reminder_success(self, mock_send):
        """Тест успешной отправки напоминания о привычке"""
        mock_send.return_value = True

        result = send_habit_reminder(self.habit.id)

        self.assertTrue(result)
        mock_send.assert_called_once()

    def test_send_habit_reminder_no_chat_id(self):
        """Тест отправки напоминания без chat_id"""
        self.user.telegram_chat_id = None
        self.user.save()

        result = send_habit_reminder(self.habit.id)

        self.assertFalse(result)

    def test_send_habit_reminder_invalid_habit(self):
        """Тест отправки напоминания для несуществующей привычки"""
        result = send_habit_reminder(9999)

        self.assertFalse(result)

    @patch('bot.tasks.send_habit_reminder.delay')
    def test_check_due_habits(self, mock_reminder):
        """Тест проверки привычек для выполнения"""
        from django.utils import timezone

        # Создаем привычку с текущим временем
        now = timezone.now()
        current_time = now.time()

        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=current_time,
            action='Читать',
            duration=60,
            is_pleasant=False
        )

        result = check_due_habits()

        # Проверяем, что задача была вызвана
        self.assertTrue(mock_reminder.called)
