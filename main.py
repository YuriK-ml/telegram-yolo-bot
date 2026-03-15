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

load_dotenv()
TOKEN = os.environ.get("TOKEN_Family")

# --- Пользователи системы ---
# роли можно комбинировать
USERS = {
    1387433465: {
        "username": "@YuriKorobkov",
        "roles": ["admin", "teacher"]
    },
    8527953030: {
        "username": "@Anna",
        "roles": ["teacher"]
    }
}

# --- Универсальная функция получения пользователей по роли ---
def get_users_by_role(role):
    return [
        user_id
        for user_id, data in USERS.items()
        if role in data["roles"]
    ]


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
    handler = button_actions.get(text)

    if handler:
        await handler(update, context)

    else:
        # Если пользователь присылает текст как результат теста
        if context.user_data.get("mode") == "english_test":
            await forward_test_result(update, context)
        else:
            await default_text_handler(update, context, main_menu_keyboard)


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
    app.add_handler(CommandHandler("start", lambda u, c: start(u, c, main_menu_keyboard)))

    # --- Текстовые сообщения ---
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    # --- Фото ---
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()