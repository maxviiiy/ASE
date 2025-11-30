import socket
import os
import re

HOST = '127.0.0.1'
PORT = 7777


def get_txt_files():
    return [f for f in os.listdir('./') if f.endswith('.txt')]


def main():
    word = input('Word to search (will be sent to each client): ').strip()
    files = get_txt_files()
    print(f'Found {len(files)} .txt files; will assign one file per client.')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Dispatch server listening on {HOST}:{PORT}')

    idx = 0
    while idx < len(files):
        client_socket, addr = server_socket.accept()
        print(f'Client connected from {addr}, assigning file {files[idx]}')

        with open(files[idx], 'rb') as fh:
            content_bytes = fh.read()
        header = f"{files[idx]}|{word}|{len(content_bytes)}\n"
        client_socket.sendall(header.encode('utf-8'))
        client_socket.sendall(content_bytes)

        data = client_socket.recv(4096).decode('utf-8')
        print(f'Result from {addr}: {data}')

        client_socket.close()
        idx += 1

    print('All files assigned and processed. Shutting down server.')
    server_socket.close()


if __name__ == '__main__':
    main()
