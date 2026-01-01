# src/server/client_handler.py
import os
from common.protocol import *

STORAGE_DIR = "server_storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

def handle_client(conn, addr):
    print(f"[SERVER] Client {addr} đã kết nối")

    current_file = None
    expected_size = 0
    received_bytes = 0
    current_filename = None

    try:
        while True:
            if current_file is not None:
                # Nhận binary chunk
                remaining = expected_size - received_bytes
                if remaining <= 0:
                    continue

                chunk_size = min(CHUNK_SIZE, remaining)
                chunk = conn.recv(chunk_size)
                if not chunk:
                    raise Exception("Client ngắt giữa upload")

                current_file.write(chunk)
                received_bytes += len(chunk)
                print(f"[SERVER] Đã nhận {received_bytes:,}/{expected_size:,} bytes của {current_filename}")

                if received_bytes >= expected_size:
                    current_file.close()
                    conn.sendall(b"SUCCESS\n")
                    print(f"[SERVER] UPLOAD HOÀN TẤT: {current_filename}")
                    current_file = None
                    expected_size = 0
                    received_bytes = 0
                    current_filename = None

            else:
                # Nhận command text
                data = conn.recv(1024).decode(FORMAT)
                if not data:
                    break

                commands = data.strip().split(COMMAND_SEPARATOR)
                for cmd in commands:
                    cmd = cmd.strip()
                    print(f"[SERVER] Lệnh nhận được: '{cmd}'")

                    if cmd == CMD_LIST:
                        files = [f for f in os.listdir(STORAGE_DIR) if not f.startswith('.')]
                        file_info = []
                        for f in files:
                            path = os.path.join(STORAGE_DIR, f)
                            if os.path.isfile(path):
                                size = os.path.getsize(path)
                                file_info.append(f"{f}{SEPARATOR}{size}")
                        response = "\n".join(file_info) + "\nDONE\n" if file_info else "EMPTY\nDONE\n"
                        conn.sendall(response.encode(FORMAT))

                    elif cmd.startswith(CMD_UPLOAD):
                        parts = cmd.split(" ", 2)
                        if len(parts) != 3:
                            conn.sendall(b"ERROR Invalid UPLOAD command\n")
                            continue

                        _, filename, size_str = parts
                        try:
                            expected_size = int(size_str)
                        except ValueError:
                            conn.sendall(b"ERROR Invalid file size\n")
                            continue

                        file_path = os.path.join(STORAGE_DIR, filename)
                        if os.path.exists(file_path):
                            conn.sendall(b"ERROR File already exists\n")
                            continue

                        current_file = open(file_path, "wb")
                        current_filename = filename
                        received_bytes = 0
                        conn.sendall(b"READY\n")
                        print(f"[SERVER] Sẵn sàng nhận file: {filename} ({expected_size:,} bytes)")

    except Exception as e:
        print(f"[SERVER] Lỗi với client {addr}: {e}")
    finally:
        if current_file:
            current_file.close()
            print("[SERVER] Đóng file dở")
        conn.close()
        print(f"[SERVER] Client {addr} ngắt kết nối")