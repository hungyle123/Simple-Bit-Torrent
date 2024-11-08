import threading
import json
import socket
from collections import defaultdict
import os

magnet_link = {}

import hashlib
import bencodepy

def create_magnet_link(torrent_filename):
    """Tạo magnet link từ file torrent."""
    with open(torrent_filename, 'rb') as f:
        torrent_data = bencodepy.decode(f.read())
    
    # Tính toán hash SHA1 của phần info
    info_hash = hashlib.sha1(bencodepy.encode(torrent_data[b'info'])).hexdigest()
    
    # Lấy tên file từ 'name' trong info để sử dụng trong magnet link
    file_name = torrent_data[b'info'][b'name'].decode()
    
    # Tạo magnet link
    magnet_uri = f"magnet:?xt=urn:btih:{info_hash}&dn={file_name}"
    
    return magnet_uri

def magnet_to_folder(magnet_link):
    # Tạo một chuỗi băm SHA-256 từ magnet link để làm tên thư mục
    folder_name = hashlib.sha256(magnet_link.encode()).hexdigest()
    return folder_name

class client_process(threading.Thread):
    def __init__(self, client_socket, addr, tracker_socket, tracker_addr):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.addr = addr
        self.tracker_socket = tracker_socket
        self.tracker_addr = tracker_addr

    def receive_torrent(self):
        torrent_size = int.from_bytes(self.client_socket.recv(8),'big')

        torrent_content = b""

        while len(torrent_content) < torrent_size:
            torrent_content += self.client_socket.recv(1024*512)  #64KB

        return torrent_content
    
    def run(self):
        print(f"A client from {self.addr} has connected to the Internet!")

        try:
            while True:
                client_require = self.client_socket.recv(1024*512).decode('utf-8')

                if client_require == 'send_torrent_list':
                    # Gửi file cho client
                    self.receive_send_torrrent_list()
                elif client_require == 'send':
                    # Nhận file torrent được gửi từ client
                    self.receive_send()
                elif client_require == 'send_torrent_file':
                    self.send_file_torrent()
                elif client_require == 'exit':
                    print(f"Client {self.addr} has disconnected.")
                    break
                else:
                    reply = f'Sorry your we do not understand your request'
                    
                    self.client_socket.sendall(reply.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()

    def send_file_torrent(self):
        magnet_file_receive = self.client_socket.recv(1024*512).decode('utf-8')
        
        magnet_folder = os.path.join(os.getcwd(),magnet_to_folder(magnet_file_receive))

        #print(f'hi: {magnet_folder}')

        files_in_folder = os.listdir(magnet_folder)
        if not files_in_folder:
            print("Không có file nào trong thư mục.")
            return

        torrent_file_path = os.path.join(magnet_folder, files_in_folder[0])

        #print(f'hi: {torrent_file_path}')
        # Lấy kích thước của file
        size_file = os.path.getsize(torrent_file_path)

        #print(f'hi: {size_file}')

        # Gửi kích thước file qua socket
        self.client_socket.sendall(size_file.to_bytes(8, 'big'))

        # Mở file và gửi dữ liệu theo từng phần
        with open(torrent_file_path, 'rb') as f:
            while True:
                # Đọc dữ liệu theo từng chunk (mỗi lần 4096 bytes)
                chunk = f.read(4096)
                if not chunk:
                    break  # Thoát khi đã đọc hết file
                print(f'hi: {chunk}')
                self.client_socket.sendall(chunk)  # Gửi chunk qua socket
        
        print("Đã gửi file torrent thành công.")


    def receive_send(self):
        try:
            # Nhận con số num_file: có bao nhiêu file torrent được tạo từ client gửi qua
            num_files = int.from_bytes(self.client_socket.recv(8), 'big')
            print(f"Receiving {num_files} torrent files...")

            for i in range(num_files):
                torrent_content = self.receive_torrent()

                ###
                self.protocol_send_tracker_information(torrent_content)
                ###

                torrent_filename = f"received_file_{i+1}.torrent"

                # Ghi tạm file ra để lát đọc được thông tin về cái file torrent đó tên j để lát đặt tên
                
                with open(torrent_filename, 'wb') as f:
                    f.write(torrent_content)
                print(f"Saved {torrent_filename}")

                # Ta sử dụng biến torrent_content để đọc tiếp các cái trường tên file nên cần 1 biến khác để giữ content torrent
                torrent_content_keep = torrent_content
                new_magnet_link = create_magnet_link(torrent_filename)

                with open(torrent_filename, 'rb') as torrent_file:
                    try:
                        torrent_content = bencodepy.decode(torrent_file.read())
                    except Exception as e:
                        print(f"Error decoding torrent file: {e}")
                        continue  # Skip this iteration if decoding fails


                torrent_name = torrent_content[b'info'][b'name'].decode()  # Lấy trường 'name' từ torrent
                final_torrent_filename = f"{torrent_name}.torrent"

                # Tạo folder với tên là 1 cái hash id để lúc sau truy vấn
                magnet_folder = os.path.join(os.getcwd(), magnet_to_folder(new_magnet_link))
                os.makedirs(magnet_folder, exist_ok=True)
                final_torrent_path = os.path.join(magnet_folder, final_torrent_filename)

                with open(final_torrent_path, 'wb') as new_torrent_file:
                    new_torrent_file.write(torrent_content_keep)  # Ghi nội dung tệp torrent mới
                print(f"Saved new torrent file as {final_torrent_path}")

                #Thêm vào dictionary magnet_link với tên tệp và giá trị Magnet link
                magnet_link[new_magnet_link] = torrent_name
                print(f"Added new magnet link: {new_magnet_link}:{torrent_name}")

                #Sau đó xóa cái file tạm (file để lấy tên torrent)
                os.remove(torrent_filename)
        except Exception as e:
            print(f"Error: {e}")
            
    def receive_send_torrrent_list(self):

        magnet_link_json = json.dumps(magnet_link)

        # Gửi danh sách magnet link đã serialize cho client
        self.client_socket.sendall(magnet_link_json.encode('utf-8'))
        print(f"Sent torrent list to {self.addr}")

    def protocol_send_tracker_information(self, torrent_content):
        message = f'information_file'

        self.tracker_socket.sendall(message.decode('utf-8'))

        self.tracker_socket.sendall(len(torrent_content).to_bytes(8,'big'))

        self.tracker_socket.sendall(torrent_content)

        self.tracker_socket.sendall(self.addr.decode('utf-8'))
        print('Đã chuyển tiếp qua cho tracker')




class Server:
    def __init__(self, host = 'localhost', port = 1234):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen(100)
        print("Welcome to the Computer Network!")
        print()

        while True:
            node_socket, addr = self.server_socket.accept()
            
            one_client_socket = client_process(node_socket,addr)    
            one_client_socket.start()

if __name__ == "__main__":

    temp = Server()
