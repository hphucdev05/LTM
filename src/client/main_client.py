import socket
import os
import sys

# Fix đường dẫn tuyệt đối
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.common import protocol
from src.client import core_logic

# Thư mục chứa file tải về
DOWNLOAD_DIR = os.path.join(current_dir, 'downloads')
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("⏳ Đang kết nối tới server...")
        client.connect((protocol.HOST, protocol.PORT))
        print("✅ Kết nối thành công!\n")

        while True:
            print(f"\n{'='*10} SECURE SHARE MENU {'='*10}")
            print("1. Xem danh sách file (List)")
            print("2. Upload file")
            print("3. Download file (Có Resume)")
            print("4. Thoát")
            choice = input("👉 Chọn chức năng (1-4): ")

            if choice == "1":
                files = core_logic.list_files(client)
                print("\n--- FILE TRÊN SERVER ---")
                if not files: print("(Trống)")
                else:
                    print(f"{'Tên file'.ljust(30)} | {'Kích thước'.rjust(15)}")
                    print("-" * 50)
                    for name, size in files:
                        size_str = f"{size/(1024**3):.2f} GB" if size > 1024**3 else f"{size/(1024**2):.2f} MB"
                        print(f"{name.ljust(30)} | {size_str.rjust(15)}")

            elif choice == "2":
                path = input("📂 Nhập đường dẫn file cần Upload: ").strip().replace('"', '')
                if os.path.isfile(path):
                    print("🚀 Đang upload...")
                    success, msg = core_logic.upload_file(client, path)
                    print(f"Kết quả: {msg}")
                else:
                    print("❌ File không tồn tại!")

            elif choice == "3":
                fname = input("📥 Nhập tên file muốn tải (copy từ danh sách): ").strip()
                if fname:
                    print(f"🚀 Đang tải về thư mục: {DOWNLOAD_DIR}")
                    success, msg = core_logic.download_file(client, fname, DOWNLOAD_DIR)
                    print(f"Kết quả: {msg}")
                else:
                    print("❌ Tên file không được để trống")

            elif choice == "4":
                print("👋 Tạm biệt!")
                break
            else:
                print("❌ Sai cú pháp, chọn lại!")

    except Exception as e:
        print(f"\n❌ Lỗi Client: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()