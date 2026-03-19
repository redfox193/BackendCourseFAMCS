import json
from typing import Dict, Any, Callable, Awaitable

import uvicorn

Scope = Dict[str, Any]
Message = Dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class App:
    def __init__(self) -> None:
        self.todo_list = {}
        self.next_id = 0

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope['type'] == 'http'

        method = scope['method']
        path = scope['path']

        # routing
        if method == 'GET' and path == '/':
            resp = self.root()
        elif path == '/todos':
            if method == 'GET':
                resp = self.list_todos()
            elif method == 'POST':
                resp = await self.add_todo(receive)
            else:
                resp = self.json_response(
                    {'error': 'Method not allowed'},
                    status=405,
                )
        elif path.startswith('/todos/'):
            todo_id = path[len('/todos/') :]
            if method == 'PUT':
                resp = await self.edit_todo(todo_id, receive)
            elif method == 'DELETE':
                resp = self.remove_todo(todo_id)
            else:
                resp = self.json_response(
                    {'error': 'Method not allowed'},
                    status=405,
                )
        else:
            resp = self.json_response(
                {'error': 'Not found'},
                status=404,
            )

        await send(
            {
                'type': 'http.response.start',
                'status': resp['status'],
                'headers': resp['headers'],
            }
        )
        await send(
            {
                'type': 'http.response.body',
                'body': resp['body'],
            }
        )

    # -------- helpers --------

    @staticmethod
    async def read_body(receive: Receive) -> bytes:
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            assert message['type'] == 'http.request'
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body

    @staticmethod
    def json_response(
        data: Any,
        status: int = 200,
    ):
        body_bytes = json.dumps(data).encode('utf-8')
        return {
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'content-length', str(len(body_bytes)).encode('utf-8')],
            ],
            'body': body_bytes,
        }

    @staticmethod
    def html_response(html: str, status: int = 200) -> Dict[str, Any]:
        body_bytes = html.encode('utf-8')
        return {
            'status': status,
            'headers': [
                [b'content-type', b'text/html; charset=utf-8'],
                [b'content-length', str(len(body_bytes)).encode('utf-8')],
            ],
            'body': body_bytes,
        }

    # -------- handlers --------

    def root(self):
        html = '''
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
        '''
        return self.html_response(html)

    def list_todos(self):
        return self.json_response(self.todo_list)

    async def add_todo(self, receive: Receive):
        try:
            body = await self.read_body(receive)
            data = json.loads(body.decode('utf-8') or '{}')
        except Exception:
            return self.json_response(
                {'error': 'Invalid JSON body'},
                status=400,
            )

        text = data.get('text')
        if text is None or not isinstance(text, str):
            return self.json_response(
                {'error': 'Field "text" must be a string'},
                status=400,
            )

        todo_id = str(self.next_id)
        self.todo_list[todo_id] = text
        self.next_id += 1

        return self.json_response(self.todo_list)

    async def edit_todo(self, todo_id: str, receive: Receive):
        if todo_id not in self.todo_list:
            return self.json_response(
                {'error': f'Todo "{todo_id}" not found'},
                status=404,
            )

        try:
            body = await self.read_body(receive)
            data = json.loads(body.decode('utf-8') or '{}')
        except Exception:
            return self.json_response(
                {'error': 'Invalid JSON body'},
                status=400,
            )

        text = data.get('text')
        if text is None or not isinstance(text, str):
            return self.json_response(
                {'error': 'Field "text" must be a non-empty string'},
                status=400,
            )

        self.todo_list[todo_id] = text
        return self.json_response(self.todo_list)

    def remove_todo(self, todo_id: str):
        if todo_id not in self.todo_list:
            return self.json_response(
                {'error': f'Todo "{todo_id}" not found'},
                status=404,
            )

        del self.todo_list[todo_id]
        return self.json_response(self.todo_list)


app = App()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)