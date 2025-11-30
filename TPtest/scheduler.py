import socket
import threading
import random
import datetime
import os

HOST = '127.0.0.1'
PORT = 7000
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'history.txt')

# Simple routing table: map filename -> (ip, port)
ROUTING_TABLE = {
    'data-01.txt': ('127.0.0.1', 6001),
    'data-02.txt': ('127.0.0.1', 6002),
}

WORD_POOL = ['python', 'network', 'socket', 'AI', 'distributed']


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


def log_history(client_ip, filename, server_addr, word, occurrences):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] client={client_ip} file={filename} server={server_addr[0]}:{server_addr[1]} word="{word}" occurrences={occurrences}\n'
    with threading.Lock():
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    print('Logged:', line.strip())


def handle_client(conn, addr):
    try:
        print('Client connected from', addr)
        # Send list of files
        files = '|'.join(sorted(ROUTING_TABLE.keys()))
        send_msg(conn, f'FILES:{files}')

        # Receive choice
        msg = recv_msg(conn)
        if not msg:
            return
        # Expect: CHOICE:filename
        if not msg.startswith('CHOICE:'):
            send_msg(conn, 'ERROR:BAD_REQUEST')
            return
        filename = msg.split(':', 1)[1]
        if filename not in ROUTING_TABLE:
            send_msg(conn, 'ERROR:UNKNOWN_FILE')
            return

        # Choose a word (random) and send assignment
        word = random.choice(WORD_POOL)
        server_ip, server_port = ROUTING_TABLE[filename]
        send_msg(conn, f'ASSIGN:{server_ip}:{server_port}:{word}')

        # Wait for result
        res = recv_msg(conn)
        if not res:
            return
        # Expect: RESULT:filename:count
        if res.startswith('RESULT:'):
            parts = res.split(':')
            if len(parts) >= 3:
                fn = parts[1]
                count = parts[2]
                log_history(addr[0], fn, (server_ip, server_port), word, count)
                send_msg(conn, 'OK')
                return
        send_msg(conn, 'ERROR:BAD_RESULT')
    except Exception as e:
        print('Error handling client', addr, e)
    finally:
        try:
            conn.close()
        except:
            pass


def run():
    print('Scheduler starting on', HOST, PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == '__main__':
    # Ensure history file exists
    open(HISTORY_FILE, 'a', encoding='utf-8').close()
    run()
