from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackQueryHandler
)
from All_function.Start import start
from All_function.Hello import hello
from All_function.Help import help_command
from All_function.News import news
from All_function.Thanhtoan import thanhtoan, button_callback, set_amount
from Stock_function.Getstock import getstock, allstock, track_stock

TOKEN = "7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4"

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phản hồi lại tin nhắn của người dùng"""
    await update.message.reply_text(f"Bạn nói: {update.message.text}")

def main():
    # Initialize bot with your token
    application = Application.builder().token(TOKEN).build()

    # Thêm các handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("getstock", getstock))
    application.add_handler(CommandHandler("allstock", allstock))

    # Thêm handlers cho thanh toán
    application.add_handler(CommandHandler("thanhtoan", thanhtoan))
    application.add_handler(CommandHandler("amount", set_amount))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Thêm handler cho tin nhắn thông thường
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Thêm handler mới
    application.add_handler(CommandHandler("theodoi", track_stock))

    print("🤖 Bot đang chạy...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()