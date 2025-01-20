from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import re

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Welcome to XD bot! Use /hello to greet me, /help to get help, or just send a message to echo it back.'
    )

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Here are the commands you can use:\n/hello - Greet the bot\n/help - Get help information\n/news - View the latest news\n/chungkhoan - Xem tất cả các giá chứng khoản hiện tại\nnSend any message to echo it back.'
    )

# Hello Command
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Xin chào {update.effective_user.first_name}')
    await update.message.reply_text('How can I help you?')

# News Command
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        latest_news = get_all_news()  # Fetch all the latest news for the day
        if latest_news:
            for news in latest_news:
                title = escape_markdown(news['title'])  # Escape special characters in title
                link = news['link']
                message = f"*Title:* [{title}]({link})"
                await update.message.reply_text(message, parse_mode='MarkdownV2')  # Send each news item individually
        else:
            await update.message.reply_text("Không có tin tức mới nào.")
    except Exception as e:
        await update.message.reply_text("Đã xảy ra lỗi khi lấy tin tức.")
        print(f"Error fetching news: {e}")

# Get All News Function
def get_all_news():
    try:
        response = requests.get("https://vnexpress.net/", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            # Find all the news articles on the page
            news_items = soup.find_all("h3", {"class": "title-news"})
            for news in news_items:
                title = news.a.get("title", "Không có tiêu đề")
                link = news.a.get("href", "#")
                news_list.append({'title': title, 'link': link})
            return news_list
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return None

# Escape special characters for MarkdownV2
def escape_markdown(text: str) -> str:
    # List of characters that need to be escaped in MarkdownV2
    escape_chars = r'[_*`\[\]()~>#+-=|{}.!&-]'
    # Escape the special characters properly
    return re.sub(r'([\\`*_{}\[\]()#+\-.!~])', r'\\\1', text)

# Echo Handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Chung Khoan Command
async def chungkhoanchungkhoan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Chức năng chưa được hỗ trợ.")

# Telegram Bot Initialization
app = ApplicationBuilder().token("7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler("chungkhoan", chungkhoanchungkhoan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("Bot is running...")
app.run_polling()
