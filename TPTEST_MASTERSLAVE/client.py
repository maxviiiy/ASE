"""Simple client for TPTEST_MASTERSLAVE with inline comments.

This client demonstrates the two-step interaction described in the
TP-ISIA spec: it talks to the scheduler to get a server+word, then
downloads the file from that slave and reports back the count.

What to change if you customize:
- `SCHED_HOST` / `SCHED_PORT`: where the scheduler is listening.
- The client currently sends the filename as raw bytes to the slave
  and reads until the slave closes the socket. Change the framing if
  you alter the slave protocol.
"""

import socket
import re

# Scheduler address (change if scheduler runs elsewhere)
SCHED_HOST = '127.0.0.1'
SCHED_PORT = 8080


def send_msg(conn, msg):
	"""Send a newline-terminated message to the scheduler.

	The scheduler expects text-lines terminated by '\n'.
	"""
	conn.sendall((msg + '\n').encode('utf-8'))


def recv_msg(conn):
	"""Receive a single newline-terminated text message from `conn`.

	This helper returns the line without the trailing newline.
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


def receive_all(conn):
	"""Read until the other side closes the connection and return decoded text.

	The slave servers in this repo simply send the full file and then
	close the socket, so this function collects all bytes until EOF.
	"""
	parts = []
	while True:
		chunk = conn.recv(4096)
		if not chunk:
			break
		parts.append(chunk)
	return b''.join(parts).decode('utf-8', errors='ignore')


def main():
	# Keep the scheduler connection open for the entire session so the
	# RESULT is sent on the same socket (the scheduler expects that).
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((SCHED_HOST, SCHED_PORT))

		size = 'S'
		send_msg(s, size)

		msg = recv_msg(s)
		if not msg or not msg.startswith('FILES:'):
			print('Bad response from scheduler:', msg)
			return
		files = msg.split(':', 1)[1].split('|')
		print('Available files:')
		for i, f in enumerate(files, 1):
			print(f'  {i}. {f}')

		# Choose file and optionally supply a word
		choice = input('Choose a file name (exact): ').strip()
		word_override = input('Optional: provide a word to search (or press Enter): ').strip()
		if word_override:
			send_msg(s, f'CHOICE:{choice}:{word_override}')
		else:
			send_msg(s, f'CHOICE:{choice}')

		# 2) Receive assignment (server_ip:server_port:word)
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

		# 3) Download file from the slave (raw socket protocol)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
			s2.connect((server_ip, server_port))
			# The slave expects raw filename bytes (no newline framing)
			s2.sendall(choice.encode('utf-8'))
			content = receive_all(s2)

		if not content:
			print('Slave returned no content (file may be missing)')
			count = 0
		else:
			# Count whole-word occurrences (case-insensitive).
			# If you prefer substring matching, replace this with content.lower().count(word.lower()).
			pattern = r"\b" + re.escape(word) + r"\b"
			matches = re.findall(pattern, content, flags=re.IGNORECASE)
			count = len(matches)
			print(f'Found {count} occurrences of "{word}" in {choice}')

		# 4) Report the result on the original scheduler connection
		send_msg(s, f'RESULT:{choice}:{count}')
		final = recv_msg(s)
		print('Scheduler reply:', final)


if __name__ == '__main__':
	main()

