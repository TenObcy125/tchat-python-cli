import socket
import argparse
import questionary
from server import Server
from client import Client
from http_server import TChatHTTPServer
from commands.password import PasswordMiddleware

def get_local_ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def start_menu():
    return questionary.select(
        "Choose mode:",
        choices=["Server", "Client", "Exit"]
    ).ask()

def server_submenu():
    return questionary.select(
        "Server menu:",
        choices=["Run chat server", "Run HTTP API", "Settings", "Back"]
    ).ask()

def server_settings_menu():
    return questionary.select(
        "Settings menu:",
        choices=["Password options", "Back"]
    ).ask()

def password_options_menu():
    return questionary.select(
        "Password options:",
        choices=["Set new password", "Remove password", "Back"]
    ).ask()

def main():
    parser = argparse.ArgumentParser(description='TChat CLI')
    subparsers = parser.add_subparsers(dest='command', help='Show commands')
    subparsers.add_parser('start', help='Starting TChat')
    args = parser.parse_args()

    host_ip = get_local_ipv4()
    print(f"[INFO] Server will bind to local IPv4: {host_ip}")

    http_server = TChatHTTPServer(host=host_ip, port=5002)
    password_middleware = PasswordMiddleware()

    if args.command == 'start':
        print('Welcome to TChat – a Terminal-based chat for all developer geeks.\n')

        while True:
            selected = start_menu()
            if selected == "Exit" or selected is None:
                print("Exiting.")
                break

            elif selected == "Server":
                while True:
                    submenu_selected = server_submenu()

                    if submenu_selected == "Run chat server":
                        if not http_server.thread or not http_server.thread.is_alive():
                            http_server.start()
                            print(f"[INFO] HTTP Server started on {host_ip}:5002")
                        else:
                            print("[INFO] HTTP Server already running.")

                        server = Server()
                        server.run()

                    elif submenu_selected == "Run HTTP API":
                        if not http_server.thread or not http_server.thread.is_alive():
                            http_server.start()
                            print(f"[INFO] HTTP API Server started on {host_ip}:5002")
                        else:
                            print("[INFO] HTTP API Server already running.")

                    elif submenu_selected == "Settings":
                        while True:
                            settings_selected = server_settings_menu()
                            if settings_selected == "Password options":
                                while True:
                                    password_selected = password_options_menu()
                                    if password_selected == "Set new password":
                                        password = questionary.password("Enter new password:").ask()
                                        if password:
                                            password_middleware.set_password(password)
                                            print("\033[92mPassword set successfully!\033[0m")
                                        else:
                                            print("\033[91mPassword cannot be empty!\033[0m")
                                    elif password_selected == "Remove password":
                                        password_middleware.set_password("")
                                        print("\033[92mPassword removed successfully!\033[0m")
                                    elif password_selected == "Back":
                                        break
                            elif settings_selected == "Back" or settings_selected is None:
                                break

                    elif submenu_selected == "Back" or submenu_selected is None:
                        break

            elif selected == "Client":
                print(f"Connect to server IP (detected automatically): {host_ip}")
                host = input(f"Enter server IP [{host_ip}]: ").strip()
                if not host:
                    host = host_ip
                client = Client(host, 5001)
                client.run()

if __name__ == "__main__":
    main()