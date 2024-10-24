pieces_data = b'\x07<d}Fx\xd5s\xdf\xf9\xec3];`\xee\x8a\xab\x93!' \
              b'\x12\xa5\xcf\xdfY\x94\xf4\xcedA{?\xe1\xae\xf2$:\xee~x' \
              b'"\x0e\xb05\xe0\x8b\x9c\x8dx\xc1\xa9&\xc6\xfd)E' \
              b"\x91\xa1_\xd0'\xab\xe4.\\^5\xabS\\!9\xefzjf^\x9fAQ" \
              b'\r\xa9Y\xebA\xee\xd81\xc4?\xec\xc7`\xbb$+f\xef\xd0\x1a' \
              b'\x10A\x17\x9c\xbd\xda6o\xd7\xb04\x7f\t%_wQp\xe1\x03' \
              b'X\x0e\\&x]+Yu\x8c\xd0\x7fi\x86\x18V\xa9\xe9a\x96' \
              b'\xfaj\xf6\xe9}\x01\n\x98\xb5\xbf\xb9\xdc\x17\x86!\x12' \
              b'\xaf\xda@.'

# Độ dài của mỗi mã hash (SHA-1)
hash_length = 20

# Số lượng mã hash
num_hashes = len(pieces_data) // hash_length

print(f'Tổng số mã hash trong pieces: {num_hashes}')

import hashlib

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

print(calculate_hash('C:\\Users\\DELL\\Downloads\\btl_cn\\my_folder_2\\naruto.txt'))