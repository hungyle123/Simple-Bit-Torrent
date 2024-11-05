# import bencodepy

# def extract_pieces_from_torrent(torrent_file):
#     # Đọc file torrent
#     with open(torrent_file, 'rb') as f:
#         torrent_data = f.read()
    
#     # Giải mã nội dung file torrent
#     decoded_data = bencodepy.decode(torrent_data)
    
#     # Truy xuất trường pieces
#     pieces_data = decoded_data[b'info'][b'pieces']
    
#     return pieces_data

# def print_hashes(pieces_data):
#     # Kích thước của từng mã hash
#     hash_length = 20

#     # Kích thước của pieces
#     pieces_size = len(pieces_data)

#     # Tính số lượng mã hash
#     num_hashes = pieces_size // hash_length

#     print(f'Tổng số mã hash trong pieces: {num_hashes}')
#     print(f'Kích thước của pieces: {pieces_size} bytes')

#     # In ra từng dòng mã hash
#     for i in range(num_hashes):
#         start_index = i * hash_length
#         end_index = start_index + hash_length
#         hash_value = pieces_data[start_index:end_index]
#         print(f'Mã hash {i + 1}: {hash_value}')  # Chuyển đổi thành chuỗi hex để dễ đọc

# # Đường dẫn tới file torrent của bạn
# torrent_file = 'naruto.torrent'  # Thay thế bằng đường dẫn thực tế

# # Trích xuất và in ra mã hash từ file torrent
# pieces_data = extract_pieces_from_torrent(torrent_file)
# print_hashes(pieces_data)

import tkinter as tk

root = tk.Tk()
root.title("Color Options in Tkinter")

# Create a button with active background and foreground colors
button = tk.Button(root, text="Click Me", activebackground="blue", activeforeground="white")
button.pack()

# Create a label with background and foreground colors
label = tk.Label(root, text="Hello, Tkinter!", bg="red", fg="green")
label.pack()

# Create an Entry widget with selection colors
entry = tk.Entry(root, selectbackground="lightblue", selectforeground="black", fg="green")
entry.pack()

root.mainloop()

