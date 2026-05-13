# ===================================================
# bot.py - File CHÍNH của Telegram Bot (v2 - HTML mode)
# ===================================================
# Đây là file bạn chạy để khởi động bot: python bot.py
#
# THAY ĐỔI SO VỚI v1:
#   - Đổi từ MARKDOWN_V2 → HTML (ổn định hơn, ít lỗi hơn)
#   - HTML mode chỉ cần escape: < > &  (thay vì ~20 ký tự của MD v2)
#   - Dùng html.escape() để bảo vệ tên user không làm hỏng format
# ===================================================

# --------------------------------------------------
# IMPORT CÁC THƯ VIỆN
# --------------------------------------------------
import html as html_lib           # Escape ký tự HTML đặc biệt
import logging                    # Ghi log để debug
from datetime import datetime      # Lấy thời gian hiện tại

# Các class từ thư viện python-telegram-bot
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ParseMode   # ParseMode.HTML

# Import từ các file của chúng ta
from config import BOT_TOKEN, ADMIN_IDS, BOT_NAME
from storage import (
    init_storage,
    get_user,
    get_all_users,
    add_money,
    subtract_money,
    reset_user,
    get_history,
    format_money,
)


# --------------------------------------------------
# CẤU HÌNH LOGGING
# --------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ===================================================
# CÁC HÀM TIỆN ÍCH
# ===================================================

def esc(text: str) -> str:
    """
    Escape text để dùng an toàn trong HTML Telegram.
    Chuyển: & → &amp;   < → &lt;   > → &gt;
    Dùng cho mọi nội dung do USER nhập vào (tên, ghi chú...)
    để tránh bị lỗi parse HTML.
    """
    return html_lib.escape(str(text))


def get_display_name(user) -> str:
    """
    Lấy tên hiển thị của người dùng Telegram.
    Ưu tiên: username > first_name > "Unknown"
    """
    if user.username:
        return user.username
    elif user.first_name:
        return user.first_name
    return "Unknown"


def parse_username(raw: str) -> str:
    """
    Chuẩn hóa username: xóa @ ở đầu nếu có, chuyển thành chữ thường.
    Ví dụ: "@NAM" → "nam"
    """
    return raw.lstrip("@").lower()


def is_admin(user_id: int) -> bool:
    """Kiểm tra user_id có trong danh sách admin không."""
    return user_id in ADMIN_IDS


# ===================================================
# COMMAND HANDLERS
# ===================================================

# --------------------------------------------------
# /start
# --------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /start - Chào mừng người dùng."""
    if not update.message:  # Guard: bỏ qua nếu không phải tin nhắn thường
        return
    user = update.effective_user
    name = esc(get_display_name(user))  # esc() để an toàn với HTML

    message = (
        f"👋 Xin chào <b>{name}</b>!\n\n"
        f"Tôi là <b>{esc(BOT_NAME)}</b>.\n"
        "Giúp bạn quản lý tiền cho nhiều người trong nhóm.\n\n"
        "📖 Gõ /help để xem danh sách lệnh"
    )

    # parse_mode=ParseMode.HTML → dùng thẻ HTML như <b>, <i>, <code>
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /help
# --------------------------------------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /help - Hiển thị tất cả lệnh có sẵn."""
    if not update.message:
        return

    message = (
        f"📚 <b>{esc(BOT_NAME)} — Danh sách lệnh</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "➕ <b>Cộng tiền</b>\n"
        "<code>/add @user số_tiền ghi_chú</code>\n"
        "VD: <code>/add @nam 500000 tiền ăn trưa</code>\n\n"

        "➖ <b>Trừ tiền</b>\n"
        "<code>/sub @user số_tiền ghi_chú</code>\n"
        "VD: <code>/sub @nam 200000 đã trả nợ</code>\n\n"

        "💰 <b>Xem số dư</b>\n"
        "<code>/balance</code> — Xem số dư của bạn\n"
        "<code>/balance @user</code> — Xem số dư người khác\n\n"

        "📋 <b>Xem lịch sử</b>\n"
        "<code>/history @user</code> — 10 giao dịch gần nhất\n\n"

        "📊 <b>Tổng hợp tất cả</b>\n"
        "<code>/summary</code> — Xem số dư & lịch sử kèm ngày tháng\n\n"

        "👥 <b>Danh sách users</b>\n"
        "<code>/users</code> — Xem tất cả người dùng\n\n"

        "🔄 <b>Reset (chỉ admin)</b>\n"
        "<code>/reset @user</code> — Xóa số dư về 0\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>Mẹo:</b> Số tiền không cần dấu phẩy\n"
        "VD: <code>500000</code> = 500.000₫\n"
        "📅 Bot tự động ghi lại ngày tháng mỗi giao dịch."
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /add - Cộng tiền
# --------------------------------------------------
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /add
    Cú pháp: /add @user số_tiền [ghi_chú]
    Ví dụ:   /add @nam 500000 tiền ăn trưa
    """
    if not update.message:
        return
    args = context.args  # List tham số sau lệnh

    # Kiểm tra có đủ tham số không
    if not args or len(args) < 2:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "✅ Đúng: <code>/add @user số_tiền ghi_chú</code>\n"
            "VD: <code>/add @nam 500000 tiền ăn trưa</code>",
            parse_mode=ParseMode.HTML
        )
        return

    raw_username = args[0]
    raw_amount   = args[1]
    note         = " ".join(args[2:]) if len(args) > 2 else ""

    username = parse_username(raw_username)

    # Kiểm tra số tiền hợp lệ
    if not raw_amount.isdigit():
        await update.message.reply_text(
            "❌ Số tiền không hợp lệ!\n"
            "Vui lòng nhập số nguyên dương.\n"
            "VD: <code>500000</code> (không dùng dấu phẩy)",
            parse_mode=ParseMode.HTML
        )
        return

    amount = int(raw_amount)
    if amount <= 0:
        await update.message.reply_text("❌ Số tiền phải lớn hơn 0!")
        return

    # Thực hiện cộng tiền
    by = get_display_name(update.effective_user)
    user_data = add_money(username, amount, note, by)
    balance = user_data["balance"]
    balance_icon = "🟢" if balance >= 0 else "🔴"

    note_display = f"📝 {esc(note)}" if note else "📝 Không có ghi chú"

    message = (
        f"✅ <b>Đã cộng tiền thành công!</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"👤 User: <b>@{esc(username)}</b>\n"
        f"➕ Số tiền: <b>+{esc(format_money(amount))}</b>\n"
        f"{note_display}\n"
        "━━━━━━━━━━━━━━━\n"
        f"{balance_icon} Số dư hiện tại: <b>{esc(format_money(balance))}</b>\n"
        f"🕐 Lúc: {esc(datetime.now().strftime('%d/%m/%Y %H:%M'))}\n"
        f"👤 Bởi: @{esc(by)}"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /sub - Trừ tiền
# --------------------------------------------------
async def sub_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /sub
    Cú pháp: /sub @user số_tiền [ghi_chú]
    Ví dụ:   /sub @nam 200000 đã trả nợ
    """
    if not update.message:
        return
    args = context.args

    if not args or len(args) < 2:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "✅ Đúng: <code>/sub @user số_tiền ghi_chú</code>\n"
            "VD: <code>/sub @nam 200000 đã trả nợ</code>",
            parse_mode=ParseMode.HTML
        )
        return

    raw_username = args[0]
    raw_amount   = args[1]
    note         = " ".join(args[2:]) if len(args) > 2 else ""

    username = parse_username(raw_username)

    if not raw_amount.isdigit():
        await update.message.reply_text(
            "❌ Số tiền không hợp lệ!\n"
            "VD: <code>200000</code> (không dùng dấu phẩy)",
            parse_mode=ParseMode.HTML
        )
        return

    amount = int(raw_amount)
    if amount <= 0:
        await update.message.reply_text("❌ Số tiền phải lớn hơn 0!")
        return

    by = get_display_name(update.effective_user)
    user_data = subtract_money(username, amount, note, by)
    balance = user_data["balance"]
    balance_icon = "🟢" if balance >= 0 else "🔴"

    note_display = f"📝 {esc(note)}" if note else "📝 Không có ghi chú"

    message = (
        f"✅ <b>Đã trừ tiền thành công!</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"👤 User: <b>@{esc(username)}</b>\n"
        f"➖ Số tiền: <b>-{esc(format_money(amount))}</b>\n"
        f"{note_display}\n"
        "━━━━━━━━━━━━━━━\n"
        f"{balance_icon} Số dư hiện tại: <b>{esc(format_money(balance))}</b>\n"
        f"🕐 Lúc: {esc(datetime.now().strftime('%d/%m/%Y %H:%M'))}\n"
        f"👤 Bởi: @{esc(by)}"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /balance - Xem số dư
# --------------------------------------------------
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /balance
    /balance         → số dư của bản thân
    /balance @user   → số dư của người khác
    """
    if not update.message:
        return
    args = context.args

    if not args:
        username = get_display_name(update.effective_user)
    else:
        username = parse_username(args[0])

    user_data = get_user(username)

    if not user_data:
        await update.message.reply_text(
            f"❓ Không tìm thấy user <b>@{esc(username)}</b>.\n"
            "User này chưa có giao dịch nào.",
            parse_mode=ParseMode.HTML
        )
        return

    balance = user_data["balance"]
    tx_count = len(user_data["transactions"])
    balance_icon = "🟢" if balance >= 0 else "🔴"

    message = (
        f"💰 <b>Số dư của @{esc(username)}</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"{balance_icon} Số dư: <b>{esc(format_money(balance))}</b>\n"
        f"📊 Tổng giao dịch: {tx_count} lần\n"
        "━━━━━━━━━━━━━━━\n"
        f"📋 Xem lịch sử: <code>/history @{esc(username)}</code>"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /history - Lịch sử giao dịch
# --------------------------------------------------
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /history
    Cú pháp: /history @user
    """
    if not update.message:
        return
    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ Vui lòng nhập tên user!\n"
            "VD: <code>/history @nam</code>",
            parse_mode=ParseMode.HTML
        )
        return

    username = parse_username(args[0])
    transactions = get_history(username)

    if not transactions:
        await update.message.reply_text(
            f"❓ Không tìm thấy lịch sử của <b>@{esc(username)}</b>.",
            parse_mode=ParseMode.HTML
        )
        return

    # Tạo danh sách giao dịch
    tx_lines = []
    for i, tx in enumerate(transactions, 1):
        if tx["type"] == "add":
            icon = "➕"
            amount_str = f"+{format_money(tx['amount'])}"
        elif tx["type"] == "sub":
            icon = "➖"
            amount_str = f"-{format_money(tx['amount'])}"
        else:  # reset
            icon = "🔄"
            amount_str = "Reset"

        tx_lines.append(
            f"{i}. {icon} <b>{esc(amount_str)}</b>\n"
            f"   📝 {esc(tx['note'])}\n"
            f"   🕐 {esc(tx['timestamp'])}"
        )

    history_text = "\n\n".join(tx_lines)
    message = (
        f"📋 <b>Lịch sử giao dịch của @{esc(username)}</b>\n"
        "<i>(10 giao dịch gần nhất)</i>\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{history_text}"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /summary - Tổng hợp tất cả (kèm ghi chú + số tiền từng lần)
# --------------------------------------------------
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /summary
    Hiển thị cho từng user:
      - Danh sách giao dịch theo thứ tự thời gian (cũ → mới)
      - Ghi chú kèm theo từng giao dịch
      - Số dư hiện tại của mỗi người
    Cuối cùng: tổng cộng tất cả.
    """
    if not update.message:
        return
    all_users = get_all_users()

    if not all_users:
        await update.message.reply_text(
            "📊 Chưa có dữ liệu nào.\n"
            "Thêm giao dịch đầu tiên bằng lệnh /add",
        )
        return

    # Sắp xếp theo số dư giảm dần (người nhiều tiền nhất lên đầu)
    sorted_users = sorted(
        all_users.items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )

    total = 0
    user_blocks = []  # Mỗi phần tử là 1 block text của 1 user

    for i, (username, data) in enumerate(sorted_users, 1):
        balance = data["balance"]
        total += balance
        balance_icon = "🟢" if balance >= 0 else "🔴"
        transactions = data.get("transactions", [])

        # Tiêu đề user
        block_lines = [f"{i}. <b>@{esc(username)}</b>"]

        # Danh sách giao dịch theo thứ tự từ cũ → mới
        if transactions:
            chronological = list(reversed(transactions))  # Đảo lại để cũ → mới
            for tx in chronological:
                if tx["type"] == "add":
                    tx_icon = "➕"
                    amount_str = f"+{format_money(tx['amount'])}"
                elif tx["type"] == "sub":
                    tx_icon = "➖"
                    amount_str = f"-{format_money(tx['amount'])}"
                else:  # reset
                    tx_icon = "🔄"
                    amount_str = "Reset"

                note = tx.get("note", "")
                # Lấy ngày tháng từ timestamp (YYYY-MM-DD HH:MM:SS) -> DD/MM
                ts = tx.get("timestamp", "")
                date_part = ""
                if ts and len(ts) >= 10:
                    date_part = f" (<i>{ts[8:10]}/{ts[5:7]}</i>)"

                # Hiển thị: ➕ +500,000₫ (09/05) — tiền ăn trưa
                note_part = f" — {esc(note)}" if note and note != "Không có ghi chú" else ""
                block_lines.append(f"   {tx_icon} {esc(amount_str)}{date_part}{note_part}")
        else:
            block_lines.append("   <i>(Chưa có giao dịch)</i>")

        # Dòng tổng số dư của user
        block_lines.append(f"   └ {balance_icon} <b>Tổng: {esc(format_money(balance))}</b>")

        user_blocks.append("\n".join(block_lines))

    # Ghép toàn bộ
    body = "\n\n".join(user_blocks)
    total_icon = "🟢" if total >= 0 else "🔴"

    header = "📊 <b>Tổng hợp chi tiết</b>\n━━━━━━━━━━━━━━━\n\n"
    footer = (
        "\n\n━━━━━━━━━━━━━━━\n"
        f"{total_icon} <b>Tổng cộng tất cả: {esc(format_money(total))}</b>\n"
        f"👥 Số người: {len(all_users)}"
    )

    full_message = header + body + footer

    # Telegram giới hạn 4096 ký tự/tin nhắn → nếu quá dài thì tách nhiều tin
    MAX_LEN = 4000
    if len(full_message) <= MAX_LEN:
        await update.message.reply_text(full_message, parse_mode=ParseMode.HTML)
    else:
        # Gửi tiêu đề
        await update.message.reply_text(
            "📊 <b>Tổng hợp chi tiết</b>\n━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.HTML
        )
        # Gửi từng user một
        for block in user_blocks:
            await update.message.reply_text(block, parse_mode=ParseMode.HTML)
        # Gửi tổng cộng
        await update.message.reply_text(
            "━━━━━━━━━━━━━━━\n"
            f"{total_icon} <b>Tổng cộng tất cả: {esc(format_money(total))}</b>\n"
            f"👥 Số người: {len(all_users)}",
            parse_mode=ParseMode.HTML
        )


# --------------------------------------------------
# /users - Danh sách users
# --------------------------------------------------
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /users - Danh sách tất cả users."""
    if not update.message:
        return
    all_users = get_all_users()

    if not all_users:
        await update.message.reply_text("👥 Chưa có user nào.")
        return

    lines = [f"• @{esc(username)}" for username in sorted(all_users.keys())]
    users_text = "\n".join(lines)

    message = (
        f"👥 <b>Danh sách {len(all_users)} users</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{users_text}\n\n"
        "Xem số dư: <code>/summary</code>"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# --------------------------------------------------
# /reset - Reset số dư (chỉ admin)
# --------------------------------------------------
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý lệnh /reset (chỉ admin)
    Cú pháp: /reset @user
    """
    if not update.message:
        return
    # Kiểm tra quyền admin
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "🚫 <b>Bạn không có quyền thực hiện lệnh này!</b>\n"
            "Chỉ admin mới có thể reset số dư.",
            parse_mode=ParseMode.HTML
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Vui lòng nhập tên user!\n"
            "VD: <code>/reset @nam</code>",
            parse_mode=ParseMode.HTML
        )
        return

    username = parse_username(args[0])
    user_data = get_user(username)

    if not user_data:
        await update.message.reply_text(
            f"❓ Không tìm thấy user <b>@{esc(username)}</b>.",
            parse_mode=ParseMode.HTML
        )
        return

    old_balance = user_data["balance"]
    by = get_display_name(update.effective_user)
    reset_user(username, by)

    message = (
        "🔄 <b>Đã reset tài khoản!</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"👤 User: <b>@{esc(username)}</b>\n"
        f"📉 Số dư cũ: {esc(format_money(old_balance))}\n"
        f"✅ Số dư mới: <b>{esc(format_money(0))}</b>\n"
        f"🕐 Bởi admin: @{esc(by)}"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# ===================================================
# ERROR HANDLER - Bắt lỗi toàn cục
# ===================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Bắt tất cả lỗi không được xử lý và ghi vào log.
    Giúp bot không bị crash im lặng khi gặp lỗi bất ngờ.
    """
    logger.error("❌ Lỗi khi xử lý update:", exc_info=context.error)


# ===================================================
# HÀM MAIN - KHỞI CHẠY BOT
# ===================================================

def main() -> None:
    """
    Hàm chính để khởi động bot.
    1. Khởi tạo storage
    2. Tạo Application
    3. Đăng ký command handlers
    4. Bắt đầu polling
    """
    init_storage()
    print(f"🚀 Đang khởi động {BOT_NAME}...")

    # Tạo Application (ứng dụng bot)
    app = Application.builder().token(BOT_TOKEN).build()

    # --------------------------------------------------
    # ĐĂNG KÝ CÁC COMMAND HANDLERS
    # Cú pháp: app.add_handler(CommandHandler("tên_lệnh", hàm_xử_lý))
    # --------------------------------------------------
    app.add_handler(CommandHandler("start",   start_command))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("add",     add_command))
    app.add_handler(CommandHandler("sub",     sub_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("users",   users_command))
    app.add_handler(CommandHandler("reset",   reset_command))

    # Đăng ký error handler toàn cục
    app.add_error_handler(error_handler)

    print("✅ Đã đăng ký tất cả lệnh!")
    print("🤖 Bot đang chạy... Nhấn Ctrl+C để dừng.")
    print(f"👑 Admin IDs: {ADMIN_IDS if ADMIN_IDS else 'Chưa cấu hình'}")

    # Bắt đầu lắng nghe tin nhắn từ Telegram (polling mode)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    main()
