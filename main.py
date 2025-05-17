import argparse
import questionary
from server import Server
from client import Client

def start_menu():
    choice = questionary.select(
        "Choose mode:",
        choices=["Server", "Client"]
    ).ask()

    if choice is None:
        print("No option selected, exiting.")
        exit(0)

    return choice

def main():
    parser = argparse.ArgumentParser(description='TChat CLI')

    subparsers = parser.add_subparsers(dest='command', help='Show commands')

    start_parser = subparsers.add_parser('start', help='Starting TChat')

    args = parser.parse_args()

    if args.command == 'start':
        print('Welcome to TChat – a Terminal-based chat for all developer geeks.\n')
        selected = start_menu()
        
        if selected == "Server":
            server = Server()
            server.run()
        elif selected == "Client":
            host = input("Enter server IP: ")
            client = Client(host, 5001)
            client.run()

if __name__ == "__main__":
    main()