from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# Import các hàm từ All_function và Stock_function
from All_function.Start import start
from All_function.Hello import hello
from All_function.Help import help_command
from All_function.News import news
from Stock_function.Chungkhoan import chungkhoan

TOKEN = "7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4"

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn nói: {update.message.text}")

def main():
    # Tạo ứng dụng
    application = Application.builder().token(TOKEN).build()

    # Thêm các handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("chungkhoan", chungkhoan))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Chạy bot
    print("🤖 Bot đang chạy...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
