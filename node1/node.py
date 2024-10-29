import threading
import os
import json
import socket
import base64
import time
import tkinter as tk
from tkinter import scrolledtext

current_thread = 'internet'
lock = threading.Lock()

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
            global current_thread
            while True:
                with lock:
                    if current_thread == 'internet':
                        print("------------------------Internet Interface!!----------------------------")

                        request = input('input for the internet: ')

                        if request == 'switch':
                            current_thread = 'tracker'
                        else:
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

    def send(self):
        try:
            request = 'send'
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
            print(f"Error sending torrent file: {e}")


class node_process_tracker(threading.Thread):
    def __init__(self,host = 'localhost', port = 1235):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.node_to_tracker = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.node_to_tracker.connect((self.host,self.port))
            print(f"Connected to the tracker process at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to {self.host}:{self.port}")

    def run(self):
        try:
            global current_thread
            while True:
                with lock:
                    if current_thread == 'tracker':
                        print("------------------------Tracker Interface!!----------------------------")

                        request = input('input for the tracker: ')
                        if request == 'switch':
                            current_thread = 'internet'
                        else:
                            print("temp")

        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            self.node_to_tracker.close()


class Node:
    def __init__(self, host = 'localhost', port = 1234):
        
        node_internet_process = internet_process(host,port)
        node_tracker_process = node_process_tracker(host,1235)

        node_internet_process.start()
        node_tracker_process.start()

        node_internet_process.join()    
        node_tracker_process.join()
            



# if __name__ == "__main__":

#     temp = Node()


class NodeApp:
    def __init__(self, host = 'localhost', port = 1234):
        self.window = tk.Tk()
        self.window.title("Multi-threaded Node Application")

        # Create frames for internet and tracker interfaces
        self.internet_frame = tk.Frame(self.window)
        self.tracker_frame = tk.Frame(self.window)

        self.setup_internet_frame()
        self.setup_tracker_frame()

        # Start the internet and tracker processes
        self.inet_process = internet_process(host,port)
        self.tracker_process = node_process_tracker(host,1235)
        self.inet_process.start()
        self.tracker_process.start()

        # Show the internet frame initially
        self.show_frame(self.internet_frame)

        # Start the GUI main loop
        self.window.mainloop()

    def setup_internet_frame(self):
        label = tk.Label(self.internet_frame, text="Internet Interface")
        label.pack(pady=10)

        # self.text_area = scrolledtext.ScrolledText(self.internet_frame, width=40, height=10)
        # self.text_area.pack(pady=10)

        switch_button = tk.Button(self.internet_frame, text="Switch to Tracker", command=self.switch_to_tracker)
        switch_button.pack(pady=10)

        send_button = tk.Button(self.internet_frame, text="Send Files", command=self.send_files)
        send_button.pack(pady=10)
    def send_files(self):
        # Call the method in the internet process to send torrent files
        self.inet_process.send()

    def setup_tracker_frame(self):
        label = tk.Label(self.tracker_frame, text="Tracker Interface")
        label.pack(pady=10)

        self.tracker_text_area = scrolledtext.ScrolledText(self.tracker_frame, width=40, height=10)
        self.tracker_text_area.pack(pady=10)

        switch_button = tk.Button(self.tracker_frame, text="Switch to Internet", command=self.switch_to_internet)
        switch_button.pack(pady=10)

    def show_frame(self, frame):
        frame.pack(fill='both', expand=True)
        if frame == self.internet_frame:
            self.tracker_frame.pack_forget()
        else:
            self.internet_frame.pack_forget()

    def switch_to_tracker(self):
        global current_thread
        current_thread = 'tracker'
        self.show_frame(self.tracker_frame)

    def switch_to_internet(self):
        global current_thread
        current_thread = 'internet'
        self.show_frame(self.internet_frame)

if __name__ == "__main__":
    NodeApp()