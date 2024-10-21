import threading
import json
import socket
from collections import defaultdict

node_socket_list = []
file_name = {}

class node_process(threading.Thread):
    def __init__(self, node_socket, addr):
        threading.Thread.__init__(self)
        self.node_socket = node_socket
        self.addr = addr
    
    def run(self):      #Override
        print(f"Connection from {self.addr} has been established!")
        node_socket_list.append(self.node_socket)

        try:
            while True:
                node_require = self.node_socket.recv(1024*512).decode('utf-8')
                
                if node_require not in file_name:
                    reply = f'Your wanted file is not in the Bittorrent right now!'

                    self.node_socket.sendall(reply.encode('utf-8'))
                else:

                    host,port = next(iter(file_name[node_require]))
                    reply = f'{host}:{port}'

                    self.node_socket.sendall(reply.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.node_socket.close()
            print(f'Close connection from {self.addr}')
                
    def broadcast(message, sender_socket):
        for i in node_socket_list:
            if i != sender_socket:
                try:
                    i.sendall(message.encode('utf-8'))
                except:
                    node_socket_list.remove(i)
                    i.close()
class Tracker:
    def __init__(self, host = 'localhost', port = 1235):
        self.host = host
        self.port = port
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # AF_INET là IPV4 AFINET6 là IPV6, SOCK_STREAM <=> TCP; SOCK_DGRAM <=> UDP
        self.tracker_socket.bind((self.host,self.port))
        self.tracker_socket.listen(20)

        print("Server is running now!")

        while True:
            node_socket, addr = self.tracker_socket.accept()

            data = node_socket.recv(1024*512).decode('utf-8')

            file_list = json.loads(data)

            for f in file_list:
                if f not in file_name:
                    file_name[f] = set()  # Khởi tạo tập hợp nếu tệp chưa tồn tại
                file_name[f].add(addr)
                print(f)
            
            one_node_socket = node_process(node_socket,addr)    
            one_node_socket.start()
        

        

if __name__ == "__main__":

    file_name = defaultdict(set)
    temp = Tracker()