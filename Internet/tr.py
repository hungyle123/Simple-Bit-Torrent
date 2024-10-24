import os
import hashlib
import bencodepy

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

def create_torrent(input_path, tracker_url):
    """Tạo tệp torrent cho một file hoặc một thư mục."""
    files_info = []
    pieces = b""

    if os.path.isfile(input_path):  # Trường hợp input là một file
        file_hash = calculate_hash(input_path)
        file_length = os.path.getsize(input_path)

        files_info.append({
            'length': file_length,
            'path': [os.path.basename(input_path)]  # Lưu tên file
        })
        pieces += file_hash  # Hash của file

    else:  # Trường hợp input là một thư mục
        # Duyệt qua tất cả các tệp trong thư mục
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = calculate_hash(file_path)
                file_length = os.path.getsize(file_path)

                # Thêm thông tin tệp vào danh sách
                files_info.append({
                    'length': file_length,
                    'path': [os.path.relpath(file_path, input_path)]  # Lưu đường dẫn tương đối
                })

                # Thêm mã hash của tệp vào danh sách mã hash
                pieces += file_hash

    # Tạo cấu trúc tệp torrent
    torrent_data = {
        'announce': tracker_url,
        'info': {
            'files': files_info,
            'name': os.path.basename(input_path),
            'piece length': 262144,  # Kích thước mảnh (ví dụ: 256KB)
            'pieces': pieces,
        }
    }

    # Encode dữ liệu torrent
    encoded_torrent = bencodepy.encode(torrent_data)
    
    # Lưu tệp torrent vào thư mục hiện tại
    torrent_filename = f"{os.path.basename(input_path)}.torrent"
    with open(torrent_filename, 'wb') as torrent_file:
        torrent_file.write(encoded_torrent)
    
    print(f"Tệp torrent đã được lưu trữ với tên: {torrent_filename}")

# Sử dụng hàm
tracker_url = "udp://tracker.opentrackr.org:1337/announce"
input_path = "C:\\Users\\DELL\\Downloads\\btl_cn\\naruto.txt"  # Thay thế bằng file hoặc thư mục của bạn

create_torrent(input_path, tracker_url)
