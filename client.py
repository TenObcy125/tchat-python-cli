import socket
import threading
import queue
import sys
import select
import requests

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket()
        self.running = True
        self.input_queue = queue.Queue()

    def display(self, msg):

        print("\r" + " " * 100 + "\r" + msg)

    def upload_file(self, filename):
        url = f"http://{self.host}:5002/upload"
        with open(filename, 'rb') as f:
            files = {
                'file': (filename, f)
            }
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response.json()["file_url"]

    def handle_todo_command(self, command):
        try:
            self.client_socket.send(command.encode())
            
            if command == '/todo-add':
                response = self.client_socket.recv(1024).decode()
                if response == "TITLE_PROMPT":
                    title = input("> Task Title: ")
                    self.client_socket.send(f"/todo-add {title}".encode())
                    response = self.client_socket.recv(1024).decode()
                self.display(response)
            else:
                response = self.client_socket.recv(1024).decode()
                self.display(response)
        except Exception as e:
            self.display(f"\033[91mTODO error: {e}\033[0m")

    def receive_messages(self):
        while self.running:
            try:
                ready, _, _ = select.select([self.client_socket], [], [], 0.1)
                if ready:
                    message = self.client_socket.recv(1024).decode()
                    if not message:
                        self.running = False
                        break

                    if message != "TITLE_PROMPT":
                        self.display(message)
            except:
                self.running = False
                break

    def run(self):
        nickname = input("Enter your nickname: ")

        try:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(nickname.encode())

            threading.Thread(target=self.receive_messages, daemon=True).start()

            print("\nConnected to chat! Type your messages (type '/help' for commands)")

            while self.running:
                user_input = input("You: ")

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    self.running = False
                    break

                if user_input.startswith('/todo'):
                    self.handle_todo_command(user_input)
                    continue

                if user_input.startswith('/upload'):
                    file_path = input('Enter file path: ')
                    try:
                        response = self.upload_file(file_path)
                        self.client_socket.send(response.encode())
                        self.display(f"File uploaded successfully: {response}")
                    except Exception as e:
                        self.display(f"\033[91mUpload failed: {e}\033[0m")
                    continue

                self.client_socket.send(user_input.encode())

            self.client_socket.close()
            print("\nDisconnected from chat.")

        except Exception as e:
            print(f"\033[91mConnection error: {e}\033[0m")
