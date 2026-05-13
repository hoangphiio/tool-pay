#!/bin/bash
# ===================================================
# run.sh - Script khởi chạy bot nhanh
# ===================================================
# Cách dùng:
#   chmod +x run.sh   (chỉ cần làm 1 lần)
#   ./run.sh
# ===================================================

# Màu sắc terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Khởi động Tool Tính Tiền Bot...${NC}"

# Kiểm tra file .env đã tồn tại chưa
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Không tìm thấy file .env!${NC}"
    echo -e "${YELLOW}👉 Chạy lệnh: cp .env.example .env${NC}"
    echo -e "${YELLOW}👉 Sau đó điền BOT_TOKEN và ADMIN_IDS vào file .env${NC}"
    exit 1
fi

# Kiểm tra BOT_TOKEN đã điền chưa
if grep -q "your_bot_token_here" .env; then
    echo -e "${RED}❌ Bạn chưa điền BOT_TOKEN trong file .env!${NC}"
    echo -e "${YELLOW}👉 Mở file .env và thay 'your_bot_token_here' bằng token thật${NC}"
    echo -e "${YELLOW}👉 Lấy token từ @BotFather trên Telegram${NC}"
    exit 1
fi

# Kích hoạt virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Kích hoạt virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Không tìm thấy venv, dùng Python hệ thống${NC}"
fi

# Chạy bot
echo -e "${GREEN}🤖 Bot đang khởi động...${NC}"
echo -e "${YELLOW}💡 Nhấn Ctrl+C để dừng bot${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 bot.py
