import socket
import os
import json

HOST = 'localhost'
PORT = 9001
FILE_SERVER_HOST = 'localhost'
FILE_SERVER_PORT = 9000

def request_file_from_file_server(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fs_sock:
        fs_sock.connect((FILE_SERVER_HOST, FILE_SERVER_PORT))
        fs_sock.sendall(filename.encode('utf-8'))
       
        chunks = []
        while True:
            data = fs_sock.recv(4096)
            if not data:
                break
            chunks.append(data)
        file_content = b''.join(chunks).decode('utf-8')
        return file_content

def count_word_occurrences(content, word):
    words = content.lower().split()
    return words.count(word.lower())

def handle_client(conn, addr):
    print(f'Client connected: {addr}')
    with conn:
        files = ["A.txt", "B.txt", "C.txt"]

        files_json = json.dumps(files)
        conn.sendall(files_json.encode('utf-8'))

        selection_str = conn.recv(1024).decode('utf-8')
        selection = json.loads(selection_str)
        filename = selection.get('file')
        word = selection.get('word')
        print(f'Received from client: file={filename}, word={word}')

        file_content = request_file_from_file_server(filename)

        if file_content == '':
            count = -1
        else:
            count = count_word_occurrences(file_content, word)

        conn.sendall(str(count).encode('utf-8'))
    print(f'Connection closed: {addr}')

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
        serv_sock.bind((HOST, PORT))
        serv_sock.listen(5)
        print(f'Service Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = serv_sock.accept()
            handle_client(conn, addr)

if __name__ == '__main__':
    start_server()
