from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'last_completed')

    def validate(self, data):
        # Дублируем валидацию из модели для DRF
        related_habit = data.get('related_habit')
        reward = data.get('reward')
        duration = data.get('duration', 120)
        is_pleasant = data.get('is_pleasant', False)
        periodicity = data.get('periodicity', 1)

        # Валидация 1
        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя указывать одновременно связанную привычку и вознаграждение."
            )

        # Валидация 2
        if duration > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд."
            )

        # Валидация 3
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "В связанные привычки могут попадать только приятные привычки."
            )

        # Валидация 4
        if is_pleasant:
            if reward:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения."
                )
            if related_habit:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть связанной привычки."
                )

        # Валидация 5
        if periodicity > 7:
            raise serializers.ValidationError(
                "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
            )

        return data
