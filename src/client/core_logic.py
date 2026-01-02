import socket
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.common import protocol

def print_progress_bar(received, total, start_time):
    """Hàm vẽ thanh tiến trình đẹp mắt"""
    percent = (received / total) * 100
    elapsed = time.time() - start_time
    speed = (received / (1024*1024)) / elapsed if elapsed > 0 else 0
    
    # Đổi đơn vị sang GB nếu lớn hơn 1GB
    if total > 1024**3:
        curr_str = f"{received/(1024**3):.2f}"
        total_str = f"{total/(1024**3):.2f} GB"
    else:
        curr_str = f"{received/(1024**2):.1f}"
        total_str = f"{total/(1024**2):.1f} MB"

    bar_len = 30
    filled = int(bar_len * received // total)
    bar = '█' * filled + '-' * (bar_len - filled)
    
    sys.stdout.write(f"\r   [{bar}] {percent:.1f}% | {curr_str}/{total_str} | {speed:.2f} MB/s")
    sys.stdout.flush()

def list_files(client_socket):
    try:
        client_socket.sendall(protocol.CMD_LIST.encode(protocol.FORMAT))
        data = client_socket.recv(4096).decode(protocol.FORMAT)
        if not data or data == "EMPTY": return []
        
        parts = data.split(protocol.SEPARATOR)
        file_list = []
        for i in range(0, len(parts), 2):
            if i+1 < len(parts):
                file_list.append((parts[i], int(parts[i+1])))
        return file_list
    except: return []

def upload_file(client_socket, filepath):
    if not os.path.exists(filepath): return False, "File không tồn tại"
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    
    header = f"{protocol.CMD_UPLOAD}{protocol.SEPARATOR}{filename}{protocol.SEPARATOR}{filesize}"
    client_socket.sendall(header.encode(protocol.FORMAT))
    
    if "READY" not in client_socket.recv(1024).decode(protocol.FORMAT):
        return False, "Server từ chối"

    start_time = time.time()
    sent = 0
    with open(filepath, "rb") as f:
        while sent < filesize:
            chunk = f.read(protocol.CHUNK_SIZE)
            if not chunk: break
            client_socket.sendall(chunk)
            sent += len(chunk)
            print_progress_bar(sent, filesize, start_time)
            
    print() # Xuống dòng
    return True, client_socket.recv(1024).decode(protocol.FORMAT)

def download_file(client_socket, filename, save_dir):
    save_path = os.path.join(save_dir, filename)
    offset = 0
    
    # Tự động phát hiện Resume
    if os.path.exists(save_path):
        offset = os.path.getsize(save_path)
        print(f"⚠️ Phát hiện file tải dở ({offset} bytes). Đang yêu cầu Resume...")

    # Gửi lệnh kèm offset
    msg = f"{protocol.CMD_DOWNLOAD}{protocol.SEPARATOR}{filename}{protocol.SEPARATOR}{offset}"
    client_socket.sendall(msg.encode(protocol.FORMAT))

    response = client_socket.recv(1024).decode(protocol.FORMAT)
    
    # Xử lý phản hồi OK|filesize
    if "OK" not in response:
        return False, f"Lỗi từ server: {response}"
        
    try:
        total_size = int(response.split(protocol.SEPARATOR)[1])
    except:
        return False, "Lỗi format kích thước file"

    client_socket.send("READY".encode(protocol.FORMAT))

    mode = 'ab' if offset > 0 else 'wb' # Append nếu resume
    received = offset
    start_time = time.time()

    with open(save_path, mode) as f:
        while received < total_size:
            chunk = client_socket.recv(protocol.CHUNK_SIZE)
            if not chunk: break
            f.write(chunk)
            received += len(chunk)
            print_progress_bar(received, total_size, start_time)

    print()
    return True, "Download hoàn tất!"