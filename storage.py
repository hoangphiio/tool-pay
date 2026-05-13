# ===================================================
# storage.py - Quản lý lưu trữ dữ liệu
# ===================================================
# File này chịu trách nhiệm:
#   - Đọc/ghi dữ liệu vào file JSON
#   - Cung cấp các hàm thao tác với số dư và lịch sử
#
# CẤU TRÚC DỮ LIỆU trong balances.json:
# {
#   "nam": {
#     "balance": 500000,
#     "transactions": [
#       {
#         "type": "add",           ← "add" hoặc "sub"
#         "amount": 500000,        ← số tiền (luôn dương)
#         "note": "tiền ăn",       ← ghi chú
#         "timestamp": "2024-01-01 12:00:00",
#         "by": "hoang"            ← người thực hiện
#       }
#     ]
#   }
# }
# ===================================================

import json                        # Đọc/ghi file JSON
import os                          # Thao tác với hệ thống file
from datetime import datetime      # Lấy thời gian hiện tại
from typing import Optional        # Type hint cho Python 3.9+

from config import DATA_DIR, DATA_FILE, MAX_HISTORY_DISPLAY


# ===================================================
# KHỞI TẠO
# ===================================================

def init_storage() -> None:
    """
    Tạo thư mục data/ và file balances.json nếu chưa tồn tại.
    Gọi hàm này một lần khi khởi động bot.
    """
    # Tạo thư mục data/ nếu chưa có
    # exist_ok=True → không báo lỗi nếu đã tồn tại
    os.makedirs(DATA_DIR, exist_ok=True)

    # Tạo file JSON rỗng nếu chưa có
    if not os.path.exists(DATA_FILE):
        _write_data({})  # Ghi dictionary rỗng vào file
        print(f"✅ Đã tạo file dữ liệu: {DATA_FILE}")


# ===================================================
# HÀM ĐỌC / GHI FILE
# ===================================================

def _read_data() -> dict:
    """
    Đọc toàn bộ dữ liệu từ file JSON.
    → Trả về dictionary chứa tất cả users và số dư.
    Gọi hàm có prefix _ (underscore) là hàm nội bộ,
    không nên dùng trực tiếp từ bên ngoài.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)  # Chuyển JSON string → Python dict
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu file không tồn tại hoặc bị hỏng → trả về dict rỗng
        return {}


def _write_data(data: dict) -> None:
    """
    Ghi toàn bộ dữ liệu vào file JSON.
    indent=2 → format đẹp, dễ đọc khi mở file
    ensure_ascii=False → hiển thị tiếng Việt đúng
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ===================================================
# HÀM THAO TÁC VỚI USER
# ===================================================

def get_user(username: str) -> Optional[dict]:
    """
    Lấy thông tin của một user theo tên.
    username: tên user (không có @)
    → Trả về dict chứa balance và transactions, hoặc None nếu không tìm thấy
    """
    data = _read_data()
    return data.get(username.lower())  # .lower() → không phân biệt hoa/thường


def get_all_users() -> dict:
    """
    Lấy thông tin của tất cả users.
    → Trả về toàn bộ dictionary
    """
    return _read_data()


def _ensure_user(data: dict, username: str) -> None:
    """
    Đảm bảo user tồn tại trong data.
    Nếu chưa có → tạo mới với balance = 0
    """
    if username not in data:
        data[username] = {
            "balance": 0,
            "transactions": []
        }


# ===================================================
# HÀM CỘNG / TRỪ TIỀN
# ===================================================

def add_money(
    username: str,
    amount: int,
    note: str,
    by: str
) -> dict:
    """
    Cộng tiền vào tài khoản của user.

    Tham số:
        username: tên user nhận tiền (không có @)
        amount:   số tiền cộng vào (VNĐ, số nguyên dương)
        note:     ghi chú cho giao dịch
        by:       tên người thực hiện lệnh

    Trả về:
        dict chứa thông tin user sau khi cập nhật
    """
    data = _read_data()
    username = username.lower()

    # Tạo user mới nếu chưa tồn tại
    _ensure_user(data, username)

    # Cộng tiền vào số dư
    data[username]["balance"] += amount

    # Tạo bản ghi giao dịch mới
    transaction = {
        "type": "add",
        "amount": amount,
        "note": note if note else "Không có ghi chú",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "by": by
    }

    # Thêm giao dịch vào đầu danh sách (giao dịch mới nhất lên đầu)
    data[username]["transactions"].insert(0, transaction)

    # Lưu lại vào file
    _write_data(data)

    return data[username]


def subtract_money(
    username: str,
    amount: int,
    note: str,
    by: str
) -> dict:
    """
    Trừ tiền khỏi tài khoản của user.

    Tham số:
        username: tên user bị trừ tiền (không có @)
        amount:   số tiền trừ đi (VNĐ, số nguyên dương)
        note:     ghi chú cho giao dịch
        by:       tên người thực hiện lệnh

    Trả về:
        dict chứa thông tin user sau khi cập nhật
    """
    data = _read_data()
    username = username.lower()

    # Tạo user mới nếu chưa tồn tại
    _ensure_user(data, username)

    # Trừ tiền khỏi số dư (có thể âm)
    data[username]["balance"] -= amount

    # Tạo bản ghi giao dịch mới
    transaction = {
        "type": "sub",
        "amount": amount,
        "note": note if note else "Không có ghi chú",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "by": by
    }

    # Thêm giao dịch vào đầu danh sách
    data[username]["transactions"].insert(0, transaction)

    # Lưu lại vào file
    _write_data(data)

    return data[username]


def reset_user(username: str, by: str) -> dict:
    """
    Reset số dư của user về 0 và xóa toàn bộ lịch sử.
    Chỉ admin mới được dùng hàm này.

    Tham số:
        username: tên user cần reset
        by:       tên admin thực hiện lệnh

    Trả về:
        dict chứa thông tin user sau khi reset
    """
    data = _read_data()
    username = username.lower()

    # Ghi lại giao dịch reset trước khi xóa
    old_balance = data.get(username, {}).get("balance", 0)

    # Reset về trạng thái ban đầu
    data[username] = {
        "balance": 0,
        "transactions": [
            {
                "type": "reset",
                "amount": old_balance,
                "note": f"Reset bởi admin (số dư cũ: {old_balance:,}₫)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "by": by
            }
        ]
    }

    _write_data(data)
    return data[username]


# ===================================================
# HÀM FORMAT DỮ LIỆU
# ===================================================

def format_money(amount: int) -> str:
    """
    Format số tiền sang dạng đẹp có dấu phân cách.
    Ví dụ: 1500000 → "1,500,000₫"
    """
    return f"{amount:,}₫"


def get_history(username: str, limit: int = MAX_HISTORY_DISPLAY) -> list:
    """
    Lấy lịch sử giao dịch của user.
    limit: số giao dịch tối đa cần lấy
    → Trả về list các giao dịch gần nhất
    """
    user = get_user(username)
    if not user:
        return []

    # Trả về tối đa `limit` giao dịch đầu tiên
    return user["transactions"][:limit]
