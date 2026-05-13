# ===================================================
# config.py - File cấu hình trung tâm
# ===================================================
# File này chịu trách nhiệm:
#   - Đọc các biến môi trường từ file .env
#   - Cung cấp các cài đặt cho toàn bộ bot
# ===================================================

import os                      # Thư viện hệ thống để đọc biến môi trường
from dotenv import load_dotenv # Thư viện đọc file .env

# --------------------------------------------------
# Đọc file .env vào hệ thống
# --------------------------------------------------
# load_dotenv() sẽ tìm file .env trong thư mục hiện tại
# và nạp tất cả KEY=VALUE vào os.environ
load_dotenv()


# --------------------------------------------------
# CÁC BIẾN CẤU HÌNH
# --------------------------------------------------

# Token của bot (bắt buộc phải có)
# Nếu không tìm thấy → báo lỗi ngay
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError(
        "❌ Thiếu BOT_TOKEN!\n"
        "Hãy tạo file .env và điền: BOT_TOKEN=your_token_here\n"
        "Xem hướng dẫn trong file .env.example"
    )

# Danh sách User ID có quyền Admin
# Ví dụ trong .env: ADMIN_IDS=123456,789012
# Kết quả: ADMIN_IDS = {123456, 789012}
_raw_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = set()
if _raw_admin_ids:
    for id_str in _raw_admin_ids.split(","):
        id_str = id_str.strip()
        if id_str.isdigit():
            ADMIN_IDS.add(int(id_str))

# Đường dẫn file lưu dữ liệu
DATA_DIR: str = "data"
DATA_FILE: str = os.path.join(DATA_DIR, "balances.json")

# Số giao dịch hiển thị tối đa trong /history
MAX_HISTORY_DISPLAY: int = 10

# Tên bot hiển thị trong message
BOT_NAME: str = "💰 Tool Tính Tiền"
