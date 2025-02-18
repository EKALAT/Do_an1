from telegram import Update
from telegram.ext import ContextTypes
import requests
from bs4 import BeautifulSoup


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
