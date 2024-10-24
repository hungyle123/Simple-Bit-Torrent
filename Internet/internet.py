import threading
import json
import socket
from collections import defaultdict

magnet_link = {"example.txt": "magnet:?xt=urn:btih:<hash1>&dn=example.txt",
            "movie.mp4": "magnet:?xt=urn:btih:<hash2>&dn=movie.mp4"}

class client_process(threading.Thread):
    def __init__(self, client_socket, addr):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.addr = addr
    
    def run(self):
        print(f"A client fromt {self.addr} has conntected to the Internet!")

        try:
            while True:
                client_require = self.node_socket.recv(1024*512).decode('utf-8')

                if client_require == 'send_torrent_list':
                    magnet_link_json = json.dumps(magnet_link)

                    # Gửi danh sách magnet link đã serialize cho client
                    self.client_socket.sendall(magnet_link_json.encode('utf-8'))
                    print(f"Sent torrent list to {self.addr}")
                
                if client_require == 'exit':
                    print(f"Client {self.addr} has disconnected.")
                    break

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()


class Server:
    def __init__(self, host = 'localhost', port = '1234'):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen(100)
        print("Welcome to the Computer Network!")
        print()

