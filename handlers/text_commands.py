# handlers/text_commands.py
from telegram.ext import ContextTypes
from telegram import Update

# --- Стартовое сообщение ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    text = (
        "🤖 *AI Vision Bot*\n\n"
        "I can analyze photos using artificial intelligence.\n\n"
        "Available modes:\n"
        "🔎 *Object detection*\n"
        "🙂 *Face analysis*\n"
        "📚 *English Test*\n\n"
        "Choose a mode below and send a photo."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard,
        parse_mode="Markdown"
    )


# --- Хэндлер Help ---
async def help_text(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    text = (
        "🤖 *AI Vision Bot*\n\n"
        "This bot uses artificial intelligence to analyze images "
        "and provide access to the English test.\n\n"
        "Available modes:\n"
        "🔎 *Object detection*\n"
        "🙂 *Face analysis*\n"
        "📚 *English Test*\n\n"
        "Choose a mode below to get started."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard,
        parse_mode="Markdown"
    )