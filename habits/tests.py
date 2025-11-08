from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Habit
from .permissions import IsOwner

User = get_user_model()


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_habit_creation(self):
        habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='08:00:00',
            action='Бегать',
            duration=120,
            is_public=True
        )
        # Исправляем ожидаемую строку согласно новому методу __str__
        self.assertEqual(str(habit), "Я буду Бегать в 08:00:00 в Парк")
        self.assertEqual(habit.user.username, 'testuser')


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_habit_success(self):
        data = {
            'place': 'Парк',
            'time': '09:00:00',
            'action': 'Бегать',
            'duration': 120,
            'is_public': True
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.first().user, self.user)

    def test_create_habit_invalid_duration(self):
        data = {
            'place': 'Парк',
            'time': '09:00:00',
            'action': 'Бегать',
            'duration': 150,  # Больше 120 секунд
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_habits(self):
        # Создаем привычку
        Habit.objects.create(
            user=self.user,
            place='Парк',
            time='08:00:00',
            action='Бегать',
            duration=120
        )

        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_public_habits(self):
        # Создаем публичную привычку
        Habit.objects.create(
            user=self.user,
            place='Парк',
            time='08:00:00',
            action='Бегать',
            duration=120,
            is_public=True
        )

        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class HabitValidationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Создаем приятную привычку для тестов связи
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Читать книгу',
            is_pleasant=True,
            duration=120
        )

        # Создаем обычную привычку
        self.normal_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            duration=120
        )

    def test_create_habit_with_related_and_reward(self):
        """Тест: нельзя указать и связанную привычку и вознаграждение"""
        data = {
            'place': 'Парк',
            'time': '10:00:00',
            'action': 'Бегать',
            'duration': 120,
            'related_habit': self.pleasant_habit.id,
            'reward': 'Кофе'
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('связанную привычку и вознаграждение', str(response.data))

    def test_create_pleasant_habit_with_reward(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        data = {
            'place': 'Дом',
            'time': '11:00:00',
            'action': 'Смотреть сериал',
            'duration': 90,
            'is_pleasant': True,
            'reward': 'Что-то'
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не может быть вознаграждения', str(response.data))

    def test_create_pleasant_habit_with_related(self):
        """Тест: у приятной привычки не может быть связанной привычки"""
        data = {
            'place': 'Дом',
            'time': '12:00:00',
            'action': 'Слушать музыку',
            'duration': 60,
            'is_pleasant': True,
            'related_habit': self.pleasant_habit.id
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не может быть связанной привычки', str(response.data))

    def test_related_habit_must_be_pleasant(self):
        """Тест: связанная привычка должна быть приятной"""
        data = {
            'place': 'Парк',
            'time': '13:00:00',
            'action': 'Гулять',
            'duration': 120,
            'related_habit': self.normal_habit.id  # Обычная привычка, не приятная
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('только приятные привычки', str(response.data))

    def test_duration_validation(self):
        """Тест: время выполнения не больше 120 секунд"""
        data = {
            'place': 'Парк',
            'time': '14:00:00',
            'action': 'Бегать',
            'duration': 150  # Больше 120
        }

        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не должно превышать 120 секунд', str(response.data))


class HabitModelValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Читать книгу',
            is_pleasant=True,
            duration=120
        )

    def test_habit_clean_validation_related_and_reward(self):
        """Тест валидации: нельзя related_habit и reward одновременно"""
        habit = Habit(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            related_habit=self.pleasant_habit,
            reward='Кофе',
            duration=120
        )

        with self.assertRaises(Exception) as context:
            habit.full_clean()
        self.assertIn('связанную привычку и вознаграждение', str(context.exception))

    def test_habit_clean_validation_duration(self):
        """Тест валидации: duration не больше 120 секунд"""
        habit = Habit(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            duration=150
        )

        with self.assertRaises(Exception) as context:
            habit.full_clean()
        self.assertIn('не должно превышать 120 секунд', str(context.exception))

    def test_habit_clean_validation_pleasant_with_reward(self):
        """Тест валидации: у приятной привычки не может быть вознаграждения"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Слушать музыку',
            is_pleasant=True,
            reward='Что-то',
            duration=90
        )

        with self.assertRaises(Exception) as context:
            habit.full_clean()
        self.assertIn('не может быть вознаграждения', str(context.exception))


class HabitPermissionsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        self.habit = Habit.objects.create(
            user=self.user1,
            place='Парк',
            time='08:00:00',
            action='Бегать',
            duration=120
        )

        self.permission = IsOwner()

    def test_is_owner_permission_same_user(self):
        """Тест: владелец имеет доступ к своему объекту"""
        request = type('Request', (), {'user': self.user1})()
        self.assertTrue(self.permission.has_object_permission(request, None, self.habit))

    def test_is_owner_permission_different_user(self):
        """Тест: другой пользователь не имеет доступа к чужому объекту"""
        request = type('Request', (), {'user': self.user2})()
        self.assertFalse(self.permission.has_object_permission(request, None, self.habit))
