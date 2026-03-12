## Docker Storage

В докере есть два способа работы с постоянными данными
- `bind-mounts` - монтирование директорий
- `volumes` - создание томов (специальных областей памяти, которые не удаляются вместе с контейнером и которые полностью управляются докером)

### bind-mounts

Добавим в наш сервис случайных чисел базу SqLite с сохранением информации о сгенерированных числах.
 В файле `.env` укажем путь к базе внутри контейнера.

```dotenv
DB_PATH=/app/random.db
```

Создадим докер образ и запустим контейнер:
```shell
docker build -t random-service-mount ./service
```

Запустим контейнер:
```shell
docker run -d \
  --name random-service-mount \
  --env-file service/.env \
  -v "$(pwd)/service/random.db:/app/random.db" \
  -p 8000:8000 \
  random-service-mount
```
- используя флаг `-v` мы указываем, файл по пути `$(pwd)/service/random.db` будет доступен в контейнере по пути `/app/random.db`

Посмотреть все `mounts` контейнера можно так
```shell
docker inspect random-service-mount --format '{{json .Mounts}}'
```

В самом контейнере файл базы можно найти по пути `/app/random.db`. Можно убить/перезапустить контейнер, чтобы убедиться в сохранении файла базы.

Ещё один способ использовния `bind-mounts` - это монтирование кода проекта а не включение его в образ. Таким
 образом вам не нужно пересоздавать образ каждый раз, когда вы вносите изменения в проект.

Используем `new.Dockerfile`:
```Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Копируем зависимости из подкаталога app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Теперь соберём образ:
```shell
docker build -t random-service-mount-code -f service/new.Dockerfile ./service
```
- `./service` - это контекст сборки (относительно него выполняются команды в Dockerfile по копированию)
- `-f` - путь к самому Dockerfile. В данном случае указываем, так как нам нуже `new.Dockerfile`

И запустим контейнер, вмонтировав остальные файлы проекта:
```shell
docker run -d \
  --name random-service-mount-code \
  --env-file service/.env \
  -v "$(pwd)/service/app:/app" \
  -v "$(pwd)/service/random.db:/app/random.db" \
  -p 8000:8000 \
  random-service-mount-code
```

Теперь при изменении кода в папке app вам не нужно пересобирать образ, достаточно перезапустить контейнер.

**NO!** Так как мы указали флаг `--reload` у `uvicorn`, то он сам перезапустит сервис в контейнере, увидев изменения в файле