import socket
import json

HOST = '127.0.0.1'  
PORT = 65432        


def calculate(a, b, op):
    try:
        if op == '+' or op.lower() == 'add':
            return a + b
        if op == '-' or op.lower() == 'sub':
            return a - b
        if op == '*' or op.lower() == 'mul':
            return a * b
        if op == '/' or op.lower() == 'div':
            if b == 0:
                return {'error': 'division_by_zero'}
            return a / b
        if op == '^' or op.lower() == 'pow' or op.lower() == 'powr':
            return a ** b
        if op.lower() == 'mod' or op == '%':
            if b == 0:
                return {'error': 'modulo_by_zero'}
            return a % b
        return {'error': f'unsupported_operation: {op}'}
    except Exception as e:
        return {'error': f'calculation_error: {str(e)}'}


def handle_client(conn, addr):
    with conn:
        print(f'Connected by {addr}')
        try:
            data = conn.recv(4096)
            if not data:
                return
            try:
                req = json.loads(data.decode())
            except json.JSONDecodeError:
                resp = {'error': 'invalid_json'}
                conn.sendall(json.dumps(resp).encode())
                return

          
            if not all(k in req for k in ('a', 'b', 'op')):
                resp = {'error': 'missing_fields; required: a, b, op'}
                conn.sendall(json.dumps(resp).encode())
                return

            try:
                a = float(req['a'])
                b = float(req['b'])
            except Exception:
                resp = {'error': 'invalid_number'}
                conn.sendall(json.dumps(resp).encode())
                return

            op = req['op']
            result = calculate(a, b, op)
         
            if isinstance(result, dict) and 'error' in result:
                conn.sendall(json.dumps(result).encode())
            else:
             
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                conn.sendall(json.dumps({'result': result}).encode())
        except Exception as e:
            try:
                conn.sendall(json.dumps({'error': f'server_exception: {str(e)}'}).encode())
            except Exception:
                pass


def main():
    print(f'Starting server on {HOST}:{PORT} ...')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print('Server listening. Waiting for connections...')
        try:
            while True:
                conn, addr = s.accept()
               
                handle_client(conn, addr)
        except KeyboardInterrupt:
            print('\nServer shutting down (keyboard interrupt).')


if __name__ == '__main__':
    main()
