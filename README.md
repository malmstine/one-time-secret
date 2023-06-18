# One time secret service

Uses postgres with asynchronous communication and alembic for migration

## Quick install
Для установки на хосте обязательно наличие `docker` и `docker-compose`.
Для удобства создания используются CLI команды.
1. Create image 
```
python3 manage.py build --target production
```
2. Run test. Created postgres image for duration of testing, after which it is deleted
```
python3 manage.py test
```
3. Run `docker-compose`. Migrations applied automatic with alembic
```
docker-compose up
```

## Tests
Written as unittests and integration with async
client testing with over 90 percent coverage