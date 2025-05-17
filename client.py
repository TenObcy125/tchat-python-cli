import socket
import threading
import sys

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket()
        self.running = True
        self.prompt = "\nYou: "
        self.lock = threading.Lock()

    def display_message(self, message):
        with self.lock:

            print(f"\n{message}", end='')
            # Reprint the prompt
            sys.stdout.write(self.prompt)
            sys.stdout.flush()

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    self.display_message("\033[91mConnection lost with server\033[0m")
                    self.running = False
                    break
                self.display_message(message)
            except Exception as e:
                print(f"\n\033[91mError receiving messages: {e}\033[0m")
                self.running = False
                break

    def run(self):
        nickname = input("Enter your nickname: ")
        try:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(nickname.encode())
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            print("\nConnected to chat! Type your messages (type '/help' for commands)")
            
            while self.running:
                try:
                    message = input(self.prompt)
                    if message.lower() == 'exit':
                        self.running = False
                        break
                    try:
                        self.client_socket.send(message.encode())
                    except Exception as e:
                        print(f"\n\033[91mFailed to send message: {e}\033[0m")
                        break
                except KeyboardInterrupt:
                    self.running = False
                    break
                except EOFError:
                    self.running = False
                    break
            
            self.client_socket.close()
            print("\nDisconnected from chat")
        except ConnectionRefusedError:
            print("\033[91mCould not connect to server\033[0m")
        except Exception as e:
            print(f"\033[91mError: {e}\033[0m")