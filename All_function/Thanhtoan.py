from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import qrcode
from io import BytesIO

# Payment Information
PAYMENT_INFO = {
    'bank_name': 'BIDV',
    'account_number': '8851982864',
    'account_holder': 'PHOMMASENG EKALAT',
    'bank_code': 'BIDV',  # Mã ngân hàng
    'amount': None
}

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