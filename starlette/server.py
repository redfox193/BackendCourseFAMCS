from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route


todo_list = {}
next_id = 0


async def add_todo(request: Request):
    global todo_list, next_id
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    text = data.get("text")
    if text is None or not isinstance(text, str):
        return JSONResponse(
            {"error": "Field 'text' must be a string"},
            status_code=400,
        )

    todo_id = str(next_id)
    todo_list[todo_id] = text
    next_id += 1

    return JSONResponse(todo_list)


async def list_todos(request: Request):
    global todo_list
    return JSONResponse(todo_list)


async def edit_todo(request: Request):
    global todo_list
    todo_id = request.path_params.get("todo_id")

    if todo_id not in todo_list:
        return JSONResponse(
            {"error": f"Todo '{todo_id}' not found"},
            status_code=404,
        )

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    text = data.get("text")
    if text is None or not isinstance(text, str):
        return JSONResponse(
            {"error": "Field 'text' must be a non-empty string"},
            status_code=400,
        )

    todo_list[todo_id] = text
    return JSONResponse(todo_list)


async def remove_todo(request: Request):
    global todo_list
    todo_id = request.path_params.get("todo_id")

    if todo_id not in todo_list:
        return JSONResponse(
            {"error": f"Todo '{todo_id}' not found"},
            status_code=404,
        )

    del todo_list[todo_id]
    return JSONResponse(todo_list)


async def root(request: Request):
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
    return HTMLResponse(html)


routes = [
    Route("/", root, methods=["GET"]),
    Route("/todos", list_todos, methods=["GET"]),
    Route("/todos", add_todo, methods=["POST"]),
    Route("/todos/{todo_id}", edit_todo, methods=["PUT"]),
    Route("/todos/{todo_id}", remove_todo, methods=["DELETE"]),
]

app = Starlette(routes=routes)
