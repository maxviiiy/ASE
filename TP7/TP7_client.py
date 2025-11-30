import socket

HOST = '127.0.0.1'
PORT = 8888


def get_user_input(file_list: str):
    print("\nAvailable text files:")
    print(file_list)
    filename = input("\nEnter the filename you want to search: ").strip()
    word = input("Enter the word to search for: ").strip()
    return filename, word


def run_client(host: str = HOST, port: int = PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}")

    file_list = client_socket.recv(4096).decode('utf-8')

    filename, word = get_user_input(file_list)

    request_data = f"{filename}|{word}"
    client_socket.sendall(request_data.encode('utf-8'))

    result = client_socket.recv(4096).decode('utf-8')
    print(f"\nResult: {result}")

    client_socket.close()
    print("Connection closed.")


run_client()
