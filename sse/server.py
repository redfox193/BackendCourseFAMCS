import json
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer


class SSEHandler(BaseHTTPRequestHandler):
    def setup(self) -> None:
        super().setup()
        self.wfile = self.connection.makefile('wb', buffering=200)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self) -> None:
        if self.path != '/events':
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        event_id = 0
        while True:
            price = round(random.uniform(90, 110), 2)
            payload = json.dumps({'usd': price})

            line = f'id: {event_id}\nevent: price\ndata: {payload}\n\n'
            self.wfile.write(line.encode())
            self.wfile.flush()

            event_id += 1
            time.sleep(0.5)

    def log_message(self, format, *args) -> None:
        pass


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), SSEHandler)
    print('Raw SSE server on http://127.0.0.1:8000/events')
    server.serve_forever()
