# gRPC & Protobuf

Protobuf - бинарный протокол

gRPC - фреймворк для межсервисной интеграции

Основные библиотеки для работы с protobuf и grpc
- `protobuf` - для сериализации/десериализации, работа со сгенерированными классами
- `grpcio-tools` - для кодогенерации и расширений возможности protobuf (компилятор `protoc` с обвязкой для питона)
- `grpcio` - движок gRPC


### Protobuf

Если мы хотим работать только с protobuf, то нам достаточно установить:
```bash
python3 -m pip install protobuf
```

И также нам нужен компилятор `protoc`. Так как он не зависит от языка, то его можно установить так:
```bash
brew install protobuf
```

Для генерации используется команда:
```bash
python protoc \
  -I./path/to/folder/with/proto \
  --python_out=./path/to/generated/class/file \
  --grpc_python_out=./path/to/generated/service/file  \
  ./path/to/.proto 
```
- `-I` - добавляет в список папок где искать прото файл укаазанную директорию
- `--python_out` - куда боложить сгенерированные классы
- `grpc_python_out` - куда положить сгенерированный сервис