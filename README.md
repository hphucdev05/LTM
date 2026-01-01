

### 2. Có nên thêm hình ảnh App không? Thêm như thế nào?

**Trả lời:** **RẤT NÊN**.
Hình ảnh giúp người chấm (hoặc người xem GitHub) hình dung ngay game của bạn trông như thế nào mà không cần phải chạy code. Nó tăng độ tin cậy và thẩm mỹ cho đồ án lên rất nhiều.

**Vị trí thêm:**
Thường sẽ thêm vào ngay sau phần **"Tính Năng Nổi Bật"** hoặc tạo một mục riêng tên là **"📸 Hình Ảnh Minh Họa (Screenshots)"**.

**Cách làm:**

1. Tạo một thư mục tên là `screenshots` (hoặc để trong thư mục `docs` như đã bàn trước đó) nằm ở thư mục gốc.
2. Chụp ảnh màn hình game (Menu, Lúc chơi, Lúc thắng...).
3. Lưu ảnh vào thư mục đó (ví dụ: `menu.png`, `gameplay.png`).
4. Dùng cú pháp Markdown để chèn ảnh: `![Mô tả ảnh](đường_dẫn_ảnh)`.

---

### 📝 ĐÂY LÀ FILE README.MD HOÀN CHỈNH (Đã update thêm 2 phần trên)

Bạn hãy copy nội dung dưới đây, thay thế tên thật của các bạn vào và tạo thư mục ảnh tương ứng nhé:

```markdown
# 🚢 Đại Chiến Hạm Đội (Battleship Warfare)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green)
![Socket](https://img.shields.io/badge/Network-TCP%2FIP-orange)

Một tựa game bắn tàu (Battleship) nhiều người chơi theo thời gian thực (Real-time Multiplayer), được xây dựng bằng **Python** và **Pygame**, sử dụng kỹ thuật lập trình mạng **Socket**. Dự án được tái cấu trúc (Refactor) theo mô hình Client-Server hiện đại, chia nhỏ module để dễ dàng quản lý và phát triển.

---

## 🚀 Tính Năng Nổi Bật

* **Kiến trúc Client-Server:** Server tập trung xử lý logic, quản lý nhiều phòng chơi cùng lúc.
* **Giao thức mạng ổn định:** Sử dụng TCP Socket với cơ chế đóng gói tin tùy chỉnh (Header 4 bytes) để đảm bảo dữ liệu không bị dính hoặc mất.
* **Hệ thống phòng chơi (Room System):**
    * **Tạo phòng (Create):** Tạo phòng riêng tư với Mã phòng (Room ID).
    * **Vào phòng (Join):** Nhập ID để vào chơi với bạn bè.
    * **Ghép ngẫu nhiên (Random Match):** Tự động tìm đối thủ đang chờ.
* **Lối chơi (Gameplay):**
    * Sắp xếp đội hình tàu (Hỗ trợ xoay tàu dọc/ngang).
    * Cơ chế bắn theo lượt (Turn-based).
    * Cập nhật trạng thái trúng/trượt/chìm tàu theo thời gian thực.
    * Tự động xử lý khi đối thủ thoát đột ngột (Disconnect handling).

---

## 📸 Hình Ảnh Minh Họa (Screenshots)

*Giao diện Menu chính và Tạo phòng chờ*
![Menu Game](docs/screenshots/menu.png)
!
*Giao diện Đặt tàu và Chiến đấu*
![Gameplay](docs/screenshots/gameplay.png)

*Giao diện Tìm thấy trận*
![MatchFound](docs/screenshots/matchfound.png)

*Giao diện Kết thúc trận
![Winlose](docs/screenshots/win-lose.png)
*Giao diện Tạo phòng bạn bè*
![PrivateRoom](docs/screenshots/create_room.png)


## 📂 Cấu Trúc Dự Án

Dự án được tổ chức theo mô hình module hóa:

```text
LTM/
├── client/                 # Thư mục chứa mã nguồn Client
│   ├── __init__.py         # Khởi tạo package
│   ├── main.py             # File chạy chính (Vòng lặp game)
│   ├── ui.py               # Xử lý giao diện, hình ảnh, vẽ màn hình
│   ├── network.py          # Xử lý kết nối Socket Client
│   ├── game_logic.py       # Luật chơi, Class Tàu, Check thắng thua
│   ├── constants.py        # Cấu hình (Màu sắc, IP Server, Kích thước)
│   └── assets/             # Tài nguyên (Ảnh tàu, Nền, Icon)
├── docs/                   # Tài liệu & Hình ảnh minh chứng
├── server.py               # Mã nguồn Server (Chạy độc lập)
├── requirements.txt        # Các thư viện cần thiết
└── README.md               # Tài liệu hướng dẫn

```

---

## 🛠️ Cài Đặt

### 1. Yêu cầu

* Máy tính đã cài đặt Python 3.x.

### 2. Cài đặt thư viện

Bạn cần cài thư viện `pygame` để chạy Client.

```bash
pip install pygame

```

---

## 🎮 Hướng Dẫn Chạy (Quan Trọng)

**LƯU Ý:** Luôn mở Terminal tại **thư mục gốc** của dự án (thư mục chứa file `server.py` và folder `client`).

### Bước 1: Khởi động Server

Mở một Terminal và chạy lệnh:

```bash
python server.py

```

*Server sẽ bắt đầu lắng nghe tại `0.0.0.0:65432`.*

### Bước 2: Khởi động Client (Người chơi)

Mở một Terminal mới (cho Người chơi 1) và chạy lệnh:

```bash
python -m client.main

```

> **⚠️ CẢNH BÁO:** Tuyệt đối **KHÔNG** chạy lệnh `python client/main.py`. Điều này sẽ gây lỗi `ImportError`. Bạn bắt buộc phải dùng cờ `-m` để chạy như một module.

Để giả lập 2 hoặc nhiều người chơi, hãy mở thêm một Terminal nữa và chạy lại lệnh trên.

---

## 🕹️ Cách Chơi

* **Chuột:** Click để đặt tàu và chọn ô bắn trên bàn cờ địch.
* **Bàn phím:**
* Phím `R`: Xoay tàu (Ngang/Dọc) trong giai đoạn xếp tàu.
* Phím `Backspace`: Xóa ký tự khi nhập ID phòng.
* Phím `Enter`: Xác nhận vào phòng.



---

## 👥 Phân Công Nhóm

| Vai Trò | Trách Nhiệm Chính | Thành Viên |
| --- | --- | --- |
| **Trưởng Nhóm** | Quản lý cấu trúc, ghép code (`main.py`), xử lý luồng game. | **Lê Hoàng Phúc**  |
| **Giao Diện** | Thiết kế giao diện (`ui.py`), xử lý hình ảnh (`assets`). | **Nguyễn Quốc An**  |
| **Mạng** | Xử lý Socket (`network.py`), logic Server (`server.py`). | **Huỳnh Minh Quân**  |
| **Logic** | Xử lý luật chơi (`game_logic.py`), thuật toán check tàu. | **Bùi Văn Ý**  |


---

## 📝 Khắc Phục Lỗi Thường Gặp

**1. Lỗi `ModuleNotFoundError: No module named 'client'**`

* **Nguyên nhân:** Bạn đang đứng sai thư mục (ví dụ đang đứng trong folder `client`) hoặc chạy sai lệnh.
* **Khắc phục:** Quay ra thư mục gốc (`cd ..`) và chạy lệnh `python -m client.main`.

**2. Lỗi không kết nối được (Connection Refused)**

* **Nguyên nhân:** Server chưa bật hoặc sai địa chỉ IP.
* **Khắc phục:** Hãy chắc chắn đã chạy `python server.py` trước. Nếu chơi qua mạng LAN, hãy chỉnh IP trong `client/constants.py` thành IP của máy chủ.

---

## 📜 Bản Quyền

Dự án phục vụ mục đích học tập môn Lập trình mạng.

```

```