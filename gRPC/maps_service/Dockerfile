FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY proto /proto
RUN mkdir -p /opt/generated
RUN python -m grpc_tools.protoc \
    -I/proto \
    --python_out=/opt/generated \
    --grpc_python_out=/opt/generated \
    /proto/transport.proto

ENV PYTHONPATH=/app:/opt/generated

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
