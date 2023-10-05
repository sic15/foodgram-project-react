# praktikum_new_diplom
## Описание проекта
Социальная сеть с возможностью выкладывать фото и состав рецептов. Добавлять рецепты в избранное, подписываться на авторов. А так же составлять список покупок для выбранных рецептов

## Стек
Python 3.9, Docker, Nginx, PostgreSQL, Gunicorn, GitHub Actions

## Развернутый проект
https://https://tasty-food.sytes.net/

## Отличия файлов docker-compose.yml и docker-compose.production.yml
Первый файл необходим для создания образов контейнеров, которые впоследствии будут использованы в docker-compose.production.yml

docker-compose.yml используется для тестирования изменений, вносимых в проект.
docker-compose.production.yml используется для деплоя проекта на сервер.
## Запуcк проекта:
1) скопировать проект с github git clone git@github.com:Your_account/foodgram-project-react.git
2) В директории /foodgram/infra/ создайте файл .env Шаблон заполнения .env: 
POSTGRES_DB 
POSTGRES_USER  
POSTGRES_PASSWORD 
DB_NAME 
DB_HOST
DB_PORT
SECRET_KEY
DEBUG
ALLOWED_HOSTS
3) На github необходимо создать следующие "секреты":
        DOCKER_PASSWORD
        Updated
        DOCKER_USERNAME
        HOST
        SSH_KEY
        SSH_PASSPHRASE
        TELEGRAM_TO
        TELEGRAM_TOKEN
        USER
        
4) В файлах docker-compose.production и main необходимо вставить свой логин DockerHub
5) Для запуска на локальном сервере:
   
   `docker compose up` # запускаем сеть контейнеров
   
   `docker compose exec backend python manage.py migrate` # выполянем миграции
   
   `docker compose exec backend python manage.py collectstatic` # собираем статику
   
   `docker compose exec backend cp -r /app/backend_static/. /backend_static/static/` # копируем статику в /backend_static/static/
## Об авторе
Автор фронтенда Яндекс.Практикум.

Бэкэнд и сброка: студентка Яндекс.Практикума Наталья Арлазарова
