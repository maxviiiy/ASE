import socket
import re

SCHED_HOST = '127.0.0.1'
SCHED_PORT = 8080


def send_msg(conn, msg):
	conn.sendall((msg + '\n').encode('utf-8'))


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


def receive_all(conn):
	parts = []
	while True:
		chunk = conn.recv(4096)
		if not chunk:
			break
		parts.append(chunk)
	return b''.join(parts).decode('utf-8', errors='ignore')


def main():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((SCHED_HOST, SCHED_PORT))

		# receive file list
		msg = recv_msg(s)
		if not msg or not msg.startswith('FILES:'):
			print('Bad response from scheduler:', msg)
			return
		files = msg.split(':', 1)[1].split('|')
		print('Available files:')
		for i, f in enumerate(files, 1):
			print(f'  {i}. {f}')

		choice = input('Choose a file name (exact): ').strip()
		word_override = input('Optional: provide a word to search (or press Enter): ').strip()
		if word_override:
			send_msg(s, f'CHOICE:{choice}:{word_override}')
		else:
			send_msg(s, f'CHOICE:{choice}')

		assign = recv_msg(s)
		if not assign:
			print('No response from scheduler')
			return
		if assign.startswith('ERROR:'):
			print('Scheduler error:', assign)
			return
		if not assign.startswith('ASSIGN:'):
			print('Bad assign:', assign)
			return

		parts = assign.split(':')
		# ASSIGN:ip:port:word
		if len(parts) < 4:
			print('Malformed ASSIGN:', assign)
			return
		server_ip = parts[1]
		server_port = int(parts[2])
		word = ':'.join(parts[3:])
		print('Assigned server', server_ip, server_port, 'search word:', word)

		# Connect to the slave server (raw protocol) while keeping scheduler socket open
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
			s2.connect((server_ip, server_port))
			# send filename (raw bytes)
			s2.sendall(choice.encode('utf-8'))
			# receive entire content until server closes
			content = receive_all(s2)

		if not content:
			print('Slave returned no content (file may be missing)')
			count = 0
		else:
			# Count whole-word occurrences (case-insensitive)
			pattern = r"\b" + re.escape(word) + r"\b"
			matches = re.findall(pattern, content, flags=re.IGNORECASE)
			count = len(matches)
			print(f'Found {count} occurrences of "{word}" in {choice}')

		# Send result back to scheduler on the same connection
		send_msg(s, f'RESULT:{choice}:{count}')
		final = recv_msg(s)
		print('Scheduler reply:', final)

	# (logic moved inside the main scheduler connection so result is sent on same socket)


if __name__ == '__main__':
	main()

