Nhom01_FileTransferApp/
│
├── .gitignore               <-- Cấu hình Git (để loại bỏ file rác)
├── README.md                <-- Hướng dẫn chạy dự án (cho Giảng viên đọc)
├── requirements.txt         <-- Danh sách thư viện cần cài (VD: customtkinter)
│
├── src/                     <-- SOURCE CODE CHÍNH (Yêu cầu: Full Source Code)
│   ├── __init__.py
│   │
│   ├── common/              <-- Code dùng chung (Giao thức mạng)
│   │   ├── __init__.py
│   │   ├── protocol.py      <-- Định nghĩa lệnh: LOGIN, UPLOAD, PAUSE...
│   │   └── file_utils.py    <-- Hàm cắt file/ghép file (Xử lý byte)
│   │
│   ├── server/              <-- Code phía Server (Thành viên 1)
│   │   ├── __init__.py
│   │   ├── main_server.py   <-- File chạy Server
│   │   ├── client_handler.py<-- Thread xử lý từng kết nối
│   │   └── server_storage/  <-- Thư mục chứa file đã upload lên Server
│   │
│   └── client/              <-- Code phía Client (Thành viên 2, 3)
│       ├── __init__.py
│       ├── main_client.py   <-- File chạy Client
│       ├── core_logic.py    <-- Xử lý gửi/nhận file, socket
│       ├── ui_app.py        <-- Giao diện (Tkinter/CustomTkinter)
│       └── downloads/       <-- Thư mục chứa file tải về
│
└── docs/                    <-- HỒ SƠ BÁO CÁO (Quan trọng để nộp bài)
    ├── 1_PhanCong/          <-- Chứa file Excel phân công
    │   └── BangPhanCong.xlsx
    │
    ├── 2_BaoCaoWord/        <-- Chứa file Word (Tối đa 20 trang)
    │   └── Nhom01_BaoCao.docx
    │
    ├── 3_ThuyetTrinh/       <-- Chứa file PowerPoint
    │   └── Nhom01_Slide.pptx
    │
    ├── 4_ThietKe/           <-- Chứa hình ảnh UML, Flowchart, Pseudo Code
    │   ├── UseCase.png
    │   ├── Sequence_Resume.png
    │   ├── Flowchart_Upload.png
    │   └── diagram.puml     <-- File code PlantUML gốc
    │
    └── 5_MinhChungGit/      <-- Chứa ảnh chụp lịch sử commit Git
        ├── Member1_Commit.png
        ├── Member2_Commit.png
        └── Git_History_Tree.png