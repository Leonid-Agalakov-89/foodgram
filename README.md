## О проекте:

Веб-приложение для публикации рецептов блюд и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Проект доступен по ссылке:

```
- https://foodgram89.work.gd
- https://91.238.222.222
```

Проект позволяет:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок


## Как запустить проект:

1. Сделайте форк репозитория с гитхаб.
2. Настройте Secrets and variables для Actions в настройках своего гитхаба:
    - DOCKER_USERNAME
    - DOCKER_PASSWORD
    - HOST - IP-адрес вашего сервера
    - SSH_PASSWORD - пароль от вашего сервера
    - USER - имя пользователя от вашего сервера
    - TELEGRAM_TO - ваш ID в Telegram
    - TELEGRAM_TOKEN - токен вашего бота в Telegram (для отправки сообщений об успешном запуске проекта на сервере)
    - SECRET_KEY - Это большое случайное число, применяемое для защиты от CSRF. Важно, чтобы ключ, используемый в продакшене, не указывался в исходном коде, и/или не запрашивался с другого сервера. Django рекомендует размещать значение ключа либо в переменной окружения, или в файле с доступом только на чтение. Настройка используется в файле settings.py.


3. Создайте на сервере в домашней директории папку `/foodgram`.

4. В корне этой папке создайте файл .env и заполните данные по примеру `.env.example`

5. Получите доменное имя для вашего сайта.

6. В настройках nginx на сервере сделайте прокси для всех запросов:
```
server {

    server_name имя_вашего_сайта;

        location / {
        proxy_pass http://127.0.0.1:8000;
        
		}

```
7. Настройте cerbot, запустите его и получите ssl сертификат для вашего сайта

8. Перезапустите nginx.

9. Теперь любой push на GitHub в этот репозиторий в ветку main автоматически запустит Flake8-тест кода, загрузит образы контейнеров в ваш аккаунт на DockerHub и развернёт проект на сервере.


## Технологии:

Docker

Backend
* Django
* djangorestframework
* djoser
* PostgreSQL

Frontend
* JavaScript
* React

WSGI сервер
* Gunicorn

WEB сервер
* NGINX

CD/CI
* Github Actions


## Об авторе:
Леонид Агалаков - python backend developer.
`https://github.com/Leonid-Agalakov-89`
