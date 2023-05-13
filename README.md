# praktikum_new_diplom
Проект продуктовый помощник.

##  технологии:
- Python
- Django
- Django REST framework
- Nginx
- Docker
- Postgres

### Как запустить проект на удаленном сервере:

Клонировать на удаленный сервер репозиторий:

```
git clone git@github.com:mekhaneg/foodgram-project-react.git
```
Перейти в репозиторий в командной строке 

```
cd infra
```
Необходимо создать файл .env со значениями:
        DB_ENGINE
        DB_NAME
        POSTGRES_USER
        POSTGRES_PASSWORD
        DB_HOST
        DB_PORT

Далее необходимо: 
```
в файле infra/nging.conf поменять server_name на адрес удаленного сервера
```
```
в файле backend/backend/settings.py вснести в список ALLOWE_HOSTS адрес удаленного сервера
```

из директории infra Запустить контейнеры, выполнив команды:

```
chmod +x init-letsencrypt.sh
```
```
sudo ./init-letsencrypt.sh
```

```
docker-compose up -d --build 
```
Выполнить команды:

```
sudo docker-compose exec backend python manage.py makemigrations users
```
```
sudo docker-compose exec backend python manage.py makemigrations recipes
```

```
sudo docker-compose exec backend python manage.py migrate
```

```
sudo docker-compose exec backend python manage.py createsuperuser
```

```
sudo docker-compose exec backend python manage.py collectstatic --no-input 
```
Перенести данные в базу данных:

```
sudo docker exec -it backend bash
```

```
python3 manage.py create_db
```

Далее с помощью админки необходимо создать несколько экземпляров модели Tags

```
Проект будет доступен по адресу:
https://oladushki-unadushki.ddns.net/
```
