import threading
import os
import json
import socket
import base64
import time
import tkinter as tk
from tkinter import scrolledtext, filedialog
from typing import Dict, List, Set, Any, Tuple
import pickle
import mimetypes

current_thread = 'internet'
lock = threading.Lock()

cache_data: Dict[Tuple[bytes,int], Any] = {}
hash_addr: Dict[Tuple[bytes,int], str] = {}

already_received: Dict[Tuple[bytes,int], Any] = {}
not_yet_received: Dict[Tuple[bytes,int], Any] = {}

def is_binary_file(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    # MIME types thường bắt đầu với "text" hoặc "application"
    if mime_type is not None:
        return not mime_type.startswith("text")
    # Nếu không đoán được loại MIME, giả định đó là file nhị phân
    return True

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




####################################################
class uploading(threading.Thread):
    def __init__(self, upload_socket, addr):
        threading.Thread.__init__(self)
        self.upload_socket = upload_socket
        self.addr = addr

    def run(self):

        request = receive_simple_message(self.upload_socket,True)

        if request == 'ask_for_file_content_folder_mode':
            self.folder_mode()
        else:
            self.file_mode()


        print(f'Send file part to {self.addr}')


    def folder_mode(self):
        information_change = receive_simple_message(self.upload_socket,False)

        information = pickle.loads(information_change)

        key_hash,key_num_part,path_name,name_torrent,file_type = information

        return_content = None

        if (key_hash,key_num_part) in cache_data:
            return_content = cache_data[(key_hash,key_num_part)]
        else:
            full_path = os.path.join(name_torrent,path_name)

            chunk_size = 1024*512
            part = key_num_part
            with open(full_path, 'rb') as f:
                f.seek(part * chunk_size)

                return_content = f.read(chunk_size)

            
        if file_type == True:
            send_simple_message(self.upload_socket,return_content,False)
        else:
            send_simple_message(self.upload_socket,return_content,True)

    def file_mode(self):
        print('test1')
        information_change = receive_simple_message(self.upload_socket,False)

        information = pickle.loads(information_change)

        key_hash,key_num_part,path_name,name_torrent,file_type = information

        return_content = None

        if (key_hash,key_num_part) in cache_data:
            return_content = cache_data[(key_hash,key_num_part)]
        else:
            full_path = path_name

            chunk_size = 1024*512
            part = key_num_part
            with open(full_path, 'rb') as f:
                f.seek(part * chunk_size)

                return_content = f.read(chunk_size)

        print('test2')
        if file_type == True:
            print('test3')
            send_simple_message(self.upload_socket,return_content,False)
        else:
            print('test3')
            #send_simple_message(self.upload_socket,return_content,True)
            send_simple_message(self.upload_socket,return_content,False)

class uploading_server(threading.Thread):  # chưa sửa
    def __init__(self, node_host = 'localhost', node_port = 1):
        threading.Thread.__init__(self)
        self.upload = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.upload.bind((node_host,node_port))
        self.upload.listen(20)


    def run(self):
        while True:
            upload_socket, addr = self.upload.accept()

            new_upload = uploading(upload_socket,addr)

            new_upload.start()

        

####################################################

class downloading(threading.Thread):
    def __init__(self,connect_to_host,connect_to_port,this_host,this_port,key,folder_or_not,name_torrent):
        threading.Thread.__init__(self)
        self.key = key
        self.folder_or_not = folder_or_not
        self.name_torrent = name_torrent
        self.this_host = this_host
        self.this_port = this_port
        self.download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.download_socket.bind((this_host,this_port))
        self.download_socket.connect((connect_to_host,connect_to_port))
        print(key)
        print(f'Connecting to the {(connect_to_host,connect_to_port)} to get the {key[1]} part of file {hash_addr[key]}')


    def run(self):

        if self.folder_or_not == True:
            print(1)
            self.folder_mode()
        else:
            print(1)
            self.file_mode()

        self.download_socket.close()
        print(f'Close connecting')

        

    def folder_mode(self):
        request = 'ask_for_file_content_folder_mode'

        send_simple_message(self.download_socket,request,True)

        file_type = is_binary_file(hash_addr[self.key[0]])

        information = (self.key[0],self.key[1],hash_addr[self.key[0]],self.name_torrent,file_type)

        information_change = pickle.dumps(information)

        send_simple_message(self.download_socket,information_change,False)

        file_content = None
        if file_type == True:
            file_content = receive_simple_message(self.download_socket,False)
        else:
            file_content = receive_simple_message(self.download_socket,False)

        cache_data[(self.key[0],self.key[1])] = file_content
        already_received[(self.key[0],self.key[1])] = (self.this_host,self.this_port)

    def file_mode(self):
        request = 'ask_for_file_content_file_mode'
        print(2)

        send_simple_message(self.download_socket,request,True)

        file_type = is_binary_file(hash_addr[self.key])

        information = (self.key[0],self.key[1],hash_addr[self.key],self.name_torrent,file_type)

        information_change = pickle.dumps(information)

        print(3)

        send_simple_message(self.download_socket,information_change,False)

        print(4)

        file_content = None
        if file_type == True:
            file_content = receive_simple_message(self.download_socket,False)
        else:
            file_content = receive_simple_message(self.download_socket,False)

        cache_data[(self.key[0],self.key[1])] = file_content
        already_received[(self.key[0],self.key[1])] = (self.this_host,self.this_port)

####################################################

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
            'path': os.path.basename(input_path)  # Lưu tên file
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
                    'path': os.path.relpath(file_path, input_path)  # Lưu đường dẫn tương đối
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
                a = 2

        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            self.node_socket.close()

    def ask_for_torrent(self):
        try:
            request = 'send_torrent_list'
            #self.node_socket.sendall(request.encode('utf-8'))
            send_simple_message(self.node_socket,request,True)

            #data = self.node_socket.recv(4096)  # Nhận gói dữ liệu đầu tiên (4096 bytes là buffer size)
            data = receive_simple_message(self.node_socket,False)

            magnet_link = json.loads(data.decode('utf-8'))  # Giải mã dữ liệu nhận được và chuyển đổi từ JSON sang dictionary

            print("Received torrent list:", magnet_link)
            return magnet_link
        
        except Exception as e:
            print(f"Error during communication: {e}")

    def send_torrent(self,torrent_content):
        
        # self.node_socket.sendall(len(torrent_content).to_bytes(8,'big'))
        # self.node_socket.sendall(torrent_content)
        send_simple_message(self.node_socket,torrent_content,False)

        print('Torrent file sent.')

    def send(self):
        try:
            request = 'send'
            #self.node_socket.sendall(request.encode('utf-8'))
            send_simple_message(self.node_socket,request,True)

            file_have = []
            current_dir = os.path.dirname(os.path.abspath(__file__))
            current_file = os.path.basename(__file__)

            print(current_dir)

            for f in os.listdir(current_dir):
                if(f != current_file):
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

            #self.node_socket.sendall(len(file_have).to_bytes(8,'big'))
            send_simple_number(self.node_socket,len(file_have))

            # Send the list of files that the node has
            for file_path in file_have:
                #data = json.dumps({"torrent_content": file_path})  # Wrap it in a dict for clarity
                self.send_torrent(file_path)
                time.sleep(2)
        except Exception as e:
            print(f"Error sending torrent file: {e}")

    def receive_file_torrent(self,magnet_link, name_file):
        message = f'send_torrent_file'

        #self.node_socket.sendall(message.encode('utf-8'))
        send_simple_message(self.node_socket,message,True)

        #self.node_socket.sendall(magnet_link.encode('utf-8'))
        send_simple_message(self.node_socket,magnet_link,True)

        # size_file = int.from_bytes(self.node_socket.recv(8),'big')

        # torrent_content = b""

        # while len(torrent_content) < size_file:
        #     torrent_content += self.node_socket.recv(1024*512)
        torrent_content = receive_simple_message(self.node_socket,False)

        name_file += '.torrent'

        file_path = os.path.join(os.getcwd(), name_file)

        # Lưu nội dung vào file
        with open(file_path, 'wb') as f:
            f.write(torrent_content)

        print(f"Đã lưu file torrent tại {file_path}.")

        


class node_process_tracker(threading.Thread):
    def __init__(self, this_ip, this_port,host = 'localhost', port = 1235):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.this_ip = this_ip
        self.this_port = this_port
        self.node_to_tracker = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            #self.node_to_tracker.bind((self.this_ip,self.this_port))
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

    def ask_for_the_list_ip_file(self,torrent_path):

        update_information: Dict[Tuple[bytes,int], Set] = {}

        with open(torrent_path, 'rb') as f:
            torrent_content = bencodepy.decode(f.read())

            piece = torrent_content[b'info'][b'pieces']

            piece_hash = [piece[i:i+20] for i in range(0,len(piece),20)]

            file_info = torrent_content[b'info'][b'files']

            total_num_part = 0

            folder_or_not = True

            if (len(torrent_content[b'info'][b'files']) == 1) and (torrent_content[b'info'][b'name'] == torrent_content[b'info'][b'files'][0][b'path']):
                folder_or_not = False
            else:
                folder_or_not = True

            for i,file in enumerate(file_info):
                file_size = file[b'length']

                part_size = 512*1024
                num_part = (file_size + part_size - 1) // part_size
                total_num_part += num_part

                for index in range(num_part):
                    cache_data[(piece_hash[i],index)] = None
                    hash_addr[(piece_hash[i],index)] = torrent_content[b'info'][b'files'][i][b'path'].decode('utf-8')
            

            update_information = cache_data

            print(1)

            self.process_taking_file(update_information,total_num_part,folder_or_not,torrent_content[b'info'][b'name'])

            for key in piece_hash:
                data = self.retrieve_file_data(key,cache_data)

                with open('temp', 'wb') as f:
                    f.write(data)


    def retrieve_file_data(self, file_id: bytes, cache_data: Dict[Tuple[bytes, int], Any]) -> bytes:
        # Lấy tất cả các phần dữ liệu liên quan đến file_id, gồm cả part và data
        chunks = [(part, data) for (key_id, part), data in cache_data.items() if key_id == file_id]
        
        # Sắp xếp các chunk theo thứ tự part
        sorted_chunks = sorted(chunks, key=lambda item: item[0])  # item[0] là part

        # Nối tất cả các chunk lại thành dữ liệu hoàn chỉnh
        file_data = b''.join(data for _, data in sorted_chunks)
        return file_data



    def process_taking_file(self,update_information,total_num_part,folder_or_not,name_torrent):
        not_yet_received = {}

        while total_num_part != 0:
            threads = []

            received_ip_list = self.send_another_update(update_information)

            print(2)

            for key in received_ip_list:
                if received_ip_list[key] == None:
                    not_yet_received[key] = None
                else:

                    print(received_ip_list[key][0])
                    print(type(received_ip_list[key][0]))
                    print(received_ip_list[key][1])
                    print(type(received_ip_list[key][1]))
                    thread_download = downloading(received_ip_list[key][0],received_ip_list[key][1],self.this_ip,self.this_port,key,folder_or_not,name_torrent)

                    thread_download.start()
                    threads.append(thread_download)


            for i in threads:
                i.join()


            print(3)

            total_num_part -= len(threads)

            self.send_the_chunk_receive()
            update_information = not_yet_received
            not_yet_received = {}
            already_received = {}

        print('Complete')

    def send_another_update(self,update_information):
        request = f'ask_seeder_ip'

        send_simple_message(self.node_to_tracker,request,True)

        update_information_transform = pickle.dumps(update_information)

        send_simple_message(self.node_to_tracker,update_information_transform,False)

        received_ip_list_transform = receive_simple_message(self.node_to_tracker,False)

        received_ip = pickle.loads(received_ip_list_transform)

        return received_ip


    def send_the_chunk_receive(self):
        request = f'update_the_table'

        send_simple_message(self.node_to_tracker,request,True)

        already_received_transform = pickle.dumps(already_received)

        send_simple_message(self.node_to_tracker,already_received_transform,False)



class Node:
    def __init__(self, host = 'localhost', port = 1234):
        
        node_internet_process = internet_process(host,port)

        #this_ip,this_port = node_internet_process.node_socket.getsockname()

        node_tracker_process = node_process_tracker(host,1235)

        node_internet_process.start()
        node_tracker_process.start()

        node_internet_process.join()    
        node_tracker_process.join()
            



# if __name__ == "__main__":

#     temp = Node()
from tkinter import ttk
from tkinter import scrolledtext

class NodeApp:
    def __init__(self, host='localhost', port=1234):
        self.window = tk.Tk()
        self.window.title("Multi-threaded Node Application")

        # Create frames for internet and tracker interfaces
        self.internet_frame = tk.Frame(self.window, width=400, height=300, bg='lightgray')
        self.internet_frame.pack_propagate(False)
        self.tracker_frame = tk.Frame(self.window, width=400, height=300, bg='lightgray')
        self.tracker_frame.pack_propagate(False)
        self.progress_frame = tk.Frame(self.window, width=400, height=300, bg='lightgray')
        self.progress_frame.pack_propagate(False)
        self.selection_frame = tk.Frame(self.window, width=400, height=300, bg='lightgray')
        self.selection_frame.pack_propagate(False)

        self.setup_internet_frame()
        self.setup_tracker_frame()
        self.setup_progress_frame()
        self.setup_selection_frame()

        # Start the internet and tracker processes
        self.inet_process = internet_process(host, port)
        this_ip,this_port = self.inet_process.node_socket.getsockname()
        self.tracker_process = node_process_tracker(this_ip,this_port,host, 1235)
        self.inet_process.start()
        self.tracker_process.start()
        self.the_server_upload = uploading_server(this_ip,this_port)
        self.the_server_upload.start()

        # Show the internet frame initially
        self.show_frame(self.internet_frame)

        # Start the GUI main loop
        self.window.mainloop()

    def setup_internet_frame(self):
        label = tk.Label(self.internet_frame, text="Internet Interface")
        label.pack(pady=10)

        switch_button = tk.Button(self.internet_frame, text="Switch to Tracker", command=self.switch_to_tracker)
        switch_button.pack(pady=10)

        send_button = tk.Button(self.internet_frame, text="Send Files", command=self.start_sending_files)
        send_button.pack(pady=10)

        receive_button = tk.Button(self.internet_frame, text="Receive Torrent List", command=self.receive_list_torrent)
        receive_button.pack(pady=10)

    def setup_tracker_frame(self):
        label = tk.Label(self.tracker_frame, text="Tracker Interface")
        label.pack(pady=10)

        switch_button = tk.Button(self.tracker_frame, text="Switch to Internet", command=self.switch_to_internet)
        switch_button.pack(pady=10)

        load_torrent_button = tk.Button(self.tracker_frame, text="Load Torrent File", command=self.load_torrent_file)
        load_torrent_button.pack(pady=10)

    def load_torrent_file(self):
        # Open file dialog and filter for .torrent files
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a Torrent File",
            filetypes=(("Torrent files", "*.torrent"), ("All files", "*.*"))
        )

        print(f'You chose {file_path}')

        self.tracker_process.ask_for_the_list_ip_file(file_path)

        print('Done all')
        #....

    def setup_progress_frame(self):
        label = tk.Label(self.progress_frame, text="Sending Files...")
        label.pack(pady=10)

    
        # Progress bar setup
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=200)
        self.progress_bar.pack(pady=10)
    
    def setup_selection_frame(self):
        label = tk.Label(self.selection_frame, text="Select Torrent", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=3, pady=10)

        # Vertical and Horizontal scrollbars for the Listbox
        self.listbox = tk.Listbox(self.selection_frame, width=20, height=10)
        self.listbox.grid(row=1, column=0, padx=(20, 5), pady=10, sticky="ns")

        y_scroll = tk.Scrollbar(self.selection_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        y_scroll.grid(row=1, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=y_scroll.set)

        x_scroll = tk.Scrollbar(self.selection_frame, orient=tk.HORIZONTAL, command=self.listbox.xview)
        x_scroll.grid(row=2, column=0, sticky="ew")
        self.listbox.config(xscrollcommand=x_scroll.set)

        # Text widget on the right for displaying values
        self.text_display = scrolledtext.ScrolledText(self.selection_frame, wrap=tk.WORD, width=40, height=10)
        self.text_display.grid(row=1, column=2, padx=(5, 20), pady=10, rowspan=2)

        # Define text tags for colors
        self.text_display.tag_configure("key", foreground="black")
        self.text_display.tag_configure("value", foreground="blue")

        # Bind selection event to update value display
        self.listbox.bind("<<ListboxSelect>>", self.on_key_select)

        # Add "Select" button to confirm selection
        self.select_button = tk.Button(self.selection_frame, text="Select", command=self.select_item)
        self.select_button.grid(row=3, column=0, columnspan=3, pady=10)

        # Add "Back" button to go back to the internet interface
        back_button = tk.Button(self.selection_frame, text="Back to internet_process", command=lambda: self.show_frame(self.internet_frame))
        back_button.grid(row=4, column=0, columnspan=3, pady=5)

    def start_sending_files(self):
        # Switch to the progress frame and start the progress bar
        self.show_frame(self.progress_frame)
        self.progress_bar.start(10)  # Start the progress bar animation
        
        self.window.update_idletasks()

        # Start the send_files method in a new thread to avoid blocking the GUI
        threading.Thread(target=self.send_files).start()

    def send_files(self):
        # Simulate sending files for demonstration purposes
        self.inet_process.send() # Replace with actual file-sending code

        # Stop progress bar animation and switch back to internet frame
        self.progress_bar.stop()
        self.show_frame(self.internet_frame)

    def receive_list_torrent(self):
        magnet_link = self.inet_process.ask_for_torrent()  # Assume this returns a dictionary

        if isinstance(magnet_link, dict):
            self.data = magnet_link
            self.update_listbox()

            # Show the select frame after data is received
            self.show_frame(self.selection_frame)
            self.window.update_idletasks()

    def update_listbox(self):
        # Clear any existing items in the listbox
        self.listbox.delete(0, tk.END)
        
        # Populate listbox with new keys
        for key in self.data.keys():
            self.listbox.insert(tk.END, key)

    def on_key_select(self, event):
        # Get selected key from listbox
        selected_index = self.listbox.curselection()
        if selected_index:
            key = self.listbox.get(selected_index)
            value = self.data.get(key, "")

            # Update the text display with the selected key's value
            self.text_display.config(state=tk.NORMAL)
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"{key}: ", "key")
            self.text_display.insert(tk.END, f"{value}", "value")
            self.text_display.config(state=tk.DISABLED)

    def select_item(self):
        # Get selected key from listbox
        selected_index = self.listbox.curselection()
        if selected_index:
            key = self.listbox.get(selected_index)
            value = self.data.get(key)

            # Save the selected item to the instance variable
            self.selected_item = (key, value)

            # Optional: Show a confirmation message
            print(f"Selected: {key}: {value}")

            self.inet_process.receive_file_torrent(key,value)

            print('Đã lưu trên local ...')
        

        self.show_frame(self.internet_frame)

    ### hàm này đang ko xài
    def handle_selection(self):
        # Lấy mục đã chọn từ Listbox
        selected_index = self.listbox.curselection()

        if selected_index:
            # Lấy giá trị của item đã chọn
            selected_item = self.listbox.get(selected_index[0])
            print("Selected torrent:", selected_item)

            # Lưu giá trị chọn vào biến cho các bước sau
            self.selected_torrent = selected_item

            # Sau khi xử lý, quay lại giao diện internet
            self.show_frame(self.internet_frame)

            # Nếu bạn muốn sử dụng giá trị này để gửi file, ví dụ:
            # self.send_selected_file(self.selected_torrent)
        else:
            print("No selection made.")

    def show_frame(self, frame):
        # Hide all frames and show only the selected frame
        for f in [self.internet_frame, self.tracker_frame, self.progress_frame, self.selection_frame]:
            if(f != frame):
                f.pack_forget()
        frame.pack(fill='both', expand=True)

    def switch_to_tracker(self):
        self.show_frame(self.tracker_frame)

    def switch_to_internet(self):
        self.show_frame(self.internet_frame)

if __name__ == "__main__":
    NodeApp()