import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Message received: {message}")
            else:
                break
        except:
            print("Connection closed by server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 1234))

    # Start a thread to continuously receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    try:
        while True:
            sending_msg = input()
            client_socket.sendall(sending_msg.encode('utf-8'))
            if sending_msg.lower() == "bye":
                break
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
