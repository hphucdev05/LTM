import socket
import os
import sys

# Đảm bảo nhận diện được folder src để import protocol
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.common import protocol

def list_files(client_socket):
    """Lấy danh sách file từ server và parse đúng format"""
    try:
        client_socket.sendall(protocol.CMD_LIST.encode(protocol.FORMAT))
        data = client_socket.recv(4096).decode(protocol.FORMAT)
        
        if data == "EMPTY" or not data:
            return []
        
        # Server gửi: file1|1024|file2|2048|file3|512
        parts = data.split(protocol.SEPARATOR)
        file_list = []
        
        # Parse theo cặp (tên, size)
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):  # Đảm bảo có đủ cặp
                name = parts[i]
                try:
                    size = int(parts[i + 1])
                except ValueError:
                    size = 0  # Fallback nếu parse lỗi
                file_list.append((name, size))
        
        return file_list
    except Exception as e:
        print(f"❌ Lỗi list_files: {e}")
        return []
    
def upload_file(client_socket, filepath, progress_callback=None):
    """Upload file với progress tracking"""
    try:
        if not os.path.exists(filepath):
            return False, "File không tồn tại"

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        # 1. Gửi Header
        header = f"{protocol.CMD_UPLOAD}{protocol.SEPARATOR}{filename}{protocol.SEPARATOR}{filesize}"
        client_socket.sendall(header.encode(protocol.FORMAT))

        # 2. Chờ server xác nhận
        response = client_socket.recv(protocol.HEADER_SIZE).decode(protocol.FORMAT)
        if "READY" not in response:
            return False, "Server từ chối"

        # 3. Gửi dữ liệu với progress
        sent_bytes = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(protocol.CHUNK_SIZE)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                sent_bytes += len(chunk)
                
                # Gọi callback để update progress bar
                if progress_callback:
                    percent = (sent_bytes / filesize) * 100
                    progress_callback(percent)
                    print(f"📤 Upload: {percent:.1f}%", end='\r')
        
        print()  # Xuống dòng sau khi xong
        
        # 4. Nhận kết quả
        result = client_socket.recv(protocol.HEADER_SIZE).decode(protocol.FORMAT)
        return True, result
    except Exception as e:
        return False, f"Lỗi Upload: {e}"