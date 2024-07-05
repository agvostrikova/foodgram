# Foodgram

## Описание
Сайт, на котором пользователи публикую свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка:

Клонировать репозиторий
```
git clone https://github.com/agvostrikova/foodgram
```

Для запуска приложения необходим сервер

Устанавливаем Docker Compose на сервер:

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

Создаем директорию для проекта на сервере:
```
sudo mkdir foodgram
```

Создаем файл docker-compose.production.yml в директорию проекта:
```
cd foodgram
sudo touch docker-compose.production.yml
```

Cоздаем файл переменных окружения .env в директории проекта на сервере:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=...
ALLOWED_HOSTS=127.0.0.1,localhost
```

Сохраняем секретные переменные на платформе GitHub Actions:

DOCKER_PASSWORD - пароль к аккаунту на Docker Hub

DOCKER_USERNAME - аккаунт на Docker Hub

HOST - IP адрес сервера

SSH_KEY -закрытый SSH ключ

SSH_PASSPHRASE - пароль на сервере

USER - имя пользователя на сервере

TELEGRAM_TO - ID телеграм-аккаунта

TELEGRAM_TOKEN - токен бота в телеграм

Сделайте коммит и пуш в репозиторий. Образ должен собраться и запушиться в Docker Hub
После успешного запуска worklow в телеграм-бот придет сообщение "Деплой успешно выполнен"

## Примеры запросов

Добавить рецепт: POST /recipes/create

Редактировать рецепт: PUTCH /recipes/1/edit

Просмотреть вкладку избранное: GET /favorites

