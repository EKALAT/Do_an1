from telegram import Update
from telegram.ext import ContextTypes

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📝 DANH SÁCH LỆNH:\n\n"
        "🤝 /hello - Chào hỏi\n"
        "📰 /news - Xem tin tức mới\n"
        "📊 /getstock - Xem thông tin chứng khoán\n"
        "💸 /thanhtoan <số tiền> - Tạo mã QR thanh toán\n"
        "💡 Mẹo: Bạn có thể gửi tin nhắn bất kỳ, tôi sẽ phản hồi lại."
    )
    await update.message.reply_text(help_text)