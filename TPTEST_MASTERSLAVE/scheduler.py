import socket
import threading
import random
import datetime
import os

# Scheduler (Master) for TPTEST_MASTERSLAVE
#
# Short guide to modify this file:
# - Change `HOST`/`PORT` to bind scheduler to a different address.
# - Edit `ROUTING_TABLE` to map filenames to the slave IP/port that serve them.
# - Edit `WORD_POOL` to change which random words the scheduler can assign.
# - `HISTORY_FILE` is where the scheduler appends results; change path if needed.

HOST = '127.0.0.1'   # scheduler bind address
PORT = 8080          # scheduler port
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'history.txt')

# ROUTING_TABLE maps filename -> (server_ip, server_port)
# Modify this mapping to reflect where your slaves run and which files they host.
ROUTING_TABLE = {
    'A.txt': ('127.0.0.1', 9000),
    'B.txt': ('127.0.0.1', 9000),
    'C.txt': ('127.0.0.1', 9001),
    'D.txt': ('127.0.0.1', 9001),
    'E.txt': ('127.0.0.1', 9001),
    'F.txt': ('127.0.0.1', 9002),
}

# Words the scheduler can choose from when assigning a search word.
WORD_POOL = ['AI', 'animal', 'vacation', 'dog', 'dogs', 'star', 'stars', 'recipe', 'step', 'again', 'music', 'travel', 'can', 'and']

# simple lock to protect writes to the history file from multiple threads
LOCK = threading.Lock()


def send_msg(conn, msg):
    """Send a newline-terminated text message over `conn`.

    The protocol between scheduler and client is line-based; messages
    are ASCII/UTF-8 text ending with a single '\n'.
    """
    conn.sendall((msg + '\n').encode('utf-8'))


def recv_msg(conn):
    """Receive a single newline-terminated message from `conn`.

    This reads until the first '\n' and returns the line without the '\n'.
    """
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
    """Append a single-line log entry to `HISTORY_FILE`.

    Format: [timestamp] client=IP file=... server=IP:port word="..." occurrences=N
    """
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] client={client_ip} file={filename} server={server_addr[0]}:{server_addr[1]} word="{word}" occurrences={occurrences}\n'
    with LOCK:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    print('Logged:', line.strip())


def handle_client(conn, addr):
    """Handle a scheduler <-> client session.

    Protocol (text lines):
      - Scheduler -> client: FILES:fname1|fname2|...
      - Client -> scheduler: CHOICE:filename or CHOICE:filename:word
      - Scheduler -> client: ASSIGN:server_ip:server_port:word
      - Client -> scheduler: RESULT:filename:count

    This function is simple and intentionally small. If you want to accept
    the RESULT on a new connection (instead of the same one), modify this
    function to remember assignments elsewhere (e.g., a dict) and accept
    RESULT messages in `run()` when they arrive on fresh sockets.
    """
    print('Client connected from', addr)

    # Send list of available files
    files = '|'.join(sorted(ROUTING_TABLE.keys()))
    send_msg(conn, f'FILES:{files}')

    # Receive the client's choice (optionally with a preferred word)
    msg = recv_msg(conn)
    if not msg:
        conn.close()
        return
    if not msg.startswith('CHOICE:'):
        send_msg(conn, 'ERROR:BAD_REQUEST')
        conn.close()
        return
    parts = msg.split(':')
    if len(parts) < 2:
        send_msg(conn, 'ERROR:BAD_REQUEST')
        conn.close()
        return
    filename = parts[1]
    client_word = parts[2] if len(parts) >= 3 else None
    if filename not in ROUTING_TABLE:
        send_msg(conn, 'ERROR:UNKNOWN_FILE')
        conn.close()
        return

    server_ip, server_port = ROUTING_TABLE[filename]

    # Choose word if client didn't provide one
    word = client_word if client_word else random.choice(WORD_POOL)

    # Tell the client which server to contact and which word to search for
    send_msg(conn, f'ASSIGN:{server_ip}:{server_port}:{word}')

    # Expect the RESULT on the same connection
    res = recv_msg(conn)
    if not res:
        conn.close()
        return
    if res.startswith('RESULT:'):
        rparts = res.split(':')
        if len(rparts) >= 3:
            fn = rparts[1]
            count = int(rparts[2])
            log_history(addr[0], fn, (server_ip, server_port), word, count)
            send_msg(conn, 'OK')
            conn.close()
            return

    send_msg(conn, 'ERROR:BAD_RESULT')
    conn.close()


def run():
    """Start the scheduler socket and accept client connections.

    This loop spawns a thread per client. For a production system you might
    prefer a thread pool or async IO.
    """
    print('Scheduler starting on', HOST, PORT)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    open(HISTORY_FILE, 'a', encoding='utf-8').close()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)  # backlog; increase if you expect many simultaneous connect attempts
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == '__main__':
    run()

