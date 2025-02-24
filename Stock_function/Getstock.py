from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ContextTypes
import time
from Stock_function.database_handler import DatabaseHandler
from datetime import datetime

EXCLUDED_STOCKS = {"VNXALL", "VNINDEX", "VN30", "HNXUPCOMIND", "HNXINDEX", "HNX30", "HNXIndex", "HNXUpcomIndex"}

# Thêm biến global để lưu instance của DatabaseHandler
db_handler = DatabaseHandler()

async def getstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lấy danh sách mã chứng khoán từ SSI và lưu vào database"""
    browser = None
    try:
        await update.message.reply_text(
            "🔄 *ĐANG CẬP NHẬT DỮ LIỆU*\n\n"
            "• Đang kết nối đến SSI...\n"
            "• Quá trình này có thể mất 1-2 phút\n"
            "• Vui lòng đợi trong giây lát...",
            parse_mode='Markdown'
        )
        
        async with async_playwright() as p:
            # Khởi tạo browser với các tùy chọn
            browser = await p.chromium.launch(
                headless=True,  # Chạy ẩn browser
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            
            # Tạo context với timeout dài hơn
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Tải trang với retry
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    await update.message.reply_text(
                        f"📡 *Đang tải dữ liệu... ({retry_count + 1}/{max_retries})*",
                        parse_mode='Markdown'
                    )
                    
                    await page.goto(
                        "https://iboard.ssi.com.vn/",
                        timeout=60000,
                        wait_until="networkidle"
                    )
                    await page.wait_for_selector(".ag-body-viewport", timeout=30000)
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise Exception(f"Không thể tải trang sau {max_retries} lần thử: {str(e)}")
                    await update.message.reply_text(
                        f"⚠️ *Lần thử {retry_count} thất bại*\n"
                        "Đang thử lại...",
                        parse_mode='Markdown'
                    )
                    await page.reload()

            await update.message.reply_text(
                "✅ *Đã kết nối thành công*\n"
                "Đang thu thập dữ liệu...",
                parse_mode='Markdown'
            )

            # Lấy dữ liệu
            stock_code_elements = await page.locator("//div[contains(@class, 'ag-cell') and contains(@class, 'stock-symbol')]").all()
            stock_codes = []
            for el in stock_code_elements:
                code = await el.inner_text()
                if code not in EXCLUDED_STOCKS:
                    stock_codes.append(code)

            # Lấy tất cả hàng dữ liệu
            rows = await page.query_selector_all(".ag-center-cols-container .ag-row")
            stocks_data = []
            processed_count = 0
            total_stocks = len(stock_codes)

            for i, row in enumerate(rows[6:]):  # Bỏ qua 6 hàng đầu
                if i >= len(stock_codes):
                    continue

                stock_code = stock_codes[i]
                processed_count += 1

                if processed_count % 100 == 0:  # Cập nhật tiến độ mỗi 100 mã
                    await update.message.reply_text(
                        f"📊 *Tiến độ xử lý:* {processed_count}/{total_stocks} mã",
                        parse_mode='Markdown'
                    )
                
                try:
                    # Lấy các thông tin cần thiết
                    price_el = await row.query_selector("[aria-colindex='30']")
                    volume_el = await row.query_selector("[aria-colindex='31']")
                    total_volume_el = await row.query_selector("[aria-colindex='54']")

                    stocks_data.append({
                        "ma_ck": stock_code,
                        "gia": (await price_el.inner_text() if price_el else "N/A").strip(),
                        "klgd": (await volume_el.inner_text() if volume_el else "N/A").strip(),
                        "tongklgd": (await total_volume_el.inner_text() if total_volume_el else "N/A").strip()
                    })
                except Exception as e:
                    print(f"Lỗi khi lấy dữ liệu cho mã {stock_code}: {e}")
                    continue

            if not stocks_data:
                raise Exception("Không tìm thấy dữ liệu chứng khoán")

            # Lưu vào database
            await update.message.reply_text(
                "💾 *Đang lưu dữ liệu vào database...*",
                parse_mode='Markdown'
            )

            if await db_handler.update_stock_data(stocks_data):
                success_message = (
                    "✅ *CẬP NHẬT THÀNH CÔNG*\n\n"
                    f"📊 Tổng số mã: {len(stocks_data)}\n"
                    "⏰ Thời gian: " + datetime.now().strftime("%H:%M:%S %d/%m/%Y") + "\n\n"
                    "💡 *Các lệnh có thể dùng:*\n"
                    "• /allstock - Xem tất cả các mã\n"
                    "• /theodoi <mã> - Theo dõi một mã cụ thể"
                )
                await update.message.reply_text(success_message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "❌ *LỖI CẬP NHẬT*\n\n"
                    "Không thể lưu dữ liệu vào database.\n"
                    "Vui lòng thử lại sau.",
                    parse_mode='Markdown'
                )

    except Exception as e:
        error_message = str(e)
        print(f"Lỗi: {error_message}")
        
        if "timeout" in error_message.lower():
            await update.message.reply_text(
                "⚠️ *LỖI KẾT NỐI*\n\n"
                "Hệ thống đang tải chậm.\n"
                "Vui lòng thử lại sau vài phút.",
                parse_mode='Markdown'
            )
        elif "không thể tải trang" in error_message.lower():
            await update.message.reply_text(
                "⚠️ *KHÔNG THỂ KẾT NỐI*\n\n"
                "Không thể kết nối đến SSI.\n"
                "Vui lòng kiểm tra lại kết nối mạng.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ *LỖI HỆ THỐNG*\n\n"
                "Đã xảy ra lỗi không mong muốn.\n"
                "Vui lòng thử lại sau hoặc liên hệ admin.",
                parse_mode='Markdown'
            )
    
    finally:
        if browser:
            await browser.close()

async def allstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lấy thông tin chứng khoán từ database và hiển thị cho user"""
    try:
        await update.message.reply_text("🔄 Đang lấy dữ liệu từ database...")
        stocks_data = await db_handler.get_current_prices()
        
        if not stocks_data:
            await update.message.reply_text("⚠️ Chưa có dữ liệu chứng khoán trong database!")
            return

        # In số lượng chứng khoán để debug
        print(f"Số lượng chứng khoán sẽ hiển thị: {len(stocks_data)}")

        # Format và gửi kết quả
        message = "📈 *BẢNG GIÁ CHỨNG KHOÁN (Từ Database)*\n"
        message += f"⏰ Cập nhật: {stocks_data[0]['updated_at']}\n"
        message += f"📊 Số lượng: {len(stocks_data)} mã\n\n"
        message += "```\n"
        message += "┌────────┬──────────┬───────────┬────────────┐\n"
        message += "│ MÃ     │    GIÁ   │    KLGD   │   TỔNG KL  │\n"
        message += "├────────┼──────────┼───────────┼────────────┤\n"

        for stock in stocks_data:
            message += "│ {:<6} │ {:>8} │ {:>9} │ {:>10} │\n".format(
                stock["ma_ck"],
                stock["gia"],
                stock["klgd"],
                stock["tongklgd"]
            )

        message += "└────────┴──────────┴───────────┴────────────┘\n"
        message += "```\n"
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ database: {e}")
        await update.message.reply_text("⚠️ Có lỗi xảy ra khi lấy dữ liệu từ database!")

async def chungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /chungkhoan và gửi kết quả cho user"""
    # Gọi trực tiếp getstock thay vì lưu kết quả
    await getstock(update, context)

async def track_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Theo dõi giá chứng khoán theo mã cụ thể"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ *HƯỚNG DẪN THEO DÕI*\n\n"
            "🔍 *Cú pháp:* `/theodoi <mã chứng khoán>`\n"
            "📝 *Ví dụ:* `/theodoi FPT`\n\n"
            "💡 *Lưu ý:*\n"
            "• Chạy /getstock để cập nhật dữ liệu mới\n"
            "• Mã CK không phân biệt chữ HOA/thường\n"
            "• Dữ liệu được cập nhật từ SSI",
            parse_mode='Markdown'
        )
        return

    stock_code = context.args[0].upper()
    
    try:
        await update.message.reply_text(
            f"🔄 *Đang tìm thông tin mã {stock_code}...*",
            parse_mode='Markdown'
        )
        
        stock_data = await db_handler.get_stock_by_code(stock_code)
        
        if not stock_data:
            await update.message.reply_text(
                f"❌ *Không tìm thấy mã {stock_code}*\n\n"
                "💭 *Nguyên nhân có thể:*\n"
                "• Mã chứng khoán không tồn tại\n"
                "• Dữ liệu chưa được cập nhật\n"
                "• Hệ thống đang bảo trì\n\n"
                "✅ *Giải pháp:*\n"
                "1️⃣ Kiểm tra lại mã chứng khoán\n"
                "2️⃣ Chạy /getstock cập nhật dữ liệu\n"
                "3️⃣ Thử lại sau vài phút",
                parse_mode='Markdown'
            )
            return

        # Phân tích xu hướng giá
        price = float(stock_data["gia"].replace(",", ""))
        trend = "🔴" if price < 0 else "🟢" if price > 0 else "⚪"
        
        # Format thông điệp với màu sắc và biểu tượng
        message = (
            f"{'='*35}\n"
            f"📊 *THÔNG TIN MÃ {stock_code}*\n"
            f"{'='*35}\n\n"
            f"⏰ *Cập nhật:* {stock_data['updated_at']}\n\n"
            f"{trend} *GIÁ HIỆN TẠI:*\n"
            f"└─ {stock_data['gia']} VNĐ\n\n"
            f"📈 *KHỐI LƯỢNG GIAO DỊCH:*\n"
            f"└─ {stock_data['klgd']} CP\n\n"
            f"📊 *TỔNG KHỐI LƯỢNG:*\n"
            f"└─ {stock_data['tongklgd']} CP\n\n"
            f"{'─'*35}\n"
            "*CHI TIẾT GIAO DỊCH*\n"
            "```\n"
            "┌────────┬──────────┬───────────┬────────────┐\n"
            "│   MÃ   │    GIÁ   │    KLGD   │   TỔNG KL  │\n"
            "├────────┼──────────┼───────────┼────────────┤\n"
            "│ {:<6} │ {:>8} │ {:>9} │ {:>10} │\n".format(
                stock_data["ma_ck"],
                stock_data["gia"],
                stock_data["klgd"],
                stock_data["tongklgd"]
            ) +
            "└────────┴──────────┴───────────┴────────────┘\n"
            "```\n"
            f"{'─'*35}\n\n"
            "💡 *THAO TÁC NHANH:*\n"
            "• /getstock - Cập nhật dữ liệu\n"
            "• /allstock - Xem tất cả mã\n"
            "• /theodoi <mã> - Theo dõi mã khác\n\n"
            "🔔 Để nhận thông báo khi giá thay đổi,\n"
            "sử dụng lệnh /alert <mã> <giá>"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        print(f"Lỗi khi theo dõi mã {stock_code}: {e}")
        await update.message.reply_text(
            "❌ *LỖI HỆ THỐNG*\n\n"
            "😢 Không thể lấy thông tin chứng khoán.\n"
            "🔄 Vui lòng thử lại sau hoặc liên hệ admin.\n\n"
            "💡 *Mẹo:* Chạy /getstock để cập nhật lại dữ liệu",
            parse_mode='Markdown'
        )