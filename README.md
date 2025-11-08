# 🚀 Трекер полезных привычек

Django REST API для трекера полезных привычек по методологии "Атомные привычки".

## 🛠 Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <your-repository-url>
cd coursework_django_rest_framework
```
## 2. Настройка окружения

```bash
# Копируем пример файла окружения
cp .env.example .env

# Редактируем файл .env с вашими настройками
# SECRET_KEY - сгенерируйте новый ключ для продакшена
# POSTGRES_PASSWORD - ваш пароль PostgreSQL
# TELEGRAM_BOT_TOKEN - токен вашего Telegram бота
```
## 3. Установка зависимостей
```bash

poetry install
```
## 4. База данных
```bash
# Создайте базу данных в PostgreSQL
createdb habit_tracker

# Миграции
python manage.py migrate
```
## 5. Создание суперпользователя
```bash
python manage.py createsuperuser
```

## 6. Запуск сервера
```bash
python manage.py runserver
```
## 7. Запуск Celery (в отдельном терминале)
```bash
# Worker
celery -A config worker --loglevel=info

# Beat (для периодических задач)
celery -A config beat --loglevel=info
```
---
## 🌐 API Endpoints
- Документация Swagger: http://localhost:8000/swagger/

- Документация ReDoc: http://localhost:8000/redoc/

- Админ панель: http://localhost:8000/admin/

## 🧪 Тестирование

```bash
# Запуск тестов
python manage.py test

# Покрытие тестами
python -m coverage run --source='.' manage.py test
python -m coverage report
```
---
## Деплой на сервер

### Требования
- Ubuntu 22.04
- Python 3.12
- PostgreSQL
- Redis
- Nginx

### Настройка
1. Клонировать репозиторий
2. Создать виртуальное окружение
3. Установить зависимости: `pip install -r requirements.txt`
4. Настроить .env файл из .env.example
5. Выполнить миграции: `python manage.py migrate`
6. Собрать статику: `python manage.py collectstatic`
7. Настроить Gunicorn и Nginx
---

## 🚀 Deployment Status

### Production Environment
- ✅ **GitHub Actions CI/CD** - Configured and working
- ✅ **SSH Authentication** - Set up for deployment
- ✅ **Python 3.12 + Django 5.2.7** - Installed and running
- ✅ **Gunicorn** - Service active with 3 workers
- ✅ **Nginx** - Service active and configured
- ✅ **Database Migrations** - Applied successfully
- ✅ **Static Files** - Collected and served
- ✅ **All Services** - Operational and monitoring

### Deployment Pipeline
- Automatic tests on push to  branch
- Automated deployment to production after successful tests
- Zero-downtime deployments with service restarts
- 
---

## 🌐 Работающее приложение

Приложение развернуто и доступно по адресу:  
**http://158.160.68.20/**

- Swagger документация: http://158.160.68.20/swagger/
- ReDoc документация: http://158.160.68.20/redoc/
- Админ панель: http://158.160.68.20/admin/

## 🔄 CI/CD Настройка

### GitHub Actions
Проект использует GitHub Actions для автоматического тестирования и деплоя.

#### Workflow файл
Расположение: `.github/workflows/docker-ci-cd.yml`

#### Этапы:
1. **Тестирование** - запускается при push и pull requests
2. **Деплой** - автоматический деплой на сервер при push в develop ветку

#### Настройка Secrets в GitHub:
- `SERVER_HOST` - IP адрес сервера
- `SERVER_USER` - пользователь сервера  
- `SERVER_SSH_KEY` - приватный SSH ключ

## 🚀 Деплой на сервер

### Docker-версия (рекомендуется)

#### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
sudo apt install docker.io docker-compose -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

```bash
# Клонирование репозитория
git clone <your-repository-url>
cd coursework_django_rest_framework

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск контейнеров
docker-compose up -d --build

# Выполнение миграций
docker-compose exec web python manage.py migrate

# Сбор статики
docker-compose exec web python manage.py collectstatic --noinput

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```
---
## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE)

## 👨‍💻 Разработчик
 ### Василий - tanec_991@mail.ru