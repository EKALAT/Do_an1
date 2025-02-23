from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a list of available games to download"""
    keyboard = [
        [
            InlineKeyboardButton("Minecraft", url="https://www.minecraft.net/download"),
            InlineKeyboardButton("Roblox", url="https://www.roblox.com/download")
        ],
        [
            InlineKeyboardButton("Among Us", url="https://www.innersloth.com/games/among-us/"),
            InlineKeyboardButton("Fortnite", url="https://www.epicgames.com/fortnite/download")
        ],
        [
            InlineKeyboardButton("Steam", url="https://store.steampowered.com/about/"),
            InlineKeyboardButton("Epic Games", url="https://store.epicgames.com/download")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎮 *Popular Games Download Links:*\n\n"
        "Choose a game or platform to download:\n"
        "• Minecraft\n"
        "• Roblox\n"
        "• Among Us\n"
        "• Fortnite\n"
        "• Steam Platform\n"
        "• Epic Games Platform",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    ) 