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
class uploading(threading.Thread):  # chưa sửa
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
                a = 2
                # with lock:
                #     if current_thread == 'internet':
                #         print("------------------------Internet Interface!!----------------------------")

                #         request = input('input for the internet: ')

                #         if request == 'switch':
                #             current_thread = 'tracker'
                #         else:
                #             self.node_socket.sendall(request.encode('utf-8'))

                #             file_have = []
                #             current_dir = os.path.dirname(os.path.abspath(__file__))
                #             current_file = os.path.basename(__file__)

                #             print(current_dir)

                #             for f in os.listdir(current_dir):
                #                 full_path = os.path.join(current_dir, f)

                #                 print(full_path)

                #                 if os.path.isfile(full_path):  # If it's a file
                #                     torrent_content = create_torrent(full_path, tracker_url="http://example.com/announce")
                #                     # Encode the bytes to base64 string
                #                     file_have.append(torrent_content)
                                
                #                 elif os.path.isdir(full_path):  # If it's a directory
                #                     torrent_content = create_torrent(full_path, tracker_url="http://example.com/announce")
                #                     # Encode the bytes to base64 string
                #                     file_have.append(torrent_content)

                #             self.node_socket.sendall(len(file_have).to_bytes(8,'big'))

                #             # Send the list of files that the node has
                #             for file_path in file_have:
                #                 #data = json.dumps({"torrent_content": file_path})  # Wrap it in a dict for clarity
                #                 self.send_torrent(file_path)
                #                 time.sleep(2)

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
from tkinter import ttk
from tkinter import scrolledtext

class NodeApp:
    def __init__(self, host='localhost', port=1234):
        self.window = tk.Tk()
        self.window.title("Multi-threaded Node Application")

        # Create frames for internet and tracker interfaces
        self.internet_frame = tk.Frame(self.window, width=300, height=200, bg='lightgray')
        self.tracker_frame = tk.Frame(self.window, width=300, height=200, bg='lightgray')
        self.progress_frame = tk.Frame(self.window, width=300, height=200, bg='lightgray')
        self.selection_frame = tk.Frame(self.window, width=300, height=200, bg='lightgray')

        self.setup_internet_frame()
        self.setup_tracker_frame()
        self.setup_progress_frame()
        self.setup_selection_frame()

        # Start the internet and tracker processes
        self.inet_process = internet_process(host, port)
        self.tracker_process = node_process_tracker(host, 1235)
        self.inet_process.start()
        self.tracker_process.start()

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

        self.tracker_text_area = scrolledtext.ScrolledText(self.tracker_frame, width=40, height=10)
        self.tracker_text_area.pack(pady=10)

        switch_button = tk.Button(self.tracker_frame, text="Switch to Internet", command=self.switch_to_internet)
        switch_button.pack(pady=10)

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

            # You can now use self.selected_item for further actions
            # For example, if you want to use it in another function, you can access it like this:
            # key, value = self.selected_item
            # Perform any action with this key-value pair
        
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