from aiohttp import web

todo_list = {}
next_id = 0


async def add_todo(request):
    global todo_list, next_id
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


async def list_todos(request):
    global todo_list
    return web.json_response(todo_list)


async def edit_todo(request):
    global todo_list
    todo_id = request.match_info.get("todo_id")

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


async def remove_todo(request):
    global todo_list
    todo_id = request.match_info.get("todo_id")

    if todo_id not in todo_list:
        return web.json_response(
            {"error": f"Todo '{todo_id}' not found"},
            status=404,
        )

    del todo_list[todo_id]
    return web.json_response(todo_list)


async def root(request):
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


app = web.Application()
app.add_routes([
    web.get("/", root),
    web.get("/todos", list_todos),
    web.post("/todos", add_todo),
    web.put("/todos/{todo_id}", edit_todo),
    web.delete("/todos/{todo_id}", remove_todo),
])

if __name__ == '__main__':
    web.run_app(app)
