import threading
import os
import json
import socket

class uploading(threading.Thread):
    def __init__(self, node_host = 'localhost', node_port = 1):
        threading.Thread.__init__(self)
        self.upload = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.upload.bind((node_host,node_port))
        self.upload.listen(5)


    def run(self):
        self.upload_socket,addr = self.upload.accept()
        message = self.upload_socket.recv(1024).decode('utf-8')

        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if message in os.listdir(current_dir):
            with open(message, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break

                    self.upload_socket.sendall(chunk)

        else:
            reply = f"We don't have that file"
            self.upload_socket.sendall(reply.encode('utf-8'))

        self.upload_socket.close()

class Node:
    def __init__(self, host = 'localhost', port = 1235):
        self.host = host
        self.port = port
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.node_socket.connect((host,port))

        file_have = []

        current_dir = os.path.dirname(os.path.abspath(__file__))

        for f in os.listdir(current_dir):
            if f.endswith('.txt'):
                file_have.append(f)

        data = json.dumps(file_have)

        self.node_socket.sendall(data.encode('utf-8'))

        node_host, node_port = self.node_socket.getsockname()

        upload = uploading(node_host,node_port)
        upload.start()

        try:
            while True:
                file_need = input("input: ")
                self.node_socket.sendall(file_need.encode('utf-8'))
                
                message = self.node_socket.recv(1024).decode('utf-8')

                print(message)

                if message != "Your wanted file is not in the Bittorrent right now!":
                    cleaned_message = message
                    print(f"Cleaned message: {cleaned_message}")  # In ra thông điệp đã làm sạch
                    server_ip, server_port = cleaned_message.split(':')

                    print(server_ip)
                    print('127.0.0.1')
                    print(server_port)
                    server_port = int(server_port) 

                    get_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    get_file.connect(('127.0.0.1',server_port))

                    get_file.sendall(file_need.encode('utf-8'))

                    with open(file_need,"wb") as f:
                        while True:
                            data = get_file.recv(1024)

                            if not data:
                                break

                            f.write(data)
                    
                    get_file.close()
                else:
                    print('That file is not in the Bittorrent')
        finally:
            self.node_socket.close()



if __name__ == "__main__":

    temp = Node()