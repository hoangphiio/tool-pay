# ===================================================

# 📖 README.md - Hướng dẫn sử dụng Tool Tính Tiền

# ===================================================

# 💰 Tool Tính Tiền - Telegram Bot

Bot Telegram giúp quản lý số dư tiền (VNĐ) cho nhiều người trong nhóm.

---

## 📋 Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Bước 1 - Tạo Bot Telegram](#2-bước-1---tạo-bot-telegram)
3. [Bước 2 - Cài đặt môi trường](#3-bước-2---cài-đặt-môi-trường)
4. [Bước 3 - Cấu hình bot](#4-bước-3---cấu-hình-bot)
5. [Bước 4 - Chạy bot](#5-bước-4---chạy-bot)
6. [Danh sách lệnh](#6-danh-sách-lệnh)
7. [Ví dụ sử dụng](#7-ví-dụ-sử-dụng)
8. [Giữ bot chạy 24/7](#8-giữ-bot-chạy-247)

---

## 1. Yêu cầu hệ thống

- **Python 3.10** trở lên
- **pip** (trình quản lý thư viện Python)
- Tài khoản **Telegram**
- Kết nối internet

### Kiểm tra Python đã cài chưa:

```bash
python3 --version
# Kết quả mong muốn: Python 3.10.x hoặc cao hơn
```

---

## 2. Bước 1 - Tạo Bot Telegram

### Bước 2.1 - Tìm BotFather

1. Mở Telegram
2. Tìm kiếm `@BotFather`
3. Nhấn **Start**

### Bước 2.2 - Tạo bot mới

Gõ lệnh trong chat với BotFather:

```
/newbot
```

### Bước 2.3 - Đặt tên bot

BotFather sẽ hỏi 2 câu:

- **Tên hiển thị:** VD → `Tool Tính Tiền Nhóm`
- **Username (tên đăng nhập):** VD → `tinh_tien_nhom_bot` _(phải kết thúc bằng "bot")_

### Bước 2.4 - Lấy Token

Sau khi tạo xong, BotFather gửi cho bạn **Bot Token** trông như thế này:

```
1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456
```

⚠️ **Giữ token này bí mật! Không chia sẻ với ai.**

### Bước 2.5 - Lấy User ID của bạn (để làm Admin)

1. Tìm `@userinfobot` trên Telegram
2. Nhấn Start
3. Bot sẽ gửi lại User ID của bạn (dạng số, VD: `123456789`)

---

## 3. Bước 2 - Cài đặt môi trường

### Clone project về máy:

```bash
cd ~/Documents  # Hoặc thư mục bạn muốn
# Nếu dùng git:
git clone <repo-url> tool-pay
cd tool-pay
```

### Tạo môi trường ảo (khuyến nghị):

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt (macOS/Linux):
source venv/bin/activate

# Kích hoạt (Windows):
venv\Scripts\activate

# Dấu hiệu thành công: tên terminal có (venv) ở đầu
```

### Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

Kết quả thành công sẽ thấy:

```
Successfully installed python-telegram-bot-20.7 python-dotenv-1.0.0 ...
```

---

## 4. Bước 3 - Cấu hình bot

### Tạo file .env từ mẫu:

```bash
cp .env.example .env
```

### Mở file .env và điền thông tin:

```bash
# Dùng nano (terminal):
nano .env

# Hoặc mở bằng VS Code:
code .env
```

Nội dung file .env sau khi điền:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456
ADMIN_IDS=123456789
```

> **Nếu có nhiều admin:** `ADMIN_IDS=123456789,987654321`

### Lưu file và thoát:

- Nano: `Ctrl+X` → `Y` → `Enter`

---

## 5. Bước 4 - Chạy bot

```bash
# Đảm bảo đang ở thư mục tool-pay và venv đã active
python bot.py
```

Kết quả thành công:

```
✅ Đã tạo file dữ liệu: data/balances.json
🚀 Đang khởi động 💰 Tool Tính Tiền...
✅ Đã đăng ký tất cả lệnh!
🤖 Bot đang chạy... Nhấn Ctrl+C để dừng.
```

### Thêm bot vào group:

1. Mở group Telegram của bạn
2. Nhấn vào tên group → **Add Members**
3. Tìm username bot của bạn (VD: `@tinh_tien_nhom_bot`)
4. Thêm vào group
5. Gõ `/start` để bắt đầu!

---

## 6. Danh sách lệnh

| Lệnh       | Cú pháp                      | Mô tả                     |
| ---------- | ---------------------------- | ------------------------- |
| `/start`   | `/start`                     | Chào mừng & giới thiệu    |
| `/help`    | `/help`                      | Xem tất cả lệnh           |
| `/add`     | `/add @user số_tiền ghi_chú` | Cộng tiền vào user        |
| `/sub`     | `/sub @user số_tiền ghi_chú` | Trừ tiền khỏi user        |
| `/balance` | `/balance [@user]`           | Xem số dư                 |
| `/history` | `/history @user`             | Xem 10 giao dịch gần nhất |
| `/summary` | `/summary`                   | Tổng hợp số dư tất cả     |
| `/users`   | `/users`                     | Danh sách tất cả users    |
| `/reset`   | `/reset @user`               | Reset về 0 (admin only)   |

---

## 7. Ví dụ sử dụng

### Tình huống: Nhóm 3 người đi ăn

**Nam** trả tiền ăn cho cả nhóm (600k), mỗi người nợ Nam 200k:

```
/add @lan 200000 tiền ăn trưa 9/5
/add @hung 200000 tiền ăn trưa 9/5
```

**Lan** trả nợ Nam 200k:

```
/sub @lan 200000 đã trả nợ tiền ăn
```

Xem số dư hiện tại:

```
/summary
```

Xem lịch sử của Lan:

```
/history @lan
```

Admin reset khi kết toán xong tháng:

```
/reset @lan
/reset @hung
```

---

## 8. Giữ bot chạy 24/7

### Cách 1: Dùng `nohup` (Linux/Mac - đơn giản)

```bash
nohup python bot.py > bot.log 2>&1 &

# Xem log:
tail -f bot.log

# Dừng bot:
kill $(pgrep -f "python bot.py")
```

### Cách 2: Dùng `pm2` (khuyên dùng)

```bash
# Cài pm2
npm install -g pm2

# Chạy bot với pm2
pm2 start bot.py --name "tool-pay" --interpreter python3

# Xem trạng thái
pm2 status

# Xem log
pm2 logs tool-pay

# Dừng bot
pm2 stop tool-pay

# Tự khởi động lại khi máy restart
pm2 startup
pm2 save
```

### Cách 3: Deploy lên VPS (chạy 24/7 trên server)

1. Thuê VPS (DigitalOcean, Vultr,... ~$4/tháng)
2. SSH vào VPS
3. Cài Python, clone project, cấu hình .env
4. Dùng pm2 hoặc systemd để chạy

---

## 📁 Cấu trúc thư mục

```
tool-pay/
├── bot.py              ← File chính, chạy cái này
├── config.py           ← Cấu hình, đọc .env
├── storage.py          ← Quản lý dữ liệu JSON
├── data/
│   └── balances.json   ← Dữ liệu tự động tạo
├── requirements.txt    ← Danh sách thư viện
├── .env                ← Token bí mật (tự tạo)
├── .env.example        ← Mẫu cấu hình
├── .gitignore          ← File không đưa lên git
└── README.md           ← File này
```

---

## ❓ Câu hỏi thường gặp

**Q: Bot không nhận lệnh trong group?**

> Vào Settings của bot trong BotFather → Bot Settings → Group Privacy → **Disable**

**Q: Lỗi "Unauthorized" khi chạy?**

> Kiểm tra lại BOT_TOKEN trong file .env, đảm bảo copy đúng và đầy đủ

**Q: Dữ liệu lưu ở đâu?**

> File `data/balances.json` trong thư mục project

**Q: Làm sao backup dữ liệu?**

> Copy file `data/balances.json` ra nơi khác

---

_Made with ❤️ using Python & python-telegram-bot_
