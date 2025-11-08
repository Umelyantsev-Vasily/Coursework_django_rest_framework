from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя"""
    permission_classes = [AllowAny]  # Разрешаем доступ без аутентификации
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_telegram_chat_id(request):
    """Установка Telegram chat_id для пользователя"""
    chat_id = request.data.get('chat_id')

    if not chat_id:
        return Response(
            {'error': 'chat_id обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.telegram_chat_id = chat_id
    request.user.save()

    return Response(
        {'message': 'Telegram chat_id успешно установлен'},
        status=status.HTTP_200_OK
    )
