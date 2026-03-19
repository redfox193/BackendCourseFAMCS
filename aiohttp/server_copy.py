import asyncio
from aiohttp import web

todo_list = {}
next_id = 0


async def handle_request(request: web.Request) -> web.Response:
    global todo_list, next_id

    method = request.method
    path = request.path

    # root page: GET /
    if method == "GET" and path == "/":
        html = """
        <html>
            <head><title>Todo API</title></head>
            <body>
                <h1>Available endpoints</h1>
                <ul>
                    <li>GET /todos - list all to-dos</li>
                    <li>POST /todos - add a to-do</li>
                    <li>PUT /todos/{todo_id} - edit a to-do</li>
                    <li>DELETE /todos/{todo_id} - remove a to-do</li>
                </ul>
            </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    # /todos
    if path == "/todos":
        # GET /todos
        if method == "GET":
            return web.json_response(todo_list)

        # POST /todos
        if method == "POST":
            try:
                data = await request.json()
            except Exception:
                return web.json_response(
                {"error": "Invalid JSON body"},
                status=400,
            )

            text = data.get("text")
            if text is None or not isinstance(text, str):
                return web.json_response(
                    {"error": "Field 'text' must be a string"},
                    status=400,
                )

            todo_id = str(next_id)
            todo_list[todo_id] = text
            next_id += 1

            return web.json_response(todo_list)

        return web.json_response(
            {"error": "Method not allowed"},
            status=405,
        )

    # /todos/{todo_id}
    if path.startswith("/todos/"):
        todo_id = path[len("/todos/") :]

        if method == "PUT":
            if todo_id not in todo_list:
                return web.json_response(
                    {"error": f"Todo '{todo_id}' not found"},
                    status=404,
                )

            try:
                data = await request.json()
            except Exception:
                return web.json_response(
                    {"error": "Invalid JSON body"},
                    status=400,
                )

            text = data.get("text")
            if text is None or not isinstance(text, str):
                return web.json_response(
                    {"error": "Field 'text' must be a non-empty string"},
                    status=400,
                )

            todo_list[todo_id] = text
            return web.json_response(todo_list)

        if method == "DELETE":
            if todo_id not in todo_list:
                return web.json_response(
                    {"error": f"Todo '{todo_id}' not found"},
                    status=404,
                )

            del todo_list[todo_id]
            return web.json_response(todo_list)

        return web.json_response(
            {"error": "Method not allowed"},
            status=405,
        )

    # Fallback: 404
    return web.json_response(
        {"error": "Not found"},
        status=404,
    )


async def main():
    # создаем HTTP‑сервер и задаем обработчик запросов, handle_request - единый обработчик всех запросов
    server = web.Server(handle_request)
    # оборачиваем сервер в объект ServerRunner, который управляет жизненным циклом сервера
    runner = web.ServerRunner(server)
    await runner.setup()
    # настраиваем прослушку по 8080 порту
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("Serving on http://0.0.0.0:8080")
    # бесконечная работа корутины main, чтобы сервер жил
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
