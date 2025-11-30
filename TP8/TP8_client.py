import socket
import struct

def receive_file_and_word(conn):

    try:

        word_length_data = conn.recv(4)
        if not word_length_data:
            return None, None

        word_length = struct.unpack('!I', word_length_data)[0]
        word_encoded = conn.recv(word_length)
        word = word_encoded.decode('utf-8')


        file_name_length_data = conn.recv(4)
        if not file_name_length_data:
            return None, None

        file_name_length = struct.unpack('!I', file_name_length_data)[0]
        file_name_encoded = conn.recv(file_name_length)
        file_name = file_name_encoded.decode('utf-8')

        return file_name, word

    except Exception as e:
        print(f"Error receiving data: {e}")
        return None, None

def count_word_occurrences(text, word):
  
    return text.split().count(word)

def count_word_occurrences_case_insensitive(text, word):
  
    words = text.lower().split()
    return words.count(word.lower())

def start_client(host='127.0.0.1', port=65432):
  
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        
       
        file_name, word = receive_file_and_word(client_socket)

        if file_name and word:
            print(f"Received file name: '{file_name}'")
            print(f"Word to count: '{word}'")

            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                print(f"File content loaded ({len(file_content)} characters)")

                count_case_sensitive = count_word_occurrences(file_content, word)
                count_case_insensitive = count_word_occurrences_case_insensitive(file_content, word)

                result = f"""
Word Count Results:
-------------------
Word: '{word}'
Case-sensitive count: {count_case_sensitive}
Case-insensitive count: {count_case_insensitive}


"""
                print(result)

            except FileNotFoundError:
                print(f"File '{file_name}' not found on client side")
                result = f"Error: File '{file_name}' not found"
            except Exception as e:
                print(f"Error reading file: {e}")
                result = f"Error reading file: {e}"
            
           
            client_socket.send(result.encode('utf-8'))
            
        else:
            print("Failed to receive data from server")
            
    except ConnectionRefusedError:
        print(f"Could not connect to server {host}:{port}")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()