import socket
import os
import sys

# BƯỚC 1: FIX PATH TRƯỚC (Phải đặt ở đầu tiên, trước các dòng import module dự án)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# BƯỚC 2: IMPORT CÁC MODULE TRONG DỰ ÁN (Dùng đường dẫn đầy đủ từ src)
from src.common import protocol
from src.client.core_logic import list_files, upload_file

# Lấy thông tin từ file protocol để đồng bộ với Server
HOST = protocol.HOST 
PORT = protocol.PORT

def main():
    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("✅ Đã kết nối tới server!\n")

        # 1. LIST FILE TRƯỚC
        files = list_files(client_socket)
        print("Danh sách file trên server (trước upload):")
        if not files:
            print("   → Chưa có file nào\n")
        else:
            print(f"{'Tên file'.ljust(35)} | Kích thước")
            print("-" * 50)
            for name, size in files:
                print(f"{name.ljust(35)} | {int(size):,} bytes")

        # 2. UPLOAD FILE
        print("\n=== BẮT ĐẦU UPLOAD ===")
        # Đường dẫn file test của bạn
        test_file = r"C:\Users\ASUS\Pictures\z7320949673374_10137dfeb1559233e7590df54a7748ed.jpg"

        if not os.path.exists(test_file):
            print(f"❌ Không tìm thấy file tại: {test_file}")
            print("Vui lòng kiểm tra lại đường dẫn file trong main_client.py")
        else:
            success, msg = upload_file(client_socket, test_file)
            print(f"Kết quả: {msg}")

        # 3. REFRESH DANH SÁCH SAU KHI UPLOAD
        print("\n🔄 Đang refresh danh sách...")
        files_after = list_files(client_socket)
        print("Danh sách file trên server (sau upload):")
        if not files_after:
            print("   → Vẫn chưa có file nào")
        else:
            print(f"{'Tên file'.ljust(35)} | Kích thước")
            print("-" * 50)
            for name, size in files_after:
                print(f"{name.ljust(35)} | {int(size):,} bytes")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if client_socket:
            client_socket.close()
        input("\nNhấn Enter để thoát...")

if __name__ == "__main__":
    main()