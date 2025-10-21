from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'time', 'place', 'is_pleasant', 'is_public', 'created_at')
    list_filter = ('is_pleasant', 'is_public', 'periodicity', 'created_at')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('created_at', 'last_completed')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Настройки привычки', {
            'fields': ('is_pleasant', 'related_habit', 'periodicity', 'reward', 'duration')
        }),
        ('Дополнительно', {
            'fields': ('is_public', 'created_at', 'last_completed')
        }),
    )
