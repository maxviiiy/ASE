import socket
import json
import sys

HOST = '127.0.0.1'
PORT = 65432


def send_request(a, b, op):
    req = json.dumps({'a': a, 'b': b, 'op': op})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(req.encode())
        data = s.recv(4096)
        if not data:
            print('No response from server')
            return
        try:
            resp = json.loads(data.decode())
        except json.JSONDecodeError:
            print('Invalid response from server')
            return
        if 'error' in resp:
            print('Error:', resp['error'])
        else:
            print('Result:', resp.get('result'))


def parse_and_send(expression_tokens):
   
    if len(expression_tokens) == 3:
        x, op, y = expression_tokens
        
        if is_number(x) and is_number(y):
            send_request(x, y, op)
            return True
    return False


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def interactive():
    print('Client interactive mode. Type expressions like: 5 + 3  OR 5 3 +')
    print("Supported ops: + - * / ^ % (or words: add sub mul div pow mod). Type 'quit' to exit.")
    while True:
        line = input('> ').strip()
        if not line:
            continue
        if line.lower() in ('quit', 'exit'):
            break
        tokens = line.split()
        if parse_and_send(tokens):
            continue
       
        if len(tokens) == 3 and is_number(tokens[0]) and is_number(tokens[1]):
            send_request(tokens[0], tokens[1], tokens[2])
            continue
        print('Could not parse expression. Examples: 5 + 3   or   5 3 +')


def main():

    if len(sys.argv) >= 4:
        a = sys.argv[1]
        op = sys.argv[2]
        b = sys.argv[3]
        send_request(a, b, op)
        return

    interactive()


if __name__ == '__main__':
    main()
