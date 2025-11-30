import socket
import re

HOST = '127.0.0.1'
PORT = 9999

FORMULA_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([+\-*/])\s*([-+]?\d+(?:\.\d+)?)\s*$")


def evaluate_formula(s: str):
	m = FORMULA_RE.match(s)
	if not m:
		return "ERROR: invalid formula. Use like: 12 + 2"
	a_str, op, b_str = m.group(1), m.group(2), m.group(3)
	try:
		a = float(a_str)
		b = float(b_str)
	except ValueError:
		return "ERROR: invalid number"

	try:
		if op == '+':
			res = a + b
		elif op == '-':
			res = a - b
		elif op == '*':
			res = a * b
		elif op == '/':
			if b == 0:
				return "ERROR: division by zero"
			res = a / b
		else:
			return "ERROR: unsupported operator"
	except Exception as e:
		return f"ERROR: {e}"

	if res.is_integer():
		return str(int(res))
	return str(res)


def run_server(host=HOST, port=PORT):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((host, port))
		s.listen(5)
		print(f"Calculator server listening on {host}:{port}")
		while True:
			conn, addr = s.accept()
			with conn:
				print(f"Connected by {addr}")
				data = conn.recv(1024)
				if not data:
					print("No data received, closing connection")
					continue
				text = data.decode('utf-8').strip()
				print(f"Received: {text}")
				result = evaluate_formula(text)
				conn.sendall(result.encode('utf-8'))
				print(f"Sent: {result}")


if __name__ == '__main__':
	try:
		run_server()
	except KeyboardInterrupt:
		print('\nServer shutting down')

