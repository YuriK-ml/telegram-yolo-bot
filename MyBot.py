from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from ultralytics import  YOLO
import os

load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Загружаем модель YOLOv8 (CPU)
model = YOLO("yolov8n.pt")  # можно выбрать yolov8n, yolov8s, yolov8m, yolov8l, yolov8x

print('Бот запущен...')

async def start(update, context):
    keyboard = [
        ["Object detection"],
        ["Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите функцию:", reply_markup=reply_markup)

async def help_text(update, context):
    await update.message.reply_text(update.message.text)

async def object_detection(update, context):
    user_id = update.message.from_user.id

    # сообщение о начале распознавания
    my_message = await update.message.reply_text(
        "Мы получили фотографию. Идет распознавание объектов..."
    )

    # Создаем папку для пользователя
    user_dir = f"images/{user_id}"
    os.makedirs(user_dir, exist_ok=True)

    # Сохраняем присланное фото
    new_file = await update.message.photo[-1].get_file()
    image_name = os.path.basename(new_file.file_path)
    image_path = os.path.join(user_dir, image_name)
    await new_file.download_to_drive(image_path)

    # YOLO распознавание
    results = model.predict(
        image_path,
        conf=0.5,
        save=True,
        project="runs/detect",
        name=str(user_id),
        exist_ok=True
    )

    # путь к результату
    image_name = os.path.basename(image_path)
    result_path = os.path.join("runs/detect", str(user_id), image_name)

    # удаляем сообщение "идет распознавание"
    await context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=my_message.message_id
    )

    # отправляем результат
    if os.path.exists(result_path):
        await update.message.reply_text("Распознавание объектов завершено")
        with open(result_path, "rb") as img:
            await update.message.reply_photo(img)
    else:
        await update.message.reply_text("Ошибка: результат не найден.")


async def text_handler(update, context):
    text = update.message.text
    if text == "Object detection":
        # Проверяем, есть ли фото в сообщении
        if update.message.photo:
            await object_detection(update, context)
        else:
            await update.message.reply_text("Пожалуйста, сначала отправьте фото.")
    else:
        await help_text(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, object_detection))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()