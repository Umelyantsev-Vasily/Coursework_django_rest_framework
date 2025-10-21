from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwner


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        if self.action == 'list':
            # Для списка привычек текущего пользователя
            return Habit.objects.filter(user=self.request.user)
        return Habit.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
