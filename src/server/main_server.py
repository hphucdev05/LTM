import socket
import threading
import os
import sys

# Import protocol
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import protocol

# Đường dẫn lưu file
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'server_storage')
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    try:
        while True:
            # Nhận lệnh (Header)
            msg = conn.recv(protocol.HEADER_SIZE).decode(protocol.FORMAT).strip()
            if not msg:
                break

            cmd_parts = msg.split(protocol.SEPARATOR)
            command = cmd_parts[0]

            if command == protocol.CMD_LOGIN:
                conn.send("LOGIN_OK".encode(protocol.FORMAT))

            elif command == protocol.CMD_LIST:
                # Gửi danh sách file KÈM KÍCH THƯỚC
                files = os.listdir(STORAGE_DIR)
                response_parts = []
                
                for f in files:
                    filepath = os.path.join(STORAGE_DIR, f)
                    # Chỉ lấy file, bỏ qua thư mục
                    if os.path.isfile(filepath):
                        size = os.path.getsize(filepath)
                        # Định dạng: tên|size|tên|size|...
                        response_parts.append(f"{f}{protocol.SEPARATOR}{size}")
                
                if response_parts:
                    # Nối tất cả lại: file1|1024|file2|2048
                    files_str = protocol.SEPARATOR.join(response_parts)
                else:
                    files_str = "EMPTY"
                
                conn.send(files_str.encode(protocol.FORMAT))

            elif command == protocol.CMD_UPLOAD:
                # Cấu trúc: UPLOAD|filename|filesize
                filename = os.path.basename(cmd_parts[1])
                filesize = int(cmd_parts[2])
                
                conn.send("READY_TO_RECEIVE".encode(protocol.FORMAT))
                
                # Nhận và ghi file
                filepath = os.path.join(STORAGE_DIR, filename)
                with open(filepath, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = conn.recv(protocol.CHUNK_SIZE)
                        if not chunk: break
                        f.write(chunk)
                        bytes_received += len(chunk)
                
                print(f"[UPLOAD] Đã nhận file: {filename}")
                conn.send("UPLOAD_SUCCESS".encode(protocol.FORMAT))
            # Sửa file server/main_server.py - Thêm xử lý Resume
            elif command == protocol.CMD_DOWNLOAD:
                filename = cmd_parts[1]
                offset = int(cmd_parts[2]) if len(cmd_parts) > 2 else 0  # ← THÊM DÒNG NÀY
                
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.exists(filepath):
                    full_size = os.path.getsize(filepath)
                    conn.send(f"OK{protocol.SEPARATOR}{full_size}".encode(protocol.FORMAT))
                    conn.recv(1024)
                    
                    with open(filepath, 'rb') as f:
                        f.seek(offset)  # ← THÊM DÒNG NÀY - QUAN TRỌNG NHẤT
                        while (chunk := f.read(protocol.CHUNK_SIZE)):
                            conn.sendall(chunk)
            elif command == protocol.CMD_DOWNLOAD:
                # Cấu trúc: DOWNLOAD|filename
                filename = os.path.basename(cmd_parts[1])
                filepath = os.path.join(STORAGE_DIR, filename)

                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    # Gửi header báo OK: OK|filesize
                    header = f"OK{protocol.SEPARATOR}{filesize}"
                    conn.send(header.encode(protocol.FORMAT))
                    
                    # Đợi Client sẵn sàng
                    conn.recv(1024) 

                    # Gửi nội dung file
                    with open(filepath, 'rb') as f:
                        while (chunk := f.read(protocol.CHUNK_SIZE)):
                            conn.sendall(chunk)
                    print(f"[DOWNLOAD] Đã gửi file: {filename}")
                else:
                    conn.send("FILE_NOT_FOUND".encode(protocol.FORMAT))

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((protocol.HOST, protocol.PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening on {protocol.HOST}:{protocol.PORT}")
    print(f"[STORAGE] File saving at: {STORAGE_DIR}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()