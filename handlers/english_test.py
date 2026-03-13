# bot/handlers/english_test.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

# импортируем словарь пользователей и функции из main/config
from config.users import USERS, get_users_by_role, get_user_username


async def english_test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    """
    Обработчик кнопки 'English Test'.
    Включает режим отправки результата теста.
    """

    # включаем режим "english_test"
    context.user_data["mode"] = "english_test"

    test_link = "https://progressme.ru/classroom/2165632/lesson/16607262/section/81375252"

    text = (
        "📚 *English Test*\n\n"
        "Take the test using the link below:\n\n"
        f"{test_link}\n\n"
        "After finishing the test, send your result here.\n"
        "You can send:\n"
        "• text message with your score\n"
        "• screenshot of the result\n\n"
        "The result will be forwarded to your teacher(s).\n\n"
        "🟢 *Feedback mode enabled*\n"
        "Send your result."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard,
        parse_mode="Markdown"
    )


async def forward_test_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пересылка результата теста преподавателю.
    Поддерживает текст и фото.
    """

    user = update.message.from_user

    # имя отправителя
    sender_name = user.first_name
    if user.last_name:
        sender_name += f" {user.last_name}"
    if user.username:
        sender_name += f" (@{user.username})"

    # временной штамп
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"📊 English test result from {sender_name} [{timestamp}]"

    # получаем всех учителей
    teachers = get_users_by_role("teacher")

    # --- если пришло фото ---
    if update.message.photo:

        for teacher_id in teachers:

            teacher_username = get_user_username(teacher_id)

            # отправляем заголовок
            await context.bot.send_message(
                chat_id=teacher_id,
                text=header
            )

            # пересылаем само фото
            await context.bot.forward_message(
                chat_id=teacher_id,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

            # лог в консоль
            print("\n[EnglishTest]")
            print(f"TIME: {timestamp}")
            print(f"FROM: {sender_name}")
            print("PHOTO SENT")
            print(f"TO: {teacher_username}")

    # --- если пришёл текст ---
    elif update.message.text:

        for teacher_id in teachers:

            teacher_username = get_user_username(teacher_id)

            await context.bot.send_message(
                chat_id=teacher_id,
                text=f"{header}\n\n{update.message.text}"
            )

            # лог в консоль
            print("\n[EnglishTest]")
            print(f"TIME: {timestamp}")
            print(f"FROM: {sender_name}")
            print(f"TEXT: {update.message.text}")
            print(f"TO: {teacher_username}")

    else:

        await update.message.reply_text(
            "Unsupported format. Please send text or screenshot."
        )
        return

    # уведомление отправителю
    teacher_list = ", ".join([get_user_username(t) for t in teachers])
    await update.message.reply_text(
        f"✅ Result forwarded to teacher(s): {teacher_list} [{timestamp}]"
    )
