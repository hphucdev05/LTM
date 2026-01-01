import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import core_logic

# Cấu hình giao diện
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FileTransferApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.client_core = core_logic.ClientCore()
        self.title("SecureShare - Nhóm 4")
        self.geometry("700x500")

        # --- FRAME 1: KẾT NỐI ---
        self.frame_connect = ctk.CTkFrame(self)
        self.frame_connect.pack(pady=10, fill="x", padx=10)

        self.entry_ip = ctk.CTkEntry(self.frame_connect, placeholder_text="IP Server (127.0.0.1)")
        self.entry_ip.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_ip.insert(0, "127.0.0.1")

        self.btn_connect = ctk.CTkButton(self.frame_connect, text="Kết nối", command=self.connect_server)
        self.btn_connect.pack(side="left", padx=5)

        # --- FRAME 2: CHỨC NĂNG ---
        self.frame_main = ctk.CTkFrame(self)
        self.frame_main.pack(expand=True, fill="both", padx=10, pady=5)

        # Listbox danh sách file (Dùng Textbox để giả lập vì ctk chưa có Listbox chuẩn)
        self.lbl_list = ctk.CTkLabel(self.frame_main, text="Danh sách File trên Server:")
        self.lbl_list.pack(anchor="w", padx=10)
        
        self.txt_files = ctk.CTkTextbox(self.frame_main, height=200)
        self.txt_files.pack(fill="x", padx=10, pady=5)
        self.txt_files.configure(state="disabled")

        self.btn_refresh = ctk.CTkButton(self.frame_main, text="Làm mới danh sách", command=self.refresh_list)
        self.btn_refresh.pack(pady=5)

        # Thanh tiến trình
        self.progress = ctk.CTkProgressBar(self.frame_main)
        self.progress.pack(fill="x", padx=10, pady=10)
        self.progress.set(0)

        # Nút Upload / Download
        self.frame_actions = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_actions.pack(fill="x", pady=10)

        self.btn_upload = ctk.CTkButton(self.frame_actions, text="Upload File", command=self.upload_action, fg_color="green")
        self.btn_upload.pack(side="left", padx=20, expand=True)

        self.btn_download = ctk.CTkButton(self.frame_actions, text="Download File (Nhập tên)", command=self.download_action)
        self.btn_download.pack(side="right", padx=20, expand=True)
        
        # Ô nhập tên file để download
        self.entry_filename = ctk.CTkEntry(self.frame_main, placeholder_text="Nhập tên file cần tải...")
        self.entry_filename.pack(pady=5)

    def log(self, message):
        print(message) 

    def connect_server(self):
        ip = self.entry_ip.get()
        port = 65432
        success, msg = self.client_core.connect_server(ip, port)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.client_core.login("UserGUI")
            self.refresh_list()
        else:
            messagebox.showerror("Lỗi", msg)

    def refresh_list(self):
        if not self.client_core.is_connected: return
        files = self.client_core.get_file_list()
        
        self.txt_files.configure(state="normal")
        self.txt_files.delete("1.0", "end")
        for f in files:
            self.txt_files.insert("end", f + "\n")
        self.txt_files.configure(state="disabled")

    def upload_action(self):
        if not self.client_core.is_connected:
            messagebox.showwarning("Cảnh báo", "Chưa kết nối Server!")
            return
            
        filepath = filedialog.askopenfilename()
        if filepath:
            # Chạy thread để không đơ giao diện
            threading.Thread(target=self.run_upload, args=(filepath,)).start()

    def run_upload(self, filepath):
        self.progress.set(0)
        res = self.client_core.upload_file(filepath, self.update_progress)
        messagebox.showinfo("Upload", res)
        self.refresh_list()

    def download_action(self):
        if not self.client_core.is_connected: return
        filename = self.entry_filename.get().strip()
        if not filename:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên file cần tải!")
            return
            
        save_dir = filedialog.askdirectory()
        if save_dir:
             threading.Thread(target=self.run_download, args=(filename, save_dir)).start()

    def run_download(self, filename, save_dir):
        self.progress.set(0)
        res = self.client_core.download_file(filename, save_dir, self.update_progress)
        messagebox.showinfo("Download", res)

    def update_progress(self, val):
        self.progress.set(val)

if __name__ == "__main__":
    app = FileTransferApp()
    app.mainloop()