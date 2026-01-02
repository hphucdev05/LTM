import socket
import threading
import os
import sys

# Fix lỗi import
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.common import protocol

# Tạo thư mục lưu file server
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'server_storage')
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            msg = conn.recv(protocol.HEADER_SIZE).decode(protocol.FORMAT).strip()
            if not msg: break

            cmd_parts = msg.split(protocol.SEPARATOR)
            command = cmd_parts[0]

            if command == protocol.CMD_LIST:
                files = os.listdir(STORAGE_DIR)
                # Gửi về dạng: file1|size1|file2|size2
                response_parts = []
                for f in files:
                    path = os.path.join(STORAGE_DIR, f)
                    if os.path.isfile(path):
                        response_parts.append(f)
                        response_parts.append(str(os.path.getsize(path)))
                
                data = protocol.SEPARATOR.join(response_parts) if response_parts else "EMPTY"
                conn.send(data.encode(protocol.FORMAT))

            elif command == protocol.CMD_UPLOAD:
                # CMD: UPLOAD|filename|filesize
                filename = os.path.basename(cmd_parts[1])
                filesize = int(cmd_parts[2])
                
                conn.send("READY".encode(protocol.FORMAT))
                
                filepath = os.path.join(STORAGE_DIR, filename)
                with open(filepath, 'wb') as f:
                    received = 0
                    while received < filesize:
                        # Nhận tối đa CHUNK hoặc phần còn thiếu
                        chunk = conn.recv(min(protocol.CHUNK_SIZE, filesize - received))
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)
                
                conn.send("UPLOAD_SUCCESS".encode(protocol.FORMAT))
                print(f"[UPLOAD] {filename} hoàn tất.")

            elif command == protocol.CMD_DOWNLOAD:
                # CMD: DOWNLOAD|filename|offset
                filename = os.path.basename(cmd_parts[1])
                offset = int(cmd_parts[2]) if len(cmd_parts) > 2 else 0
                
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    # Gửi phản hồi: OK|filesize
                    conn.send(f"OK{protocol.SEPARATOR}{filesize}".encode(protocol.FORMAT))
                    
                    conn.recv(1024) # Đợi Client báo READY

                    with open(filepath, 'rb') as f:
                        f.seek(offset) # 🎯 QUAN TRỌNG: Nhảy đến vị trí tải dở
                        while True:
                            chunk = f.read(protocol.CHUNK_SIZE)
                            if not chunk: break
                            conn.sendall(chunk)
                    print(f"[DOWNLOAD] Đã gửi {filename} từ byte {offset}.")
                else:
                    conn.send("ERROR|File not found".encode(protocol.FORMAT))

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((protocol.HOST, protocol.PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening on {protocol.HOST}:{protocol.PORT}")
    print(f"[STORAGE] {STORAGE_DIR}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()