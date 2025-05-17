from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import threading
import socket

class TChatHTTPServer:
    def __init__(self, host='localhost', port=5002, upload_dir='uploads'):
        self.host = host
        self.port = port
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        self.server = HTTPServer((self.host, self.port), self._make_handler())
        self.thread = None

    def _make_handler(self):
        upload_dir = self.upload_dir
        host = self.host
        port = self.port

        class CustomHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == '/upload':
                    content_length = int(self.headers['Content-Length'])
                    content_type = self.headers.get('Content-Type')

                    if not content_type.startswith('multipart/form-data'):
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'Invalid content type')
                        return

                    boundary = content_type.split('boundary=')[-1].encode()
                    body = self.rfile.read(content_length)

                    # Rozbijamy na części po boundary
                    parts = body.split(b'--' + boundary)
                    for part in parts:
                        if b'Content-Disposition' in part and b'name="file"' in part:
                            disposition_match = re.search(b'filename="([^"]+)"', part)
                            if not disposition_match:
                                continue
                            filename = disposition_match.group(1).decode()

                            file_start = part.find(b'\r\n\r\n') + 4
                            file_data = part[file_start:]
                            file_data = file_data.rstrip(b'\r\n--')

                            file_path = os.path.join(upload_dir, filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_data)

                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = (
                                f'{{"message": "File uploaded", '
                                f'"file_url": "http://{host}:{port}/uploads/{filename}"}}'
                            )
                            self.wfile.write(response.encode())
                            return

                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'No file found')

            def do_GET(self):
                if self.path.startswith('/uploads/'):
                    filepath = '.' + self.path
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.end_headers()
                        with open(filepath, 'rb') as f:
                            self.wfile.write(f.read())
                        return

                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')

        return CustomHandler

    def start(self):
        print(f"[TChatHTTPServer] Running at http://{self.host}:{self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop(self):
        print("[TChatHTTPServer] Shutting down...")
        self.server.shutdown()
        self.thread.join()
