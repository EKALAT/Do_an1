from telegram import Update
from telegram.ext import ContextTypes

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hiển thị thông tin trợ giúp về các lệnh của bot"""
    help_text = """
⭐️ *HƯỚNG DẪN SỬ DỤNG BOT* ⭐️

📱 *LỆNH CƠ BẢN*
• /start - Khởi động bot
• /hello - Chào hỏi
• /help - Xem hướng dẫn này

📈 *CHỨNG KHOÁN*
• /getstock - Cập nhật dữ liệu mới
• /allstock - Xem tất cả mã CK
• /theodoi <mã> - Theo dõi chi tiết

*Ví dụ:* 
• `/theodoi FPT` - Xem thông tin FPT
• `/theodoi VNM` - Xem thông tin VNM

📰 *TIN TỨC & THANH TOÁN*
• /news - Đọc tin tức mới nhất
• /thanhtoan - Tạo mã QR thanh toán
• /amount <số tiền> - QR với số tiền

*Ví dụ:*
• `/amount 150000` - Tạo QR 150,000đ

📊 *HƯỚNG DẪN THEO DÕI CK*
1️⃣ Chạy /getstock cập nhật data
2️⃣ Dùng /theodoi xem chi tiết
3️⃣ Xem /allstock tổng quan thị trường

ℹ️ *THÔNG TIN THÊM*
• Data trực tiếp từ SSI
• Cập nhật realtime
• Hỗ trợ mọi mã CK
• Không phân biệt chữ HOA/thường

💡 *MẸO HAY*
• Cập nhật data trước khi xem
• Theo dõi nhiều mã cùng lúc
• Đặt thông báo khi giá thay đổi

❓ *CẦN HỖ TRỢ*
• Gõ /help xem lại hướng dẫn
• Liên hệ admin nếu cần giúp đỡ

_Bot được phát triển bởi PHOMMASENG EKALAT_
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')