import socket
import threading
from typing import Dict
import json
import random
from commands.todo_menager import TODO

class Server:
    COLORS = [
        '\033[31m', '\033[32m', '\033[33m', '\033[34m',
        '\033[35m', '\033[36m', '\033[91m', '\033[92m',
        '\033[93m', '\033[94m', '\033[95m', '\033[96m',
        '\033[37m', '\033[90m', '\033[1;31m', '\033[1;32m'
    ]

    def __init__(self):
        self.clients: Dict[socket.socket, Dict[str, str]] = {}
        self.host = socket.gethostname()
        self.port = 5001
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        self.host_client = None
        self.todo = TODO()
        self.todo_waiting = {}

    def assign_color(self):
        return random.choice(self.COLORS)

    def broadcast(self, message: str, sender_socket: socket.socket = None):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode())
                except:
                    self.remove_client(client)

    def remove_client(self, client_socket: socket.socket):
        if client_socket in self.clients:
            nickname = self.clients[client_socket]['nickname']
            color = self.clients[client_socket]['color']
            del self.clients[client_socket]
            leave_msg = f"{color}[{nickname}]\033[0m has left the chat."
            self.broadcast(leave_msg)
            print(leave_msg)
            if client_socket == self.host_client:
                self.shutdown()

    def handle_client(self, client_socket: socket.socket, address: tuple):
        nickname = client_socket.recv(1024).decode()
        color = self.assign_color()

        if not self.host_client:
            self.host_client = client_socket

        self.clients[client_socket] = {
            'nickname': nickname,
            'color': color,
            'address': address
        }

        welcome_msg = f"{color}[{nickname}]\033[0m has joined the chat."
        print(welcome_msg)
        self.broadcast(welcome_msg, client_socket)

        try:
            while self.running:
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                # Check if we're expecting task title from this client
                if client_socket in self.todo_waiting:
                    title = message.strip()
                    if title:
                        response = self.todo.add_task(title, nickname)
                        client_socket.send(f"✅ {response}".encode())
                    else:
                        client_socket.send("❌ Title cannot be empty.".encode())
                    del self.todo_waiting[client_socket]
                    continue

                if message.startswith('/todo'):
                    if message.strip() == '/todo':
                        response = self.todo.render()
                        client_socket.send(response.encode())
                        continue

                    elif message.strip() == '/todo-add':
                        self.todo_waiting[client_socket] = True
                        client_socket.send("Enter the task title:".encode())
                        continue

                    elif message.startswith('/todo-add '):
                        title = message[10:].strip()
                        if title:
                            response = self.todo.add_task(title, nickname)
                            client_socket.send(f"✅ {response}".encode())
                        else:
                            client_socket.send("❌ Task title cannot be empty.".encode())
                        continue

                    elif message.startswith('/todo-set '):
                        try:
                            parts = message.strip().split()
                            if len(parts) != 3:
                                raise ValueError("Invalid format.")
                            task_num = int(parts[1])
                            complete = parts[2].lower() == 'true'
                            response = self.todo.set_completion(task_num, complete)
                            client_socket.send(f"✅ {response}".encode())
                        except ValueError:
                            client_socket.send("❌ Usage: /todo-set [number] [true/false]".encode())
                        continue

                    else:
                        client_socket.send("❌ Unknown TODO command.".encode())
                        continue

                if message.startswith('/'):
                    if client_socket == self.host_client:
                        if message.lower() == '/exit':
                            self.shutdown()
                            break
                        elif message.lower() == '/users':
                            users_list = "Connected users:\n"
                            for client in self.clients.values():
                                users_list += f"- {client['nickname']}\n"
                            client_socket.send(users_list.encode())
                            continue

                formatted_msg = f"{color}[{nickname}]\033[0m: {message}"
                print(formatted_msg)
                self.broadcast(formatted_msg, client_socket)
        except:
            pass

        self.remove_client(client_socket)
        client_socket.close()

    def shutdown(self):
        self.running = False
        shutdown_msg = "\033[91mServer is shutting down...\033[0m"
        print(shutdown_msg)
        for client in list(self.clients.keys()):
            try:
                client.send(shutdown_msg.encode())
                client.close()
            except:
                pass
        self.server_socket.close()

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        print("Waiting for connections...")

        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            self.shutdown()
        except:
            self.shutdown()
