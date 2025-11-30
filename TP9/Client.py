import socket
import json
import re

HOST = 'localhost'
PORT = 9001

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        files_bytes = s.recv(4096)
        files_json = files_bytes.decode('utf-8')
        files = json.loads(files_json)
        print("Available files:")
        for i, fname in enumerate(files):
            print(f"{i+1}. {fname}")

        file_choice = input("Enter the file name from the list above: ").strip()

        word = input("Enter the word to count in the file: ").strip()

        selection = {"file": file_choice, "word": word}
        selection_json = json.dumps(selection)
        s.sendall(selection_json.encode('utf-8'))

        count = s.recv(1024).decode('utf-8')

        if count == -1:
            print(f"File '{file_choice}' not found or error occurred.")
        else:
            print(f"The word '{word}' occurs {count} times in file '{file_choice}'.")


if __name__ == '__main__':
    main()
