# Foodgram

Автор проекта: Ларькин Никита

Foodgram — онлайн-сервис для публикации рецептов. Пользователи могут создавать свои рецепты, добавлять чужие в избранное, подписываться на авторов и формировать список покупок для выбранных рецептов.

Адрес проекта: https://foodnik.hopto.org/

# Технологии:
- Backend: Django 3.2 + Django REST Framework
- База данных: PostgreSQL
- Frontend: React
- Веб-сервер: Nginx
- Контейнеризация: Docker + Docker Compose

# Как запустить проект:
### Запуск только бэкенда (API)

- Клонировать репозиторий и перейти в папку бэкенда проекта:
```
git clone https://github.com/Niklapik/foodgram.git
cd foodgram/backend/
```

- Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```

- Установить зависимости:
```
pip install -r requirements.txt
```

- Выполнить миграции:
```
python manage.py migrate
```

- Запустить проект:
```
python manage.py runserver
```

### Запуск проекта в контейнерах:

- Создать файл .env в корне проекта со следующей структурой:
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - DB_HOST
    - DB_PORT
    - DB_NAME
    - SECRET_KEY
    - DEBUG
    - ALLOWED_HOSTS
- Запустить Docker Desktop;
- Запустить docker-compose:
```
docker compose -f docker-compose.production.yml up
```

### Примеры запросов к API:

- Post-запрос на регистрацию нового пользователя:
  - Необходимые для передачи данные:
    - email;
    - username;
    - first_name;
    - last_name;
    - password;
```
{{baseUrl}}/api/users/
```

- Get-запрос на получение всех рецептов:
```
{{baseUrl}}/api/recipes/
```

- Get-запрос на получение всех тегов:
```
{{baseUrl}}/api/tags/
```

