import socket
import re

HOST = '127.0.0.1'
PORT = 7777


def count_word_in_file(filename: str, word: str) -> int:
    with open('./' + filename, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    pattern = r'\b' + re.escape(word.lower()) + r'\b'
    return len(re.findall(pattern, content))


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # read header until newline: filename|word|size\n
    header_bytes = b''
    while b'\n' not in header_bytes:
        chunk = s.recv(4096)
        if not chunk:
            print('Server closed connection unexpectedly')
            s.close()
            return
        header_bytes += chunk

    header, rest = header_bytes.split(b'\n', 1)
    header_str = header.decode('utf-8')
    parts = header_str.split('|', 2)
    if len(parts) != 3:
        print('Invalid header from server:', header_str)
        s.close()
        return
    filename, word, size_str = parts
    try:
        size = int(size_str)
    except ValueError:
        print('Invalid size in header:', size_str)
        s.close()
        return

    file_bytes = rest
    to_read = size - len(file_bytes)
    while to_read > 0:
        chunk = s.recv(min(4096, to_read))
        if not chunk:
            print('Server closed connection while sending file')
            s.close()
            return
        file_bytes += chunk
        to_read -= len(chunk)

    file_text = file_bytes.decode('utf-8')
    pattern = r'\\b' + re.escape(word.lower()) + r'\\b'
    count = len(re.findall(pattern, file_text.lower()))

    result = f"{filename}|{count}"
    s.sendall(result.encode('utf-8'))
    s.close()
    print(f'Sent result for {filename}: {count}')


if __name__ == '__main__':
    main()
