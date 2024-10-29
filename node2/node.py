import threading
import os
import json
import socket
import base64
import time


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

import hashlib
import bencodepy

def calculate_hash(file_path):
    """Tính toán hash SHA-1 cho một tệp."""
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Đọc 64KB mỗi lần
            if not data:
                break
            sha1.update(data)
    return sha1.digest()

def create_torrent(input_path, tracker_url):
    """Tạo tệp torrent cho một file hoặc một thư mục."""
    files_info = []
    pieces = b""

    if os.path.isfile(input_path):  # Trường hợp input là một file
        file_hash = calculate_hash(input_path)
        file_length = os.path.getsize(input_path)

        files_info.append({
            'length': file_length,
            'path': [os.path.basename(input_path)]  # Lưu tên file
        })
        pieces += file_hash  # Hash của file

    else:  # Trường hợp input là một thư mục
        # Duyệt qua tất cả các tệp trong thư mục
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = calculate_hash(file_path)
                file_length = os.path.getsize(file_path)

                # Thêm thông tin tệp vào danh sách
                files_info.append({
                    'length': file_length,
                    'path': [os.path.relpath(file_path, input_path)]  # Lưu đường dẫn tương đối
                })

                # Thêm mã hash của tệp vào danh sách mã hash
                pieces += file_hash

    # Tạo cấu trúc tệp torrent
    torrent_data = {
        'announce': tracker_url,
        'info': {
            'files': files_info,
            'name': os.path.basename(input_path),
            'piece length': 262144,  # Kích thước mảnh (ví dụ: 256KB)
            'pieces': pieces,
        }
    }

    # Encode dữ liệu torrent
    encoded_torrent = bencodepy.encode(torrent_data)
    
    # Lưu tệp torrent vào thư mục hiện tại
    # torrent_filename = f"{os.path.basename(input_path)}.torrent"
    # with open(torrent_filename, 'wb') as torrent_file:
    #     torrent_file.write(encoded_torrent)
    
    # print(f"Tệp torrent đã được lưu trữ với tên: {torrent_filename}")

    return encoded_torrent

class internet_process(threading.Thread):
    def __init__(self, host='localhost', port=1234):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.node_socket.connect((self.host, self.port))
            print(f"Connected to the internet process at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to {self.host}:{self.port} - {e}")

    def run(self):
        try:
            while True:
                request = input('input: ')

                self.node_socket.sendall(request.encode('utf-8'))

                file_have = []
                current_dir = os.path.dirname(os.path.abspath(__file__))
                current_file = os.path.basename(__file__)

                print(current_dir)

                for f in os.listdir(current_dir):
                    full_path = os.path.join(current_dir, f)

                    print(full_path)

                    if os.path.isfile(full_path):  # If it's a file
                        torrent_content = create_torrent(full_path, tracker_url="http://example.com/announce")
                        # Encode the bytes to base64 string
                        file_have.append(torrent_content)
                    
                    elif os.path.isdir(full_path):  # If it's a directory
                        torrent_content = create_torrent(full_path, tracker_url="http://example.com/announce")
                        # Encode the bytes to base64 string
                        file_have.append(torrent_content)

                self.node_socket.sendall(len(file_have).to_bytes(8,'big'))

                # Send the list of files that the node has
                for file_path in file_have:
                    #data = json.dumps({"torrent_content": file_path})  # Wrap it in a dict for clarity
                    self.send_torrent(file_path)
                    time.sleep(2)

        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            self.node_socket.close()

    def send_torrent(self,torrent_content):
        
        self.node_socket.sendall(len(torrent_content).to_bytes(8,'big'))

        self.node_socket.sendall(torrent_content)
        print('Torrent file sent.')


class Node:
    def __init__(self, host = 'localhost', port = 1234):
        
        node_internet_process = internet_process(host,port)

        node_internet_process.start()

        node_internet_process.join()
            



if __name__ == "__main__":

    temp = Node()