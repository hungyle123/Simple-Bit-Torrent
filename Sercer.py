import socket
import threading

# List to store connected clients
clients = []

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, addr):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.addr = addr

    def run(self):
        print(f"Connection from {self.addr} has been established!")
        clients.append(self.client_socket)
        try:
            while True:
                client_msg = self.client_socket.recv(1024).decode('utf-8')
                if not client_msg:
                    break
                print(f"Client {self.addr}: {client_msg}")


                client_msg = f"Client {self.addr}: {client_msg}"
                
                # Broadcast the message to all other clients
                broadcast(client_msg, self.client_socket)
                
                if client_msg.lower() == "bye":
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()
            clients.remove(self.client_socket)
            print(f"Connection with {self.addr} closed.")
            temp = f"Connection with {self.addr} closed."
            broadcast(temp,self.client_socket)

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:  # Don't send the message back to the sender
            try:
                client.sendall(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 1234))
    server_socket.listen(5)
    print("Server is listening...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = ClientHandler(client_socket, addr)
        client_thread.start()

if __name__ == "__main__":
    main()
