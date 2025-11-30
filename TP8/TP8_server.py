import socket
import struct
import os

def send_file_and_word(conn, file_path, word):

    try:
        import os
        file_name = os.path.basename(file_path)
        file_name_encoded = file_name.encode('utf-8')
        word_encoded = word.encode('utf-8')

        conn.send(struct.pack('!I', len(word_encoded)))
        conn.send(word_encoded)

        conn.send(struct.pack('!I', len(file_name_encoded)))
        conn.send(file_name_encoded)

        print(f"Sent file name '{file_name}' and word '{word}' to client")
        return True

    except Exception as e:
        print(f"Error sending file name: {e}")
        return False

def start_server(host='127.0.0.1', port=65432):
   
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            
            try:
               
                file_path = "amina.txt"
                word_to_count = "walk"
                
               
                
                if send_file_and_word(conn, file_path, word_to_count):
                  
                    result_data = conn.recv(1024).decode('utf-8')
                    print(f"Client result: {result_data}")
                
            except Exception as e:
                print(f"Error handling client: {e}")
            finally:
                conn.close()
                
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()



if __name__ == "__main__":
    start_server()