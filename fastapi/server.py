from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

todo_list = {}
next_id = 0


class TodoCreate(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def root():
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
    return HTMLResponse(content=html, status_code=200)


@app.get("/todos")
async def list_todos():
    return todo_list


@app.post("/todos")
async def add_todo(todo: TodoCreate):
    global next_id

    todo_id = str(next_id)
    todo_list[todo_id] = todo.text
    next_id += 1

    return todo_list


@app.put("/todos/{todo_id}")
async def edit_todo(todo_id: str, todo: TodoCreate):
    if todo_id not in todo_list:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

    todo_list[todo_id] = todo.text
    return todo_list


@app.delete("/todos/{todo_id}")
async def remove_todo(todo_id: str):
    if todo_id not in todo_list:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

    del todo_list[todo_id]
    return todo_list
