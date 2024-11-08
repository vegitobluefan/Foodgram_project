# Итоговый проект курса Foodgram
## Сайт расположен по адресу: https://foodgramdaniyar52.ddnsking.com

### Данные от админки:
https://foodgramdaniyar52.ddnsking.com/admin/
- Почта: 
```bash 
daniararinov995@gmail.com
```
- Пароль:
``` bash 
foodgram1701
```

# Описание проекта:
«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать и скачивать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Вот что было сделано в ходе работы над проектом:
- Создан собственный API-сервис на базе проекта Django
- Подключено SPA к бэкенду на Django через API
- Созданы образы и запущены контейнеры Docker
- Создано, развёрнуто и запущено на сервере мультиконтейнерное приложение
- Закреплены на практике основы DevOps

## Проект состоит из следующих страниц:
- Главная
- Страница входа
- Страница регистрации
- Страница рецепта
- Страница пользователя
- Страница подписок
- Избранное
- Список покупок
- Создание и редактирование рецепта
- Страница смены пароля
- Статические страницы «О проекте» и «Технологии»

# Запуск API:
- Склонируйте репозиторий:
```bash 
git clone ...
```    
- Установите и активируйте виртуальное окружение:
```bash
python -m venv venv 
```  
``` bash 
source venv/Scripts/activate 
``` 
- Установите зависимости из файла requirements.txt:
``` bash 
pip install -r requirements.txt 
```
- Примените миграции:
``` bash
python manage.py migrate
```
- Запустите проект:
```bash
python manage.py runserver
```
### Документация доступна по адресу:
```
http://127.0.0.1/api/docs/
```

# Запуск проекта в контейнерах
- Перейти в директорию /infra и выполнить следующие команды:
```
docker-compose build
```
```
docker-compose up -d
```
```
docker-compose up
```
- Применить миграции:
```
docker compose exec backend python manage.py makemigrations
```
```
docker compose exec backend python manage.py migrate
```
- Собрать статику:
```
docker-compose exec python manage.py collectstatic --no-input 
```
- Загрузить ингредиенты:
```
docker-compose exec backend python manage.py load_csv
```
- Создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
# Разработчик: [Аринов Данияр](https://github.com/vegitobluefan)