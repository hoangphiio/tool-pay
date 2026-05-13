#!/bin/bash
# ===================================================
# keep_alive.sh - Chạy bot trong nền, tự restart khi tắt
# ===================================================
# CÁCH DÙNG:
#   chmod +x keep_alive.sh   (chỉ 1 lần)
#   ./keep_alive.sh          (chạy bot nền - đóng terminal vẫn chạy)
#   ./keep_alive.sh stop     (dừng bot)
#   ./keep_alive.sh status   (kiểm tra trạng thái)
#   ./keep_alive.sh logs     (xem log)
# ===================================================

# Màu sắc
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Thư mục của bot (đường dẫn tuyệt đối)
BOT_DIR="/Users/hoangphiio/Documents/Tài liệu/Dev/tool-pay"
PYTHON="$BOT_DIR/venv/bin/python3"
BOT_SCRIPT="$BOT_DIR/bot.py"
LOG_FILE="$BOT_DIR/bot.log"
PID_FILE="$BOT_DIR/bot.pid"

# --------------------------------------------------
# HÀM KIỂM TRA TRẠNG THÁI
# --------------------------------------------------
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        # Kiểm tra process có đang chạy không
        if kill -0 "$PID" 2>/dev/null; then
            return 0  # Đang chạy
        fi
    fi
    return 1  # Không chạy
}

# --------------------------------------------------
# XỬ LÝ THAM SỐ DÒNG LỆNH
# --------------------------------------------------
ACTION="${1:-start}"  # Mặc định là "start" nếu không có tham số

case "$ACTION" in

    # ── DỪNG BOT ────────────────────────────────
    stop)
        if is_running; then
            PID=$(cat "$PID_FILE")
            kill "$PID"
            rm -f "$PID_FILE"
            echo -e "${RED}🛑 Bot đã dừng (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}⚠️  Bot không đang chạy${NC}"
        fi
        ;;

    # ── KIỂM TRA TRẠNG THÁI ─────────────────────
    status)
        if is_running; then
            PID=$(cat "$PID_FILE")
            echo -e "${GREEN}✅ Bot đang chạy (PID: $PID)${NC}"
            echo -e "${BLUE}📋 Log file: $LOG_FILE${NC}"
        else
            echo -e "${RED}❌ Bot không chạy${NC}"
        fi
        ;;

    # ── XEM LOG ─────────────────────────────────
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo -e "${BLUE}📋 Log của bot (50 dòng cuối):${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            tail -50 "$LOG_FILE"
        else
            echo -e "${YELLOW}⚠️  Chưa có file log${NC}"
        fi
        ;;

    # ── KHỞI ĐỘNG BOT ───────────────────────────
    start|*)
        # Kiểm tra đã chạy chưa
        if is_running; then
            PID=$(cat "$PID_FILE")
            echo -e "${YELLOW}⚠️  Bot đã đang chạy (PID: $PID)${NC}"
            echo -e "Dùng: ${BLUE}./keep_alive.sh stop${NC} để dừng"
            exit 0
        fi

        # Kiểm tra file .env
        if grep -q "your_bot_token_here" "$BOT_DIR/.env" 2>/dev/null; then
            echo -e "${RED}❌ Chưa cấu hình BOT_TOKEN trong file .env!${NC}"
            exit 1
        fi

        echo -e "${GREEN}🚀 Khởi động bot trong nền...${NC}"

        # Chạy bot trong nền:
        # nohup  → Không bị dừng khi đóng terminal
        # &      → Chạy trong background
        # > log  → Ghi stdout vào file log
        # 2>&1   → Ghi stderr vào cùng file log
        cd "$BOT_DIR" || exit 1
        nohup "$PYTHON" "$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &

        # Lưu PID để quản lý sau này
        echo $! > "$PID_FILE"
        PID=$(cat "$PID_FILE")

        sleep 2  # Chờ 2 giây để bot khởi động

        if is_running; then
            echo -e "${GREEN}✅ Bot đang chạy ngầm! (PID: $PID)${NC}"
            echo ""
            echo -e "📋 ${BLUE}Các lệnh quản lý:${NC}"
            echo -e "  Xem trạng thái : ${YELLOW}./keep_alive.sh status${NC}"
            echo -e "  Xem log        : ${YELLOW}./keep_alive.sh logs${NC}"
            echo -e "  Dừng bot       : ${YELLOW}./keep_alive.sh stop${NC}"
            echo -e "  Restart        : ${YELLOW}./keep_alive.sh stop && ./keep_alive.sh${NC}"
            echo ""
            echo -e "${GREEN}💡 Bot vẫn chạy dù bạn đóng terminal hoặc VSCode!${NC}"
        else
            echo -e "${RED}❌ Bot khởi động thất bại! Xem log:${NC}"
            tail -20 "$LOG_FILE"
        fi
        ;;
esac
