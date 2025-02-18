from telegram import Update
from telegram.ext import ContextTypes
import webbrowser

async def chungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /chungkhoan - Tự động mở website iBoard"""
    
    # URL của iBoard
    url = "https://iboard.ssi.com.vn/"
    
    # Mở website trong trình duyệt mặc định
    webbrowser.open(url, new=2)  # new=2 mở trong tab mới
    
    message = (
        "🏦 *CHỨNG KHOÁN - IBOARD SSI*\n\n"
        "✅ Đã mở website iBoard trong trình duyệt của bạn.\n"
        "📊 Chúc bạn giao dịch thành công!"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )
