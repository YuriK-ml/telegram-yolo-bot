from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
import os

# --- Импорты хэндлеров ---
from handlers.text_commands import start, help_text as default_text_handler
from handlers.photo_handler import photo_handler
from handlers.button_handlers import object_detection_handler, age_emotion_race_handler
from handlers.english_test import english_test_handler, forward_test_result
from config.users_local import USERS, get_users_by_role
from functools import partial

load_dotenv()
TOKEN = os.environ.get("TOKEN_Family")

# --- Список кнопок ---
keyboard = [
    ["Object detection"],
    ["Age/Emotion/Race"],
    ["English Test"],
    ["Help"]
]

# --- ReplyKeyboardMarkup ---
main_menu_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Словарь кнопка → хэндлер ---
button_actions = {
    "Object detection": lambda u, c: object_detection_handler(u, c, main_menu_keyboard),
    "Age/Emotion/Race": lambda u, c: age_emotion_race_handler(u, c, main_menu_keyboard),
    "English Test": lambda u, c: english_test_handler(u, c, main_menu_keyboard),
    "Help": lambda u, c: default_text_handler(u, c, main_menu_keyboard)
}

# --- Динамический текстовый хэндлер для кнопок ---
async def text_handler(update, context):
    text = update.message.text

    if text in button_actions:
        # ✅ Если это НЕ кнопка English Test → сброс режима
        if text != "English Test":
            context.user_data["mode"] = None

        handler = button_actions[text]
        await handler(update, context)
        return

    # ✅ если пользователь в режиме теста → обрабатываем ответ
    if context.user_data.get("mode") == "english_test":
        await forward_test_result(update, context)
        return

    # ✅ иначе игнорируем текст
    return

# --- Фото (анализ или результат теста) ---
async def photo_router(update, context):

    # если пользователь в режиме English Test
    if context.user_data.get("mode") == "english_test":
        await forward_test_result(update, context)
    else:
        await photo_handler(update, context)


def main():

    app = (
        Application.builder()
        .token(TOKEN)
        .read_timeout(180)
        .write_timeout(180)
        .connect_timeout(180)
        .pool_timeout(180)
        .build()
    )

    # --- Команда /start ---
    # Используем partial, чтобы передать main_menu_keyboard в start
    app.add_handler(CommandHandler(
        "start",
        partial(start, main_menu_keyboard=main_menu_keyboard)
    ))

    # --- Текстовые сообщения ---
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    # --- Фото ---
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()