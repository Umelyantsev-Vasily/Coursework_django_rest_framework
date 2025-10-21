import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from habits.models import Habit
import logging

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message):
    """Отправка сообщения через Telegram API"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не настроен")
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Сообщение отправлено в chat_id {chat_id}")
            return True
        else:
            logger.error(f"Ошибка Telegram API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False


@shared_task
def send_habit_reminder(habit_id):
    """Отправка напоминания о привычке"""
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        if not user.telegram_chat_id:
            logger.warning(f"У пользователя {user.username} не установлен telegram_chat_id")
            return False

        message = (
            f"🔔 <b>Напоминание о привычке!</b>\n\n"
            f"📍 Место: {habit.place}\n"
            f"⏰ Время: {habit.time.strftime('%H:%M')}\n"
            f"🎯 Действие: {habit.action}\n"
            f"⏱️ Время на выполнение: {habit.duration} секунд"
        )

        if habit.reward:
            message += f"\n🎁 Вознаграждение: {habit.reward}"
        elif habit.related_habit:
            message += f"\n🔗 Связанная привычка: {habit.related_habit.action}"

        success = send_telegram_message(user.telegram_chat_id, message)

        if success:
            habit.last_completed = timezone.now()
            habit.save(update_fields=['last_completed'])

        return success

    except Habit.DoesNotExist:
        logger.error(f"Привычка с id {habit_id} не найдена")
        return False


@shared_task
def check_due_habits():
    """Проверка привычек, которые нужно выполнить сейчас"""
    now = timezone.now()
    current_time = now.time()

    logger.info(f"Проверка привычек в {current_time}")

    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        is_pleasant=False
    )

    sent_count = 0
    for habit in habits:
        if habit.last_completed:
            last_date = habit.last_completed.date()
            days_passed = (now.date() - last_date).days
            if days_passed < habit.periodicity:
                continue

        send_habit_reminder.delay(habit.id)
        sent_count += 1

    if sent_count > 0:
        logger.info(f"Отправлено напоминаний: {sent_count}")

    return sent_count
