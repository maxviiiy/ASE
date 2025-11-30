import socket
import sys

SCHED_HOST = '127.0.0.1'
SCHED_PORT = 7000


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


def main():
    # Connect to scheduler
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SCHED_HOST, SCHED_PORT))
        # Receive file list
        msg = recv_msg(s)
        if not msg.startswith('FILES:'):
            print('Bad response from scheduler:', msg)
            return
        files = msg.split(':', 1)[1].split('|')
        print('Available files:')
        for i, f in enumerate(files, 1):
            print(f'  {i}. {f}')
        choice = input('Choose a file name (exact): ').strip()
        send_msg(s, f'CHOICE:{choice}')

        # Receive assignment
        assign = recv_msg(s)
        if assign.startswith('ERROR:'):
            print('Scheduler error:', assign)
            return
        # ASSIGN:ip:port:word
        if not assign.startswith('ASSIGN:'):
            print('Bad assign:', assign)
            return
        _, rest = assign.split(':', 1)
        parts = assign.split(':')
        server_ip = parts[1]
        server_port = int(parts[2])
        word = parts[3]
        print('Assigned server', server_ip, server_port, 'search word:', word)

        # Connect to slave server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            s2.connect((server_ip, server_port))
            send_msg(s2, f'GET:{choice}')
            resp = recv_msg(s2)
            if resp.startswith('ERROR:'):
                print('Slave error:', resp)
                return
            if resp.startswith('CONTENT:'):
                content = resp[len('CONTENT:'):]
            else:
                print('Bad content response:', resp)
                return

        # Count occurrences (case-insensitive)
        count = content.lower().count(word.lower())
        print(f'Found {count} occurrences of "{word}" in {choice}')

        # Send result back to scheduler
        send_msg(s, f'RESULT:{choice}:{count}')
        final = recv_msg(s)
        print('Scheduler reply:', final)


if __name__ == '__main__':
    main()
