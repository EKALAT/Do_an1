from telegram import Update
from telegram.ext import ContextTypes

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hiển thị thông tin trợ giúp về các lệnh của bot"""
    help_text = """
🤖 *CHÀO MỪNG ĐẾN VỚI STOCK BOT* 🤖

⏰ *THỜI GIAN GIAO DỊCH*
• *Phiên Sáng:* 09:00 - 11:30
• *Phiên Chiều:* 13:00 - 14:45

🔄 *CÁC PHIÊN ĐẶC BIỆT*
• *ATO (At The Opening - Định giá mở cửa):* 
  09:00 - 09:15 
  _Xác định giá mở cửa phiên sáng_

• *ATC (At The Close - Định giá đóng cửa):* 
  14:30 - 14:45
  _Xác định giá đóng cửa phiên chiều_

• *PLO (Post-Limited Order - Giao dịch sau giờ):*
  14:45 - 15:00
  _Khớp lệnh thỏa thuận sau giờ_

📱 *LỆNH CƠ BẢN*
• /start - Khởi động bot
• /hello - Chào hỏi
• /help - Xem hướng dẫn này

📈 *CHỨNG KHOÁN & THEO DÕI*
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

📊 *QUY TRÌNH THEO DÕI*
1️⃣ Cập nhật data với /getstock
2️⃣ Xem chi tiết bằng /theodoi
3️⃣ Theo dõi thị trường qua /allstock

💡 *MẸO GIAO DỊCH*
• Phiên ATO: Đặt lệnh định hình xu hướng ngày
• Phiên ATC: Tham gia định giá cuối ngày
• Phiên PLO: Thích hợp giao dịch khối lượng lớn
• Tránh đặt lệnh vào giờ nghỉ trưa
• Theo dõi thanh khoản từng phiên

ℹ️ *THÔNG TIN BỔ SUNG*
• Dữ liệu trực tiếp từ SSI
• Cập nhật theo thời gian thực
• Hỗ trợ tất cả mã CK trên sàn
• Không phân biệt chữ HOA/thường
• Thông báo biến động giá tự động

❓ *HỖ TRỢ & LIÊN HỆ*
• Gõ /help để xem lại hướng dẫn
• Liên hệ admin nếu cần trợ giúp thêm

_Bot được phát triển bởi PHOMMASENG EKALAT_
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')