## Docker Storage

### volumes

Тома по сути своей - это тоже вмонтированные в контейнер директории. Отличие заключается в том,
 что к ним непосредственный доступ имеет только сам докер. 

Также у томов есть имена (что логично, так как доступ к тому мы получаем по его имени а не пути в системе).

Продемонстрируем работу с `volumes`, развернув PostgreSQL докере.

```shell
docker run -d \
  --name postgres-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=db \
  -v postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network random-net \
  postgres:16-alpine
```
- `postgres:16-alpine` - версия образа
- `-p 5432:5432` - пробрасываем порт чтобы подключаться с хоста
- `-v postgres-data:/var/lib/postgresql/data` - чтобы создать `volume`, справа от двоеточия указывается его имя, а не путь к директории.
 В документации к образу написано, что данные базы храняться по пути `/var/lib/postgresql/data` в контейнере, поэтому мы монтируем наш том в эту папку.

Посмотреть тома можно командой:
```shell
docker volume ls
```

Используя команду
```shell
docker volume inspect postgres-data
```
можно посмотреть, где физически на хосте располагаются данные тома.

Запустим наш контейнер с сервисом и проверим, что всё работает.

```shell
docker build -t random-service-volume ./service

docker run -d \
  --name random-service-volume \
  --env-file service/.env \
  -p 8000:8000 \
  --network random-net \
  random-service-volume
```

Удалим контейнеры
```shell
docker rm -f random-service-volume postgres-db
```