import socket
import os
import threading


HOST = '127.0.0.1'
PORT = 9002
FILES_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_client(conn, addr):
    print(f'Connected to Service Server at {addr}')
    with conn:
        filename = conn.recv(1024).decode('utf-8')
        print(f'Requested file: {filename}')
        filepath = os.path.join(FILES_DIR, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            conn.sendall(content.encode('utf-8'))
        else:
            conn.sendall(b'')
    print(f'Connection closed {addr}')

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f'File Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
if __name__ == '__main__':
    start_server()

