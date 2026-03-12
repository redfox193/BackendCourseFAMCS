## Docker Networking

На этом шаге посмотрим, как устроены сети в докере и как контейнеры 
могут общаться между собой.

Создадим простой проект: сервис, который будет возвращать случайное число и клиента.

```shell
+---client
|   |   Dockerfile
|   |   requirements.txt
|   \---app
|           main.py
\---service
    |   Dockerfile
    |   requirements.txt
    \---app
            main.py
```

Запустим для начала только сервис:
```shell
docker build -t random-service ./service
docker run -d --name random-service -p 8000:8000 random-service
```

Можно убедиться, что локально запущенный клиент может дойти до сервиса. 

Запустим клиента в контейнере:
```shell
docker build -t random-client ./client
docker run -it --name random-client random-client
```

В логах контейнера видим `request error`. Это связано с тем, 
что в контейнере клиент отправляет запрос на `localhost:8000`, то есть
 самому себе на порт `8000`. Нам же нужно указать в переменной окружения url 
сервиса.

В докере доступ к контейнеру можно получить по его IP-адресу или его имени, которое
 фиксируется как доменное.

Передадим верный url сервсиса через переменную окружения:
```shell
docker rm -f random-client
docker run -it --name random-client -e RANDOM_SERVICE_URL=http://random-service:8000 random-client
```
- `-e` используется для указание переменных окружения

Есть шанс, что в этом случае ошибка останется. Тогда лучше всего явно создать свою сеть. По умолчанию все
 контейнеры в сеть `bridge`. Контейнеры имеют доступ по имени только, когда они в одной сети.

```shell
# 1. Создаём сеть
docker network create random-net

# 2. Останавливаем и удаляем старые контейнеры (если они есть)
docker rm -f random-service random-client

# 3. Запускаем сервис в сети random-net
docker run -d --name random-service --network random-net -p 8000:8000 random-service

# 4. Запускаем клиента в сети random-net
docker run -it --name random-client --network random-net -e RANDOM_SERVICE_URL=http://random-service:8000 random-client
```

Теперь запросы клиента успешно доходят до сервиса.

Все сети докера можно посмотреть командой:
```shell
docker network ls
```

Убедимся, что наши контейнеры находятся в сети `random-net`:
```shell
docker network inspect random-net
```

Запустим ещё одного клиента с передачей переменной окружения через файл:
```shell
docker run -it --network random-net --env-file ./client/.env random-client
```