from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /hello - Chào hỏi theo thời gian"""
    
    user_name = update.effective_user.first_name
    current_hour = datetime.now().hour
    
    # Xác định thời điểm và lời chào phù hợp
    if 5 <= current_hour < 12:
        greeting = "🌅 *Chào buổi sáng*"
        message = "Chúc bạn một ngày tràn đầy năng lượng! ☀️"
    elif 12 <= current_hour < 18:
        greeting = "🌞 *Chào buổi chiều*"
        message = "Chúc bạn có một buổi chiều thật vui vẻ! 🌤"
    else:
        greeting = "🌙 *Chào buổi tối*"
        message = "Chúc bạn có một buổi tối thật thư giãn! ✨"
    
    # Tạo và gửi tin nhắn chào
    hello_message = (
        f"{greeting}, *{user_name}*!\n\n"
        f"{message}\n\n"
        "💫 _Bạn cần mình giúp gì không_?\n"
        "• Gõ /help để xem hướng dẫn\n"
    )
    
    await update.message.reply_text(
        hello_message,
        parse_mode='Markdown'
    )

