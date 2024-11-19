import threading
import json
import socket
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
import hashlib
import bencodepy
import os
import pprint
import pickle

node_socket_list = []
file_name: Dict[Tuple[bytes,int], Set] = {}

def receive_simple_message(a_socket, decode_or_not):
    while True:
        raw_size = a_socket.recv(8)
        if not raw_size:
            continue

        break

    size = int.from_bytes(raw_size, 'big')

    # Đảm bảo đọc đủ số byte của thông điệp
    message = b''
    while len(message) < size:
        packet = a_socket.recv(size - len(message))
        if not packet:
            return None  # Kết nối đóng trong khi đang nhận dữ liệu
        message += packet

    if decode_or_not == True:
        return message.decode('utf-8')
    else:
        return message


def send_simple_message(a_socket,message, encode_or_not):
    a_socket.sendall(len(message).to_bytes(8,'big'))

    if encode_or_not == True:
        a_socket.sendall(message.encode('utf-8'))
    else:
        a_socket.sendall(message)

def receive_simple_number(a_socket):
    while True:
        raw_size = a_socket.recv(8)
        if not raw_size:
            continue

        break

    size = int.from_bytes(raw_size, 'big')

    return size

def send_simple_number(a_socket,number):
    a_socket.sendall(number.to_bytes(8,'big'))


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
                node_require = receive_simple_message(self.node_socket,True)

                if node_require == 'ask_seeder_ip':
                    self.ask_seeder_ip()
                if node_require == 'update_the_table':
                    self.update_the_table()
                    

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.node_socket.close()
            print(f'Close connection from {self.addr}')
    def update_the_table(self):
        table_transform = receive_simple_message(self.node_socket,False)

        table = pickle.loads(table_transform)

        for key in table:
            file_name[key].add(self.addr)
    

    def ask_seeder_ip(self):
        update_information_transform = receive_simple_message(self.node_socket,False)

        update_information = pickle.loads(update_information_transform)

        temporary_table: Dict[Tuple[bytes,int], Any] = {}

        for key in update_information:
            temporary_table[key] = file_name[key]

        temporary_table = dict(sorted(temporary_table.items(), key=lambda item: len(item[1])))

        used_addr: set = set()

        for key,ip_set in temporary_table.items():
            for i in ip_set:
                if i not in used_addr:
                    update_information[key] = i
                    used_addr.add(i)
                    break

        return_update_information = pickle.dumps(update_information)

        send_simple_message(self.node_socket,return_update_information,False)


                
    def broadcast(message, sender_socket):
        for i in node_socket_list:
            if i != sender_socket:
                try:
                    #i.sendall(message.encode('utf-8'))
                    send_simple_message(i,message,True)
                except:
                    node_socket_list.remove(i)
                    i.close()

class handle_internet_process(threading.Thread):
    def __init__(self, interneting_socket, host, port):
        threading.Thread.__init__(self)
        self.handle_internet_socket = interneting_socket
        self.handle_internet_socket.connect((host,port))
        print('Đã kết nối với internet server !!!')
    
    def run(self):      #Override
        try:
            while True:
                #internet_message = self.handle_internet_socket.recv(1024*512).decode('utf-8')
                internet_message = receive_simple_message(self.handle_internet_socket,True)
                
                if internet_message == 'information_file':
                    self.store_information()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.handle_internet_socket.close()
            print(f'Close connection from internet')

    def store_information(self):
        torrent_content = receive_simple_message(self.handle_internet_socket,False)

        ip_port_addr_json = receive_simple_message(self.handle_internet_socket,False)

        ip_port_addr = pickle.loads(ip_port_addr_json)

        print(f"Reading the torrent_content")

        var_torrent = bencodepy.decode(torrent_content)

        pieces = var_torrent[b'info'][b'pieces']

        pieces_hash = [pieces[i:i+20] for i in range(0,len(pieces),20)]

        file_info = var_torrent[b'info'][b'files']

        for i,file in enumerate(file_info):
            file_size = file[b'length']
            
            part_size = 512 * 1024
            num_part = (file_size + part_size - 1) // part_size

            for index in range(num_part):
                if (pieces_hash[i],index) not in file_name:
                    file_name[(pieces_hash[i],index)] = set()

                if ip_port_addr not in file_name[(pieces_hash[i],index)]:
                    file_name[(pieces_hash[i],index)].add(ip_port_addr)


        #pprint.pprint(file_name)
        print(f'Đã nhận thông tin cập nhật từ {ip_port_addr}')

        #os.remove(torrent_name_temp)

                
class Tracker:
    def __init__(self, host = 'localhost', port = 1235):
        self.host = host
        self.port = port
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # AF_INET là IPV4 AFINET6 là IPV6, SOCK_STREAM <=> TCP; SOCK_DGRAM <=> UDP
        self.tracker_socket.bind((self.host,self.port))
        self.tracker_socket.listen(20)

        #######
        self.interneting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        to_internet_socket = handle_internet_process(self.interneting_socket,'localhost',1234)
        to_internet_socket.start()
        ######  

        print("Server is running now!")

        while True:
            node_socket, addr = self.tracker_socket.accept()
            one_node_socket = node_process(node_socket,addr)    
            one_node_socket.start()

if __name__ == "__main__":

    file_name = {}
    temp = Tracker()