# 🚀 SecureShare Enterprise - Hệ thống Truyền tải File Tập trung

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Socket](https://img.shields.io/badge/Network-Socket_TCP-green)
![Status](https://img.shields.io/badge/Status-Development-orange)

> **Đồ án môn học:** Lập trình mạng (Network Programming)  
> **Giảng viên hướng dẫn:** [Bùi Dương Thế]  
> **Nhóm thực hiện:** Nhóm [1]

---

## 📖 Giới thiệu
**SecureShare Enterprise** là giải pháp phần mềm client-server được thiết kế để giải quyết bài toán truyền tải dữ liệu nội bộ trong doanh nghiệp. Hệ thống cho phép người dùng upload và download các tệp tin kích thước lớn với độ ổn định cao, hỗ trợ tính năng **Pause/Resume** (Tạm dừng/Tiếp tục) khi đường truyền mạng không ổn định.

Sản phẩm được xây dựng hoàn toàn bằng **Python Socket**, tuân thủ nghiêm ngặt các nguyên lý lập trình mạng, đa luồng (Multi-threading) và xử lý Binary Stream.

---

## ✨ Tính năng nổi bật

* **📡 Kiến trúc Client - Server Đa luồng:** Server có khả năng xử lý đồng thời nhiều Client kết nối cùng lúc mà không bị tắc nghẽn.
* **📂 Quản lý File tập trung:** Client có thể xem danh sách file hiện có trên Server theo thời gian thực.
* **upload/Download Multi-thread:** Tối ưu hóa tốc độ truyền tải.
* **⏯️ Smart Pause & Resume (Tính năng lõi):**
    * Cho phép tạm dừng quá trình tải khi mất mạng hoặc người dùng bấm Stop.
    * Tự động phát hiện file tải dở và tiếp tục tải từ byte cuối cùng (không tải lại từ đầu).
* **🎨 Giao diện hiện đại:** Sử dụng thư viện **CustomTkinter** mang lại trải nghiệm người dùng (UX/UI) chuyên nghiệp, hỗ trợ Dark Mode.

---

## 🛠️ Cài đặt và Môi trường

### Yêu cầu hệ thống
* **Ngôn ngữ:** Python 3.8 trở lên.
* **Hệ điều hành:** Windows / MacOS / Linux.

### Cài đặt thư viện
Chạy lệnh sau để cài đặt các gói phụ thuộc:

```bash
pip install -r requirements.txt
