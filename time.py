import socket
import time

def udp_ping(host, port, timeout=1):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    
    # Send UDP packet to the target host on the specified port
    message = b"Ping!"
    try:
        start_time = time.time()
        client_socket.sendto(message, (host, port))
        
        # Wait for a response
        data, server = client_socket.recvfrom(1024)
        end_time = time.time()
        
        print(f"Received response from {server}: {data}")
        print(f"Round-trip time: {end_time - start_time:.6f} seconds")
    
    except socket.timeout:
        print("Request timed out")
    
    finally:
        client_socket.close()

if __name__ == "__main__":
    udp_ping("lms.hcmut.edu.vn", 9999)  # Use an unusual port