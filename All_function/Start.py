from telegram import Update, InputFile
from telegram.ext import ContextTypes

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /start - Chào mừng người dùng"""
    
    # Tạo tin nhắn chào mừng
    welcome_message = (
        f"✨ <b>Xin chào {update.effective_user.first_name}!</b> ✨\n\n"
        "🎉 Chào mừng bạn đến với <b>XD Bot</b> - <i>Người bạn đồng hành thông minh của bạn!</i>\n\n"
        "🔥 <b>Những điều tôi có thể giúp bạn:</b>\n"
        "📰 Cập nhật tin tức nóng hổi mỗi ngày\n"
        "💸 Tạo mã QR thanh toán nhanh chóng\n"
        "📈 Theo dõi thông tin chứng khoán realtime\n"
        "🎮 Và nhiều tính năng thú vị khác!\n\n"
        "💡 <b>Hướng dẫn:</b>\n"
        "• Gõ /help  để xem danh sách lệnh đầy đủ\n\n"
        "🌟 <i>Hãy bắt đầu trải nghiệm nào!</i> 🌟"
    )
    
    # Gửi GIF kèm tin nhắn chào mừng
    await update.message.reply_animation(
        animation="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGY4MjQzMjBkMDQ0ZjBhMzM5ZjI5ZjI5ZjUyYzM4ZjM5ZjQ5YjFmYiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/Wj7lNjMNDxSmc/giphy.gif",
        caption=welcome_message,
        parse_mode='HTML'
    )

