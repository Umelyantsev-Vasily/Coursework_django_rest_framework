from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Hobit(models.Model):
    PERIODICITY_CHOICES = [
        (1, 'Ежедневно'),
        (2, 'Раз в два дня'),
        (3, 'Раз в три дня'),
        (4, 'Раз в четыре дня'),
        (5, 'Раз в пять дней'),
        (6, 'Раз в шесть дней'),
        (7, 'Раз в неделю'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=255, verbose_name='Действие')
    is_pleasant = models.BooleanField(default=False, verbose_name='Признак приятной привычки')
    related_hobit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Связанная привычка')
    periodicity = models.PositiveSmallIntegerField(choices=PERIODICITY_CHOICES, default=1, verbose_name='Периодичность')
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name='Вознаграждение')
    duration = models.PositiveSmallIntegerField(verbose_name='Время на выполнение (в секундах)')
    is_public = models.BooleanField(default=False, verbose_name='Признак публичности')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"

    def clean(self):
        # Валидация 1: Исключить одновременный выбор связанной привычки и указания вознаграждения
        if self.related_habit and self.reward:
            raise ValidationError('Нельзя указывать одновременно связанную привычку и вознаграждение.')

        # Валидация 2: Время выполнения должно быть не больше 120 секунд
        if self.duration > 120:
            raise ValidationError('Время выполнения не должно превышать 120 секунд.')

        # Валидация 3: В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError('В связанные привычки могут попадать только приятные привычки.')

        # Валидация 4: У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError('У приятной привычки не может быть вознаграждения или связанной привычки.')

        # Валидация 5: Периодичность не реже чем 1 раз в 7 дней
        if self.periodicity > 7:
            raise ValidationError('Нельзя выполнять привычку реже, чем 1 раз в 7 дней.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызов валидации перед сохранением
        super().save(*args, **kwargs)
