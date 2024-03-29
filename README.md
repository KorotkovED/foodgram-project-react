# Foodgram - «Продуктовый помощник»

Cервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а также перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


# Технологии:
    Django==3.2.19
    djangorestframework==3.14.0
    PostgreSQL
    Docker

# Запуск и работа с проектом
Чтобы развернуть проект, вам потребуется:
1) Клонировать репозиторий GitHub (не забываем создать виртуальное окружение и установить зависимости):
```python
git clone https://github.com/KorotkovED/foodgram-project-react
```
2) Создать файл ```.env``` в папке проекта _/infra/_ и заполнить его всеми ключами:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432 
DJANGO_SECRET_KEY=<ваш_django_секретный_ключ>
```
Вы можете сгенерировать ```DJANGO_SECRET_KEY``` следующим образом. 
Из директории проекта _/backend/_ выполнить:
```python
python manage.py shell
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Полученный ключ скопировать в ```.env```.

3) Собрать контейнеры:
```python
cd foodgram-project-react/infra
sudo docker-compose up -d --build
```

4) Сделать миграции, собрать статику и создать суперпользователя:
```python
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic
sudo docker-compose exec backend python manage.py createsuperuser
```

Чтобы заполнить базу данных начальными данными списка ингридиетов, а также тегами выполните:
```python
sudo docker-compose exec backend python manage.py load_ingredients
sudo docker-compose exec backend python manage.py load_tags
```
Теперь можно зайти в админку _http://<ваш хост>/admin/_ под вашим логином администратора.

## Регистрация и авторизация
В сервисе предусмотрена система регистрации и авторизации пользователей.
Обязательные поля для пользователя:
<li> Логин
<li> Пароль
<li> Email
<li> Имя
<li> Фамилия

## Права доступа к ресурсам сервиса

### неавторизованные пользователи могут:

    - создать аккаунт;
    - просматривать рецепты на главной;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;

### авторизованные пользователи могут:

    - входить в систему под своим логином и паролем;
    - выходить из системы (разлогиниваться);
    - менять свой пароль;
    - создавать/редактировать/удалять собственные рецепты;
    - просматривать рецепты на главной;
    - просматривать страницы пользователей;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;
    - работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов;
    - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок;
    - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок;

### администратор
Администратор обладает всеми правами авторизованного пользователя.
<br> Плюс к этому он может:

    - изменять пароль любого пользователя;
    - создавать/блокировать/удалять аккаунты пользователей;
    - редактировать/удалять любые рецепты;
    - добавлять/удалять/редактировать ингредиенты;
    - добавлять/удалять/редактировать теги.

# Админка
В интерфейс админ-зоны выведены следующие поля моделей и фильтры:
### Модели:
    Доступны все модели с возможностью редактирования и удаления записей.

### Модель пользователей:
    Фильтр по email и имени пользователя.

### Модель рецептов:
    В списке рецептов доступны название и авторы рецептов.
    Фильтры по автору, названию рецепта, тегам.
    Выведена информация о популярности рецепта: общее число добавлений этого рецепта в избранное пользователей.

### Модель ингредиентов:
    В списке ингредиентов доступны название ингредиента и единицы измерения.
    Фильтр по названию.

# Ресурсы сервиса

### Рецепт
Рецепт описывается полями:

    Автор публикации (пользователь).
    Название рецепта.
    Картинка рецепта.
    Текстовое описание.
    Ингредиенты: продукты для приготовления блюда по рецепту с указанием количества и единиц измерения.
    Тег.
    Время приготовления в минутах.

### Тег
Тег описывается полями:

    Название.
    Цветовой HEX-код.
    Slug.

### Ингредиент
Ингредиент описывается полями:

    Название.
    Количество (только для рецепта).
    Единицы измерения.

### Список покупок.
Список покупок скачивается в текстовом формате: shopping-list.txt.

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.

## Сайт
```python
http://51.250.65.73/

Данные от суперпользователя от админ панели:

http://51.250.65.73/admin

login: admin1234
password: admin154515

Данные от обычного пользователя сайта:

http://51.250.65.73/signin

Егор Коротков:
Почта: korot12@gmail.com
Пароль: egor154515


макар макар мак
почта: mk@gmail.com
пароль: упщк154515

```

### Об авторе
Проект выполнил Коротков Егор<br />
xrystik23@yandex.com<br />