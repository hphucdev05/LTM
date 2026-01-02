import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import socket
from core_logic import list_files, upload_file_gui, download_file_gui
# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.common import protocol
from src.client import core_logic

# --- CẤU HÌNH GIAO DIỆN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#1a1a1a"       # Màu nền tối
COLOR_ACCENT = "#3B8ED0"   # Màu xanh chủ đạo
COLOR_HOVER = "#2B2B2B"    # Màu khi di chuột
COLOR_SELECTED = "#1f538d" # Màu khi chọn file

class SecureShareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SecureShare Enterprise - Nhóm 4")
        self.geometry("1000x650")
        
        self.client_socket = None
        self.is_connected = False
        self.selected_filename = None  # Biến lưu tên file đang chọn
        self.file_buttons = {}         # Dictionary lưu các nút để quản lý highlight

        # --- LAYOUT CHÍNH ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Phần danh sách giãn tối đa

        # 1. HEADER & KẾT NỐI
        self.draw_header()

        # 2. KHUNG DANH SÁCH FILE (Table View)
        self.draw_file_list_area()

        # 3. KHUNG TIẾN TRÌNH & TRẠNG THÁI
        self.draw_progress_area()

        # 4. FOOTER (NÚT CHỨC NĂNG)
        self.draw_footer()

    def draw_header(self):
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#111111")
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Logo text
        ctk.CTkLabel(header_frame, text="🚀 SECURE SHARE", font=("Segoe UI", 20, "bold"), text_color="white").pack(side="left", padx=20)
        
        # Connection Area
        self.btn_connect = ctk.CTkButton(header_frame, text="Kết nối Server", command=self.connect_server, 
                                         fg_color="#28a745", hover_color="#218838", width=120)
        self.btn_connect.pack(side="right", padx=20, pady=10)
        
        self.entry_ip = ctk.CTkEntry(header_frame, placeholder_text="127.0.0.1", width=150)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack(side="right", padx=5)

    def draw_file_list_area(self):
        # Frame chứa tiêu đề cột
        title_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        title_frame.grid(row=1, column=0, sticky="new", padx=20, pady=(20, 0))
        
        ctk.CTkLabel(title_frame, text="TÊN FILE", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=10)
        ctk.CTkLabel(title_frame, text="KÍCH THƯỚC", font=("Arial", 12, "bold"), text_color="gray").pack(side="right", padx=30)

        # Scrollable Frame (Danh sách cuộn)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#212121", corner_radius=10)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=40, pady=5)

        # Thông báo trống
        self.lbl_empty = ctk.CTkLabel(self.scroll_frame, text="Chưa kết nối hoặc Server trống", text_color="gray")
        self.lbl_empty.pack(pady=20)

    def draw_progress_area(self):
        self.progress_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        
        # Thông tin tốc độ
        self.lbl_status = ctk.CTkLabel(self.progress_frame, text="Ready", font=("Consolas", 12), text_color="#aaaaaa")
        self.lbl_status.pack(anchor="w")
        
        # Thanh Bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=15)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)

    def draw_footer(self):
        footer_frame = ctk.CTkFrame(self, height=80, fg_color="#111111", corner_radius=0)
        footer_frame.grid(row=4, column=0, sticky="ew")

        # Nút Làm mới (Nhỏ)
        self.btn_refresh = ctk.CTkButton(footer_frame, text="🔄 Refresh", width=100, fg_color="#444", command=self.refresh_list)
        self.btn_refresh.pack(side="left", padx=20, pady=20)

        # Nút Download (To)
        self.btn_download = ctk.CTkButton(footer_frame, text="⬇ DOWNLOAD SELECTED", command=self.start_download,
                                          font=("Arial", 14, "bold"), height=40, width=200, 
                                          fg_color="#e67e22", hover_color="#d35400", state="disabled")
        self.btn_download.pack(side="right", padx=20)

        # Nút Upload (To)
        self.btn_upload = ctk.CTkButton(footer_frame, text="⬆ UPLOAD NEW FILE", command=self.start_upload,
                                        font=("Arial", 14, "bold"), height=40, width=200)
        self.btn_upload.pack(side="right", padx=10)

    # --- LOGIC XỬ LÝ ---

    def connect_server(self):
        ip = self.entry_ip.get()
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, protocol.PORT))
            self.is_connected = True
            
            self.btn_connect.configure(state="disabled", text="Connected", fg_color="#1e7e34")
            self.refresh_list()
            messagebox.showinfo("Thành công", "Đã kết nối máy chủ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối: {e}")

    def get_file_icon(self, filename):
        """Trả về emoji dựa trên đuôi file"""
        ext = filename.split('.')[-1].lower()
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']: return "🖼️"
        if ext in ['mp4', 'mkv', 'avi', 'mov']: return "🎥"
        if ext in ['mp3', 'wav', 'flac']: return "🎵"
        if ext in ['pdf', 'doc', 'docx', 'txt']: return "📄"
        if ext in ['zip', 'rar', 'iso', '7z']: return "📦"
        if ext in ['py', 'cpp', 'html', 'js']: return "💻"
        return "📝"

    def format_size(self, size):
        if size > 1024**3: return f"{size/(1024**3):.2f} GB"
        return f"{size/(1024**2):.2f} MB"

    def refresh_list(self):
        if not self.is_connected: 
            return

        # Xóa cũ
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.file_buttons = {} 
        self.selected_filename = None
        self.btn_download.configure(state="disabled", text="⬇ DOWNLOAD SELECTED")

        try:
            files = core_logic.list_files(self.client_socket)
        except Exception as e:
            messagebox.showerror("Lỗi", "Không lấy được danh sách")
            return

        if not files:
            lbl = ctk.CTkLabel(self.scroll_frame, text="📂 Chưa có file nào trên Server", text_color="gray", font=("Arial", 16))
            lbl.pack(expand=True)  # Căn giữa khi trống
            return

        # Cấu hình scroll_frame giãn full
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        for index, (name, size_str) in enumerate(files):
            size = int(size_str)
            icon = self.get_file_icon(name)
            size_text = self.format_size(size)

            # Frame mỗi dòng - full width
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=50)
            row_frame.grid(row=index, column=0, sticky="ew", pady=3, padx=10)
            row_frame.grid_columnconfigure(0, weight=1)  # Tên file giãn hết

            # Nút tên file (chiếm hết bên trái)
            btn = ctk.CTkButton(
                row_frame,
                text=f"{icon}  {name}",
                anchor="w",
                font=("Segoe UI", 14),
                fg_color="transparent",
                text_color="white",
                hover_color=COLOR_HOVER,
                height=50,
                command=lambda f=name: self.on_file_select(f)
            )
            btn.grid(row=0, column=0, sticky="ew", padx=(15, 0))

            # Label size (căn phải)
            lbl_size = ctk.CTkLabel(
                row_frame,
                text=size_text,
                text_color="#4FC3F7",
                font=("Consolas", 14, "bold"),
                width=150,
                anchor="e"
            )
            lbl_size.grid(row=0, column=1, sticky="e", padx=(0, 30))

            self.file_buttons[name] = btn

        # Highlight lại file đang chọn
        if self.selected_filename and self.selected_filename in self.file_buttons:
            self.file_buttons[self.selected_filename].configure(fg_color=COLOR_SELECTED)
            self.btn_download.configure(state="normal", text=f"⬇ TẢI: {self.selected_filename}")  
    def on_file_select(self, filename):
        """Xử lý khi người dùng Click vào một file"""
        # 1. Reset màu các nút cũ
        if self.selected_filename and self.selected_filename in self.file_buttons:
            self.file_buttons[self.selected_filename].configure(fg_color="transparent")
        
        # 2. Highlight nút mới chọn
        self.selected_filename = filename
        self.file_buttons[filename].configure(fg_color=COLOR_SELECTED)

        # 3. Mở khóa nút Download
        self.btn_download.configure(state="normal", text=f"⬇ TẢI: {filename}")

    # --- UPLOAD & DOWNLOAD LOGIC ---

    def update_ui_progress(self, percent, speed, curr, total):
        self.progress_bar.set(percent)
        self.lbl_status.configure(text=f"🚀 Đang xử lý: {percent*100:.1f}% | ⚡ {speed:.2f} MB/s | 💾 {curr:.1f}/{total:.1f} MB")
        self.update_idletasks()

    def start_upload(self):
        if not self.is_connected: 
            messagebox.showwarning("!", "Chưa kết nối Server")
            return
        path = filedialog.askopenfilename()
        if path:
            threading.Thread(target=self.run_upload, args=(path,), daemon=True).start()

    def run_upload(self, path):
        self.btn_upload.configure(state="disabled")
        success, msg = core_logic.upload_file_gui(self.client_socket, path, self.update_ui_progress)
        self.btn_upload.configure(state="normal")
        if success:
            self.refresh_list()
            messagebox.showinfo("Xong", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    def start_download(self):
        if not self.selected_filename: return # Không cần nhập tay nữa!
        
        save_dir = filedialog.askdirectory()
        if save_dir:
            threading.Thread(target=self.run_download, args=(self.selected_filename, save_dir), daemon=True).start()

    def run_download(self, filename, save_dir):
        self.btn_download.configure(state="disabled")
        success, msg = core_logic.download_file_gui(self.client_socket, filename, save_dir, self.update_ui_progress)
        self.btn_download.configure(state="normal")
        if success:
            messagebox.showinfo("Xong", msg)
        else:
            messagebox.showerror("Lỗi", msg)

if __name__ == "__main__":
    app = SecureShareApp()
    app.mainloop()