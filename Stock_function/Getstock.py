from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ContextTypes
import time

EXCLUDED_STOCKS = {"VNXALL", "VNINDEX", "VN30", "HNXUPCOMIND", "HNXINDEX", "HNX30", "HNXIndex", "HNXUpcomIndex"}

async def getstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lấy danh sách mã chứng khoán từ SSI và trả về cho user"""
    browser = None
    try:
        async with async_playwright() as p:
            # Thông báo đang tải
            await update.message.reply_text("🔄 Đang tải dữ liệu chứng khoán...")
            
            # Khởi tạo browser với các tùy chọn
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            
            # Tạo context với timeout dài hơn và tắt một số tính năng không cần thiết
            context = await browser.new_context(
                viewport={"width": 1000, "height": 1000},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                bypass_csp=True,
                ignore_https_errors=True
            )
            
            page = await context.new_page()
            
            # Tải trang với retry
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
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
                    await update.message.reply_text(f"⚠️ Lần thử {retry_count}: Đang thử lại...")
                    await page.reload()

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

            for i, row in enumerate(rows[6:]):  # Bỏ qua 6 hàng đầu
                if i >= len(stock_codes):
                    continue

                stock_code = stock_codes[i]
                
                # Lấy giá thấp, cao và khối lượng
                try:
                    # Lấy giá 
                    price_el = await row.query_selector("[aria-colindex='30']")
                    price = await price_el.inner_text() if price_el else "N/A"
                    
                    # Lấy khối lượng
                    volume_el = await row.query_selector("[aria-colindex='31']")
                    volume = await volume_el.inner_text() if volume_el else "N/A"
                    
                    # Lấy Tổng khối lượng
                    total_volume_el = await row.query_selector("[aria-colindex='54']")
                    total_volume = await total_volume_el.inner_text() if total_volume_el else "N/A"

                    stocks_data.append({
                        "ma_ck": stock_code,
                        "gia": price.strip(),
                        "klgd": volume.strip(),
                        "tongklgd": total_volume.strip()
                    })
                except Exception as e:
                    print(f"Lỗi khi lấy dữ liệu cho mã {stock_code}: {e}")
                    continue

            if not stocks_data:
                raise Exception("Không tìm thấy dữ liệu chứng khoán")

            # Format và gửi kết quả
            message = "📈 *BẢNG GIÁ CHỨNG KHOÁN REALTIME*\n"
            message += "⏰ Cập nhật: " + time.strftime("%H:%M:%S %d/%m/%Y") + "\n\n"
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
        error_message = str(e)
        print(f"Lỗi: {error_message}")
        if "timeout" in error_message.lower():
            await update.message.reply_text("⚠️ Hệ thống đang tải chậm. Vui lòng thử lại sau!")
        elif "không thể tải trang" in error_message.lower():
            await update.message.reply_text("⚠️ Không thể kết nối đến SSI. Vui lòng thử lại sau!")
        elif "không tìm thấy dữ liệu" in error_message.lower():
            await update.message.reply_text("⚠️ Không tìm thấy dữ liệu chứng khoán!")
        else:
            await update.message.reply_text("⚠️ Có lỗi xảy ra. Vui lòng thử lại sau!")
    
    finally:
        if browser:
            await browser.close()

async def chungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /chungkhoan và gửi kết quả cho user"""
    # Gọi trực tiếp getstock thay vì lưu kết quả
    await getstock(update, context)