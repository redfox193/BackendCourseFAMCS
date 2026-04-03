import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx

CHAT_SERVER = 'http://127.0.0.1:8000'
BOT_NAME = 'echo_bot'
BOT_HOST = '127.0.0.1'
BOT_PORT = 8001


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != '/incoming':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers['Content-Length'])
        msg = json.loads(self.rfile.read(length))

        if msg['author'] != BOT_NAME:
            print(f'[{BOT_NAME}] got: "{msg['text']}" from {msg['author']}')
            httpx.post(
                f'{CHAT_SERVER}/message',
                json={'author': BOT_NAME, 'text': msg['text']},
            )

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')


def main() -> None:
    httpx.post(
        f'{CHAT_SERVER}/webhook/register',
        json={'url': f'http://{BOT_HOST}:{BOT_PORT}/incoming'},
    )
    print(f'[{BOT_NAME}] registered, listening on {BOT_HOST}:{BOT_PORT}...')

    server = HTTPServer((BOT_HOST, BOT_PORT), WebhookHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
