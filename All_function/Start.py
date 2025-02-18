from telegram import Update
from telegram.ext import ContextTypes

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /start - Chào mừng người dùng"""
    
    # Tạo tin nhắn chào mừng
    welcome_message = (
        f"✨ *Xin chào {update.effective_user.first_name}!* ✨\n\n"
        "🎉 Chào mừng bạn đến với *XD Bot* - Người bạn đồng hành thông minh của bạn!\n\n"
        "🔥 *Những điều tôi có thể giúp bạn:*\n"
        "📰 Cập nhật tin tức nóng hổi mỗi ngày\n"
        "💸 Tạo mã QR thanh toán nhanh chóng\n"
        "📈 Theo dõi thông tin chứng khoán realtime\n"
        "🎮 Và nhiều tính năng thú vị khác!\n\n"
        "💡 *Hướng dẫn:*\n"
        "• Gõ /help để xem danh sách lệnh đầy đủ\n"
        "🌟 Hãy bắt đầu trải nghiệm nào! 🌟"
    )
    
    # Gửi tin nhắn với định dạng Markdown
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )

