import socket
import threading
import os
import argparse

HOST = '127.0.0.1'


def send_msg(conn, msg):
    conn.sendall((msg + '\n').encode())


def recv_msg(conn):
    buf = b''
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            break
        buf += chunk
        if b'\n' in buf:
            line, _, rest = buf.partition(b'\n')
            return line.decode().strip()
    if buf:
        return buf.decode().strip()
    return ''


def handle_client(conn, addr, files_dir):
    try:
        print('Client connected to slave from', addr)
        msg = recv_msg(conn)
        # Expect: GET:filename
        if not msg or not msg.startswith('GET:'):
            send_msg(conn, 'ERROR:BAD_REQUEST')
            return
        filename = msg.split(':', 1)[1]
        file_path = os.path.join(files_dir, filename)
        if not os.path.isfile(file_path):
            send_msg(conn, 'ERROR:NOTFOUND')
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Send content prefixed
        send_msg(conn, 'CONTENT:' + content)
    except Exception as e:
        print('Slave error:', e)
    finally:
        try:
            conn.close()
        except:
            pass


def run(port, files_dir):
    os.makedirs(files_dir, exist_ok=True)
    print('Slave serving', files_dir, 'on port', port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr, files_dir), daemon=True)
            t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=6001)
    parser.add_argument('--files', type=str, default='files')
    args = parser.parse_args()
    run(args.port, args.files)
