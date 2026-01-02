import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import time

# Fix path để nhận diện folder src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.common import protocol
from src.client import core_logic

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SecureShareGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecureShare Enterprise - Nhóm 4")
        self.geometry("800x550")
        
        self.client_socket = None

        # --- GIAO DIỆN KẾT NỐI ---
        self.conn_frame = ctk.CTkFrame(self)
        self.conn_frame.pack(pady=10, padx=10, fill="x")
        
        self.ip_entry = ctk.CTkEntry(self.conn_frame, placeholder_text="Server IP (127.0.0.1)")
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        self.conn_btn = ctk.CTkButton(self.conn_frame, text="KẾT NỐI", command=self.connect, fg_color="#1f538d")
        self.conn_btn.pack(side="left", padx=10)

        # --- KHU VỰC DANH SÁCH FILE ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.label_list = ctk.CTkLabel(self.main_frame, text="DANH SÁCH FILE TRÊN SERVER", font=("Roboto", 16, "bold"))
        self.label_list.pack(pady=5)
        
        self.file_listbox = ctk.CTkTextbox(self.main_frame, height=200)
        self.file_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.file_listbox.configure(state="disabled")

        self.refresh_btn = ctk.CTkButton(self.main_frame, text="LÀM MỚI DANH SÁCH", command=self.refresh_files)
        self.refresh_btn.pack(pady=5)

        # --- THANH TIẾN TRÌNH (PROGRESS) ---
        self.progress_label = ctk.CTkLabel(self.main_frame, text="Trạng thái: Sẵn sàng")
        self.progress_label.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_bar.set(0)

        # --- NÚT ĐIỀU KHIỂN ---
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10, padx=10, fill="x")
        
        self.upload_btn = ctk.CTkButton(self.btn_frame, text="UPLOAD FILE", fg_color="#28a745", command=self.start_upload)
        self.upload_btn.pack(side="left", padx=20, pady=10, expand=True)
        
        self.download_btn = ctk.CTkButton(self.btn_frame, text="DOWNLOAD FILE", fg_color="#fd7e14", command=self.start_download)
        self.download_btn.pack(side="left", padx=20, pady=10, expand=True)

    def connect(self):
        try:
            import socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip_entry.get(), protocol.PORT))
            messagebox.showinfo("Thành công", "Đã kết nối tới Server!")
            self.refresh_files()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối: {e}")

    def refresh_files(self):
        if not self.client_socket: return
        files = core_logic.list_files(self.client_socket)
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for name, size in files:
            self.file_listbox.insert("end", f"📄 {name} ({int(size)/(1024*1024):.2f} MB)\n")
        self.file_listbox.configure(state="disabled")

    def start_upload(self):
        path = filedialog.askopenfilename()
        if path:
            # Chạy thread riêng để không treo UI
            threading.Thread(target=self.upload_thread, args=(path,), daemon=True).start()

    def upload_thread(self, path):
        self.upload_btn.configure(state="disabled")
        # Logic gửi file (tôi sẽ chỉnh lại core_logic một chút để trả về tiến độ cho UI)
        success, msg = core_logic.upload_file_gui(self.client_socket, path, self.update_progress)
        self.upload_btn.configure(state="normal")
        messagebox.showinfo("Kết quả", msg)
        self.refresh_files()

    def start_download(self):
        # Hiện popup nhập tên file
        dialog = ctk.CTkInputDialog(text="Nhập tên file chính xác trên server:", title="Download")
        filename = dialog.get_input()
        if filename:
            save_dir = filedialog.askdirectory()
            if save_dir:
                threading.Thread(target=self.download_thread, args=(filename, save_dir), daemon=True).start()

    def download_thread(self, filename, save_dir):
        self.download_btn.configure(state="disabled")
        success, msg = core_logic.download_file_gui(self.client_socket, filename, save_dir, self.update_progress)
        self.download_btn.configure(state="normal")
        messagebox.showinfo("Kết quả", msg)

    def update_progress(self, percent, speed, current_mb, total_mb):
        self.progress_bar.set(percent / 100)
        self.progress_label.configure(text=f"Đang xử lý: {percent:.1f}% | {speed:.2f} MB/s | {current_mb:.1f}/{total_mb:.1f} MB")

if __name__ == "__main__":
    app = SecureShareGUI()
    app.mainloop()