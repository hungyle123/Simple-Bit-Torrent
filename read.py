# import hashlib
# import bencodepy

# def extract_hashes_from_torrent(torrent_file):
#     with open(torrent_file, 'rb') as f:
#         torrent_data = bencodepy.decode(f.read())
#         pieces = torrent_data[b'info'][b'pieces']
#         piece_length = torrent_data[b'info'][b'piece length']
#         print(pieces)
        
#         # Mỗi mã hash SHA-1 có độ dài 20 byte, chia chuỗi pieces thành từng mảnh mã hash
#         hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
#         return hashes, piece_length

# torrent_file = 'my_folder_output.torrent'
# hashes, piece_length = extract_hashes_from_torrent(torrent_file)
# print("Extracted Hashes:", [hash.hex() for hash in hashes])
# print("Extracted piece:", [piece_length])


import bencodepy
import pprint

def inspect_torrent_file(torrent_file):
    try:
        with open(torrent_file, 'rb') as f:
            # Đọc và giải mã nội dung file torrent
            torrent_data = bencodepy.decode(f.read())
            
            # In ra nội dung của file torrent với định dạng dễ nhìn
            pprint.pprint(torrent_data)
    
    except Exception as e:
        print("Error reading torrent file:", e)

# Kiểm tra file torrent
torrent_file = 'C:\\Users\\DELL\\Downloads\\btl_cn\\tracker\\naruto.txt.torrent'  # Thay thế bằng đường dẫn đến file torrent của bạn
inspect_torrent_file(torrent_file)