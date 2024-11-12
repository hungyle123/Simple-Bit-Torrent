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
from typing import Dict, List, Set
import os

file_name: Dict[bytes, Dict[int, Set]] = {}

def inspect_torrent_file(torrent_file):
    try:
        with open(torrent_file, 'rb') as f:
            # Đọc và giải mã nội dung file torrent
            #torrent_data = bencodepy.decode(f.read())
            var_torrent = bencodepy.decode(f.read())
            
            # pieces = torrent_data[b'info'][b'files'][0]
            # # In ra nội dung của file torrent với định dạng dễ nhìn
            pprint.pprint(var_torrent)
            # #print(type(pieces))
            print(var_torrent[b'info'][b'files'][0][b'path'].decode('utf-8'))
            ip_port_addr = ('94:2004',2345)
            
            pieces = var_torrent[b'info'][b'pieces']

            pieces_hash = [pieces[i:i+20] for i in range(0,len(pieces),20)]

            file_info = var_torrent[b'info'][b'files']

            # for i,file in enumerate(file_info):
            #     file_size = file[b'length']
            
            #     part_size = 512 * 1024
            #     num_part = (file_size + part_size - 1) // part_size

            #     if pieces_hash[i] not in file_name:
            #         file_name[pieces_hash[i]] = {}

            #     for index in range(num_part):
            #         if index not in file_name[pieces_hash[i]]:
            #             file_name[pieces_hash[i]][index] = set()

            #         if ip_port_addr not in file_name[pieces_hash[i]][index]:
            #             file_name[pieces_hash[i]][index].add(ip_port_addr)

            # pprint.pprint(file_name)
    except Exception as e:
        print("Error reading torrent file:", e)

# Kiểm tra file torrent

torrent_name = 'my_folder_2'
path_name = 'my_folder_2.torrent'

th = os.path.join(torrent_name,path_name)
torrent_file = 'C:\\Users\\DELL\\Downloads\\btl_cn\\xs.txt.torrent'  # Thay thế bằng đường dẫn đến file torrent của bạn
inspect_torrent_file(torrent_file)