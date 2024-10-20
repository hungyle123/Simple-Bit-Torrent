import threading
import os
import json
import socket

class Node:
    def __init__(self, host = 'localhost', port = 1234):
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

        try:
            while True:
                sending_msg = input()
                self.node_socket.sendall(sending_msg.encode('utf-8'))
                
                message = self.node_socket.recv(1024).decode('utf-8')
                print(message)
        finally:
            self.node_socket.close()



if __name__ == "__main__":

    temp = Node()



        