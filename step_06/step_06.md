## Docker Compose 

На предыдущем шаге, чтобы запустить сервис с базой в докере нам нужно было прописать 
следующие команды:
```shell
# создать сеть
docker network create random-net

# создать образ
docker build -t random-service-volume ./service

# запустить базу
docker run -d \
  --name postgres-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=db \
  -v postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network random-net \
  postgres:16-alpine

# запустить сервис
docker run -d \
  --name random-service-volume \
  --env-file service\.env \
  -p 8000:8000 \
  --network random-net \
  random-service-volume
```

Согласитесь каждый раз писать такие сложные команды не очень удобно.

Для упрощения работы был придуман Docker Compose для удобного управления 
многоконтейнерными приложениями. Очень удобен при локальной разработке и тестировании приложения.

Опишем конфигурацию контейнеров нашего приложения используя compose-файл:
```yaml
version: "3.9"

services:
  postgres-db:
    image: postgres:16-alpine
    container_name: postgres-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  random-service-volume:
    build:
      context: ./service
    env_file:
      - ./service/.env
    ports:
      - "8000:8000"
    depends_on:
      - postgres-db

volumes:
  postgres-data:
```
Здесь каждый контейнер представляет из себя сервис.

Теперь мы можем развернуть наше приложение одной командой:
```shell
docker-compose up -d --build
```
- `--build` - указываем, что надо пересобрать образы перед запуском

В Docker Desktop контейнеры будут объединены в один проект. 
![docker_compose.png](..%2Fasssets%2Fdocker_compose.png)

Отметим следующие вещи. Во-первых мы не создавали сеть для контейнеров, так как
 docker compose автоматически объединяет контейнеры проекта в одну сеть. При запуске можно было это увидеть:
```shell
[+] Running 2/3
 - Network step_06_default          Created   0.7s 
 ✔ Container postgres-db            Started   0.4s 
 ✔ Container random-service-volume  Started   0.7s 
```
Имя контейнера по умолчанию задаётся именем сервиса.

Имена томов, сети и образов задаются с префиксом проекта `step_06_`:
- сеть `step_06_default`
- том `step_06_postgres-data`
- docker-образ `step_06-random-service-volume:latest`

Чтобы остановить и удалить все контейнеры надо выполнить команду:
```shell
docker-compose down
```

Пересобрать образы можно командой
```shell
docker-compose build
```
