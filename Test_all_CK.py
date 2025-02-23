from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ContextTypes
import time

EXCLUDED_STOCKS = {"VNXALL", "VNINDEX", "VN30", "HNXUPCOMIND", "HNXINDEX", "HNX30", "HNXIndex", "HNXUpcomIndex"}

async def getstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lấy danh sách mã chứng khoán từ SSI và trả về cho user"""
    await update.message.reply_text("🔄 Đang tải dữ liệu chứng khoán...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1000, "height": 1000})
            page = await context.new_page()
            await page.goto("https://iboard.ssi.com.vn/")
            
            # Chờ trang tải
            await page.wait_for_timeout(5000)  # Chờ 5 giây
            
            # Chờ cho dữ liệu tải
            await page.wait_for_selector(".ag-body-viewport")
            
            # Lấy danh sách mã chứng khoán
            stock_code_elements = await page.locator("//div[contains(@class, 'ag-cell') and contains(@class, 'stock-symbol')]").all()
            stock_codes = []
            for el in stock_code_elements:
                code = await el.inner_text()
                if code not in EXCLUDED_STOCKS:
                    stock_codes.append(code)

            # Lấy tất cả hàng dữ liệu
            rows = await page.query_selector_all(".ag-center-cols-container .ag-row")
            stocks_data = []

            for i, row in enumerate(rows[6:]):  # Bỏ qua 6 hàng đầu
                if i >= len(stock_codes):
                    continue

                stock_code = stock_codes[i]
                
                # Lấy giá thấp, cao và khối lượng
                try:
                    # Lấy giá thấp
                    low_price_el = await row.query_selector(".ag-cell-color-ref")
                    low_price = await low_price_el.inner_text() if low_price_el else "N/A"
                    
                    # Lấy giá cao
                    high_price_el = await row.query_selector(".ag-cell-color-up")
                    high_price = await high_price_el.inner_text() if high_price_el else "N/A"
                    
                    # Lấy khối lượng
                    volume_el = await row.query_selector("[aria-colindex='54']")
                    volume = await volume_el.inner_text() if volume_el else "N/A"

                    stocks_data.append({
                        "ma_ck": stock_code,
                        "cao": high_price.strip(),
                        "thap": low_price.strip(),
                        "klgd": volume.strip()
                    })
                except Exception as e:
                    print(f"Lỗi khi lấy dữ liệu cho mã {stock_code}: {e}")
                    continue

            await browser.close()

            if not stocks_data:
                await update.message.reply_text("⚠️ Không tìm thấy dữ liệu chứng khoán!")
                return

            # Tạo header cho bảng
            message = "📊 *BẢNG GIÁ CHỨNG KHOÁN*\n\n"
            message += "`{:<6} | {:>8} | {:>8} | {:>12}`\n".format("Mã CK", "Giá Thấp", "Giá Cao", "Tổng KL")
            message += "`" + "-"*40 + "`\n"

            # Chia thành nhiều tin nhắn nếu danh sách quá dài
            chunk_size = 30  # Số mã trong mỗi tin nhắn
            
            for i in range(0, len(stocks_data), chunk_size):
                chunk = stocks_data[i:i + chunk_size]
                chunk_message = message if i == 0 else ""  # Chỉ hiện tiêu đề ở tin nhắn đầu
                
                for stock in chunk:
                    chunk_message += "`{:<6} | {:>8} | {:>8} | {:>12}`\n".format(
                        stock["ma_ck"],
                        stock["thap"],
                        stock["cao"],
                        stock["klgd"]
                    )
                
                await update.message.reply_text(chunk_message, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu chứng khoán: {e}")
        await update.message.reply_text("⚠️ Có lỗi xảy ra khi lấy dữ liệu chứng khoán!")

async def chungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /chungkhoan và gửi kết quả cho user"""
    await update.message.reply_text("🔄 Đang tải dữ liệu chứng khoán...")
    
    stocks = await getstock(update, context)
    if not stocks:
        await update.message.reply_text("⚠️ Không thể lấy dữ liệu chứng khoán!")
        return

    message = "📊 *Danh sách mã chứng khoán:*\n\n"
    for i, stock in enumerate(stocks, 1):
        message += f"{i}. `{stock}`\n"

    await update.message.reply_text(message, parse_mode="Markdown")
