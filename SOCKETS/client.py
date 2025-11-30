import socket

HOST = '127.0.0.1'
PORT = 9999


def send_formula(formula: str, host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(formula.encode('utf-8'))
        data = s.recv(1024)
        return data.decode('utf-8')


def main():
    formula = input('Enter formula: ').strip()
    if not formula:
        print('No formula provided')
        return
    try:
        result = send_formula(formula)
        print('Result:', result)
    except ConnectionRefusedError:
        print('ERROR: could not connect to server at', f"{HOST}:{PORT}")
    except Exception as e:
        print('ERROR:', e)


if __name__ == '__main__':
    main()

