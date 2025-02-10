from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import re
import qrcode
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import os
from datetime import datetime

# Payment Information
PAYMENT_INFO = {
    'bank_name': 'BIDV',
    'account_number': '8851982864',
    'account_holder': 'PHOMMASENG EKALAT',
    'bank_code': 'BIDV',  # Mã ngân hàng
    'amount': None
}

# Bot token
BOT_TOKEN = "7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        f"👋 Chào mừng {update.effective_user.first_name} đến với XD Bot!\n\n"
        "🤖 Tôi có thể giúp bạn:\n"
        "📰 Xem tin tức mới nhất\n"
        "💰 Tạo mã QR thanh toán\n"
        "📊 Xem thông tin chứng khoán\n\n"
        "Gõ /help để xem danh sách lệnh đầy đủ."
    )
    await update.message.reply_text(welcome_message)

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📝 DANH SÁCH LỆNH:\n\n"
        "🤝 /hello - Chào hỏi\n"
        "❓ /help - Xem hướng dẫn\n"
        "📰 /news - Xem tin tức mới\n"
        "📊 /chungkhoan - Xem thông tin chứng khoán\n"
        "💳 /thanhtoan - Tạo mã QR thanh toán\n"
        "💰 /amount <số tiền> - Tạo mã QR với số tiền tùy chọn\n\n"
        "💡 Mẹo: Bạn có thể gửi tin nhắn bất kỳ, tôi sẽ phản hồi lại."
    )
    await update.message.reply_text(help_text)

# Hello Command
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        greeting = "Chào buổi sáng"
    elif 12 <= current_hour < 18:
        greeting = "Chào buổi chiều"
    else:
        greeting = "Chào buổi tối"
    
    await update.message.reply_text(
        f"👋 {greeting} {user_name}!\n"
        "Tôi có thể giúp gì cho bạn?"
    )

# News Command
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🔄 Đang tải tin tức...")
    
    try:
        latest_news = get_all_news()
        if latest_news:
            await update.message.reply_text("📰 TIN TỨC MỚI NHẤT:")
            for idx, news in enumerate(latest_news[:5], 1):  # Giới hạn 5 tin
                title = escape_markdown(news['title'])
                link = news['link']
                message = f"{idx}\\. [{title}]({link})"
                await update.message.reply_text(message, parse_mode='MarkdownV2')
        else:
            await update.message.reply_text("❌ Không có tin tức mới.")
    except Exception as e:
        await update.message.reply_text("❌ Đã xảy ra lỗi khi tải tin tức.")
        print(f"Error fetching news: {e}")

# Get All News Function
def get_all_news():
    try:
        response = requests.get("https://vnexpress.net/", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            news_items = soup.find_all("h3", {"class": "title-news"})
            for news in news_items[:10]:  # Giới hạn 10 tin
                title = news.a.get("title", "Không có tiêu đề")
                link = news.a.get("href", "#")
                news_list.append({'title': title, 'link': link})
            return news_list
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return None

# Escape special characters for MarkdownV2
def escape_markdown(text: str) -> str:
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + c if c in escape_chars else c for c in text)

# Echo Handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"🔄 Bạn vừa nói: {update.message.text}\n"
        "Gõ /help để xem các lệnh có sẵn."
    )

# Chung Khoan Command
async def chungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "⚠️ Chức năng đang được phát triển.\n"
        "Vui lòng thử lại sau!"
    )

# Payment QR Code Functions
async def thanhtoan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("50,000 VND", callback_data="pay_50000"),
            InlineKeyboardButton("100,000 VND", callback_data="pay_100000"),
        ],
        [
            InlineKeyboardButton("200,000 VND", callback_data="pay_200000"),
            InlineKeyboardButton("500,000 VND", callback_data="pay_500000"),
        ],
        [
            InlineKeyboardButton("1,000,000 VND", callback_data="pay_1000000"),
            InlineKeyboardButton("Số tiền khác", callback_data="pay_custom"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💰 THANH TOÁN QR\n\n"
        "Vui lòng chọn số tiền:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("pay_"):
        amount = query.data.replace("pay_", "")
        if amount == "custom":
            await query.message.reply_text(
                "💡 HƯỚNG DẪN:\n\n"
                "Vui lòng nhập số tiền theo định dạng:\n"
                "/amount <số tiền>\n\n"
                "Ví dụ: /amount 150000"
            )
            return
        
        try:
            amount = int(amount)
            qr_image = create_payment_qr(amount)
            
            caption = create_payment_caption(amount)
            
            await query.message.reply_photo(
                photo=qr_image,
                caption=caption,
                parse_mode='HTML'
            )
        except Exception as e:
            await query.message.reply_text("❌ Đã xảy ra lỗi khi tạo mã QR.")
            print(f"Error creating QR: {e}")

async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "⚠️ Vui lòng nhập số tiền.\n"
            "Ví dụ: /amount 150000"
        )
        return
    
    try:
        amount = int(context.args[0])
        if amount < 1000:
            await update.message.reply_text("⚠️ Số tiền tối thiểu là 1,000 VND")
            return
        elif amount > 500000000:
            await update.message.reply_text("⚠️ Số tiền tối đa là 500,000,000 VND")
            return
            
        qr_image = create_payment_qr(amount)
        caption = create_payment_caption(amount)
        
        await update.message.reply_photo(
            photo=qr_image,
            caption=caption,
            parse_mode='HTML'
        )
    except ValueError:
        await update.message.reply_text("❌ Số tiền không hợp lệ. Vui lòng nhập số.")

def create_payment_qr(amount):
    # Tạo chuỗi theo chuẩn VietQR
    qr_data = (
        f"00020101021238570010A000000727"  # Header và ID ứng dụng
        f"0111{PAYMENT_INFO['account_number']}"  # Số tài khoản
        f"0208QRIBFTTA"  # Mã ngân hàng BIDV
        f"5303704"  # Mã tiền tệ (704 là VND)
        f"54{str(amount).zfill(12)}"  # Số tiền (12 chữ số)
        f"5802VN"  # Mã quốc gia
        f"62{len(PAYMENT_INFO['account_holder']):02d}{PAYMENT_INFO['account_holder']}"  # Tên người nhận
        f"6304"  # Footer
    )
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    bio.name = 'qr.png'
    qr_image.save(bio, 'PNG')
    bio.seek(0)
    
    return bio

def create_payment_caption(amount):
    return (
        "💳 <b>THÔNG TIN CHUYỂN KHOẢN</b>\n\n"
        f"🏦 Ngân hàng: {PAYMENT_INFO['bank_name']}\n"
        f"📱 Số tài khoản: <code>{PAYMENT_INFO['account_number']}</code>\n"
        f"👤 Chủ tài khoản: <b>{PAYMENT_INFO['account_holder']}</b>\n"
        f"💰 Số tiền: <b>{amount:,} VND</b>\n\n"
        "📱 <b>HƯỚNG DẪN:</b>\n"
        "1. Mở app ngân hàng của bạn\n"
        "2. Chọn tính năng quét mã QR\n"
        "3. Quét mã QR này\n"
        "4. Kiểm tra thông tin và xác nhận"
    )

def main():
    # Khởi tạo bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Thêm các handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("chungkhoan", chungkhoan))
    app.add_handler(CommandHandler("thanhtoan", thanhtoan))
    app.add_handler(CommandHandler("amount", set_amount))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Chạy bot
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()