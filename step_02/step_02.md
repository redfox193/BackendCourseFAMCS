## Dockerfile

На прошлом шаге мы скачали docker-образ из Docker Hub, 
создали на основе него контейнер и изучили, как слоистая структура помогает 
экономить память.

Теперь попробуем описать свой docker-образ.

### Структура проекта

Создадим простое приложение на FastAPI и запустим его в контейнере.

```
|   Dockerfile
|
\---app
        main.py
        requirements.txt
```

Содержимое Dockerfile будет выглядеть так:
```Dockerfile
# Базовый образ
FROM python:3.13-slim

# Переходим в папку, аналог cd
WORKDIR /app

# Копируем зависимости из подкаталога app и устанавливаем
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код после установки библиотек
COPY app/main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Тут стоит обратить внимание, что мы разделяем установку библиотек и
 копирование кода, чтобы избегать лишнюю пересборку слоёв с библиотеками
 при разработке приложения.

То есть при редактировании `main.py` и обновлении образа докер под капотом пересоберёт только
 два последних слоя.

Теперь соберём docker-образ, из директории `step_02` выполним команду:
```shell
docker build -t fastapi-1:latest .
```
- `-t` используется, чтобы задать имя контейнера
- `.` - это относительный путь к `Dockerfile`

Запустим контейнер:
```shell
docker run -d --name fastapi-container -p 8000:8000 fastapi-1
```
Проверим http://localhost:8000

В папке `app/` контейнера появляются файлы кеша от питона, их можно убрать, установив переменную окружения:

```Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Копируем зависимости из подкаталога app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код после установки библиотек
COPY app/main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Убъем работающий контейнер:
```shell
docker rm -f fastapi-container
```

Пересоберём образ:
```shell
docker build -t fastapi-1:latest .
```

Запустим контейнер:
```shell
docker run -d --name fastapi-container -p 8000:8000 fastapi-1
```

Откроем консоль внутри контейнера:
```shell
docker exec -it fastapi-container sh
```

В консоли выполним команду `env`, чтобы увидеть установленную переменную окружения.

