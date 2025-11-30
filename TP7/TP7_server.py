import socket
import os
import re


HOST = '127.0.0.1'
PORT = 8888

def get_txt_files():
    files = [f for f in os.listdir('./') if f.endswith('.txt')]
    return files

def count_word_occurrences(filename, word):
    with open('./' + filename, 'r', encoding='utf-8') as file:
        content = file.read().lower()
        word = word.lower()
        occurrences = len(re.findall(r'\b' + re.escape(word) + r'\b', content))
        return occurrences

def handle_client(client_socket):
    files = get_txt_files()
    file_list = '\n'.join(files)
    client_socket.send(file_list.encode('utf-8'))

    request = client_socket.recv(1024).decode('utf-8')
    if '|' not in request:
        result = "Error: Invalid request format. Expected 'filename|word'"
    else:
        filename, word = request.split('|', 1)
        result = count_word_occurrences(filename, word)
        result = f"The word '{word}' appears {result} times in '{filename}'."

    client_socket.send(str(result).encode('utf-8'))
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected by {addr}")
        handle_client(client_socket)

    server_socket.close()

main()
