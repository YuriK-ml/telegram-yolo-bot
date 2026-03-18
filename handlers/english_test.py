# bot/handlers/english_test.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from config.users import get_users_by_role, get_user_username
from config.modes import get_mode_label   # ← ДОБАВИЛИ
from config.test_accounts import TEST_USERS, LOGIN_URL_TEMPLATE

async def english_test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    """
    Обработчик кнопки 'English Test'.
    Назначает пользователю тестовый аккаунт и отправляет ссылку + пароль.
    """

    context.user_data["mode"] = "english_test"

    # --- получаем отображаемое имя режима ---
    mode_label = get_mode_label(context.user_data.get("mode"))

    tg_id = update.message.from_user.id

    # --- ищем, закреплен ли аккаунт за этим пользователем ---
    user_account = None
    for acc in TEST_USERS:
        if acc["telegram_id"] == tg_id:
            user_account = acc
            break

    # --- если нет закрепленного, ищем свободный ---
    if not user_account:
        free_accounts = [acc for acc in TEST_USERS if not acc["in_use"]]

        if free_accounts:
            user_account = free_accounts[0]
        else:
            # нет свободных → ищем самый давно использованный и переназначаем
            user_account = min(TEST_USERS, key=lambda x: x["last_used"] or datetime.min)

        # закрепляем за текущим пользователем
        user_account["telegram_id"] = tg_id
        user_account["in_use"] = True
        user_account["last_used"] = datetime.now()

    # --- формируем ссылку для кнопки ---
    login_link = LOGIN_URL_TEMPLATE.format(email=user_account["email"])

    # ===================== ДОБАВЛЕННЫЙ БЛОК (ЛОГ ДЛЯ УЧИТЕЛЯ) =====================
    user = update.message.from_user

    sender_name = user.first_name
    if user.last_name:
        sender_name += f" {user.last_name}"
    if user.username:
        sender_name += f" (@{user.username})"

    system_name = user_account["system_name"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    teachers = get_users_by_role("teacher")

    log_message = (
        f"🟡 English Test STARTED  Time: {timestamp}\n"
        f"User: {sender_name}  Login in ProgressMe: {system_name}"        
    )

    for teacher_id in teachers:
        await context.bot.send_message(
            chat_id=teacher_id,
            text=log_message
        )
    # ===================== КОНЕЦ ДОБАВЛЕННОГО БЛОКА =====================

    # --- формируем сообщение ---

    # Old English version
    # text = (
    #     f"📚 *English Test*\n\n"
    #     f"Password: `{user_account['password']}`\n\n"
    #     "Press the button below to open the test.\n\n"
    #     "After finishing the test, send your result here.\n"
    #     "You can send:\n"
    #     "• text message with your score\n"
    #     "• screenshot of the result\n\n"
    #     "🟢 *Feedback mode enabled*"
    # )

    text = (
        f"📚 *English Test*\n\n"
        f"🟢 Mode: {mode_label}\n\n"
        # "Press the button below to open the test.\n"
        "Кликните на кнопку под сообщением для перехода в тест.\n"
        f"При необходимости укажите пароль: `{user_account['password']}`\n\n"
        "После прохождения теста вы можете отправить\n"
        "текстовое сообщение или фотографию преподавателю.\n\n"
        "🟢 Для выхода из режима обратной связи - выберите любой пункт в меню"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Открыть Тест / Open Test 🔥", url=login_link)],
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def forward_test_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пересылка результата теста преподавателю.
    Отображаем имя телеграм + имя в системе обучения.
    Поддерживает текст и фото.
    """

    user = update.message.from_user

    sender_name = user.first_name
    if user.last_name:
        sender_name += f" {user.last_name}"
    if user.username:
        sender_name += f" (@{user.username})"

    # находим аккаунт пользователя
    user_account = next((acc for acc in TEST_USERS if acc["telegram_id"] == user.id), None)
    system_name = user_account["system_name"] if user_account else "unknown"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"📊 English test result from {sender_name} [{timestamp}]\nLogin in ProgressMe: {system_name}"

    teachers = get_users_by_role("teacher")

    if update.message.photo:

        for teacher_id in teachers:

            teacher_username = get_user_username(teacher_id)

            await context.bot.send_message(chat_id=teacher_id, text=header)

            await context.bot.forward_message(
                chat_id=teacher_id,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

            print(f"[EnglishTest] TIME:{timestamp} FROM:{sender_name} ({system_name}) PHOTO SENT TO:{teacher_username}")

    elif update.message.text:

        for teacher_id in teachers:

            teacher_username = get_user_username(teacher_id)

            await context.bot.send_message(
                chat_id=teacher_id,
                text=f"{header}\n\n{update.message.text}"
            )

            print(f"[EnglishTest] TIME:{timestamp} FROM:{sender_name} ({system_name}) TEXT:{update.message.text} TO:{teacher_username}")

    else:

        await update.message.reply_text(
            "Unsupported format. Please send text or screenshot."
        )

        return

    teacher_list = ", ".join([get_user_username(t) for t in teachers])

    # --- сбрасываем режим ---
    # context.user_data["mode"] = None
    await update.message.reply_text(
        f"✅ Result forwarded to teacher(s): {teacher_list} [{timestamp}]"
    )