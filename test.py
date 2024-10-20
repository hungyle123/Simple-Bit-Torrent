import threading
import time

lock = threading.Lock()

def print_thread():
    while True:
        lock.acquire()
        print("This is the printing thread.")
        lock.release()
        time.sleep(1)  # Tạm dừng một chút để nhường thời gian cho thread khác

def input_thread():
    while True:
        lock.acquire()
        user_input = input("Please enter a number: ")
        print(f"You entered: {user_input}")
        lock.release()

        time.sleep(1)

# Tạo thread
t1 = threading.Thread(target=print_thread)
t2 = threading.Thread(target=input_thread)

# Chạy thread
t1.start()
t2.start()

t1.join()
t2.join()
