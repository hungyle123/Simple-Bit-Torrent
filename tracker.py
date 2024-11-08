import threading
import json
import socket
from collections import defaultdict
from typing import Dict, List, Set
import hashlib
import bencodepy
import os

node_socket_list = []
file_name: Dict[bytes, Dict[int, Set]] = {}

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

class handle_internet_process(threading.Thread):
    def __init__(self, tracker_socket, host, port):
        threading.Thread.__init__(self)
        self.handle_internet_socket = tracker_socket
        self.handle_internet_socket.connect((host,port))
        print('Đã kết nối với internet server !!!')
    
    def run(self):      #Override
        try:
            while True:
                internet_message = self.handle_internet_socket.recv(1024*512).decode('utf-8')
                
                if internet_message == 'information_file':
                    self.store_information()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.handle_internet_socket.close()
            print(f'Close connection from internet')

    def store_information(self):
        torrent_size = int.from_bytes(self.handle_internet_socket.recv(8),'big')

        torrent_content = b""
        while len(torrent_content) < torrent_size:
            torrent_content += self.handle_internet_socket.recv(1024*512)

        ip_port_addr = self.handle_internet_socket.recv(1024*512).encode('utf-8')

        torrent_name_temp = f'temp_file.torrent'

        with open(torrent_name_temp,'wb') as f:
            f.write(torrent_content)

        print(f"Save temporary {torrent_name_temp}")

        var_torrent = None

        with open(torrent_name_temp, 'rb') as f:
            var_torrent = bencodepy.decode(f)

        pieces = var_torrent[b'info'][b'pieces']

        pieces_hash = [pieces[i:i+20] for i in range(0,len(pieces),20)]

        file_info = var_torrent[b'info'][b'files']

        for i,file in enumerate(file_info):
            file_size = file[b'length']
            
            part_size = 512 * 1024
            num_part = (file_size + part_size - 1) // part_size

            if pieces[i] not in file_name:
                file_name[pieces[i]] = {}

            for index in range(num_part):
                if index not in file_name[pieces[i]]:
                    file_name[pieces[i]][index] = set()

                if ip_port_addr not in file_name[pieces[i]][index]:
                    file_name[pieces[i]][index].add(ip_port_addr)

        os.remove(torrent_name_temp)

                
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

            # data = node_socket.recv(1024*512).decode('utf-8')

            # file_list = json.loads(data)

            # for f in file_list:
            #     if f not in file_name:
            #         file_name[f] = set()  # Khởi tạo tập hợp nếu tệp chưa tồn tại
            #     file_name[f].add(addr)
            #     print(f)
            
            one_node_socket = node_process(node_socket,addr)    
            one_node_socket.start()

if __name__ == "__main__":

    file_name = {}
    temp = Tracker()