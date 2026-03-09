from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from ultralytics import YOLO
from deepface import DeepFace
import os
import cv2
import numpy as np

load_dotenv()
TOKEN = os.environ.get("TOKEN")

# --- Загружаем модель YOLOv8 (CPU) ---
model = YOLO("yolov8n.pt")

print('Bot started...')

# --- Кнопки ---
keyboard = [
    ["Object detection"],
    ["Age/Emotion/Race"],
    ["Help"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Функция DeepFace ---
async def analyze_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None, None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = DeepFace.analyze(
        img_path=img_rgb,
        actions=["age", "gender", "emotion", "race"],
        detector_backend="retinaface",
        enforce_detection=False
    )

    # --- Добавляем рамки и текст через OpenCV ---
    color = (0, 0, 255)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.5, img.shape[0] / 1000)
    thickness = max(1, int(font_scale * 2))

    for idx, face in enumerate(results):
        x, y, w, h = face["region"]["x"], face["region"]["y"], face["region"]["w"], face["region"]["h"]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

        # --- Текст для консоли ---
        print(f"Face {idx + 1}:")
        lines = [
            f"Gender: {face['dominant_gender']}",
            f"Age: {face['age']}",
            f"Emotion: {face['dominant_emotion']}",
            f"Race: {face['dominant_race']}"
        ]
        for text in lines:
            print("  ", text)

        # --- Текст на изображении с проверкой верхнего края ---
        for i, text in enumerate(lines):
            text_y = y - 10 - i*25  # стандартная позиция сверху рамки
            if text_y < 0:
                # если текст не помещается сверху, рисуем внутри рамки
                text_y = y + 15 + i*25
            cv2.putText(img, text, (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

    return img, results

# --- Команды ---
async def start(update, context):
    await update.message.reply_text("Choose a function:", reply_markup=reply_markup)

async def help_text(update, context):
    await update.message.reply_text(update.message.text)

# --- Object detection ---
async def object_detection(update, context, image_path):
    my_message = await update.message.reply_text("Photo received. Detecting objects...")

    results_yolo = model.predict(
        image_path,
        conf=0.5,
        save=True,
        project="runs/detect",
        name=str(update.message.from_user.id),
        exist_ok=True
    )

    result_path = os.path.join("runs/detect", str(update.message.from_user.id), os.path.basename(image_path))
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=my_message.message_id)

    if os.path.exists(result_path):
        await update.message.reply_text("Object detection complete")
        with open(result_path, "rb") as img:
            await update.message.reply_photo(img)
    else:
        await update.message.reply_text("Error: result not found.")

# --- Age/Emotion/Race ---
async def age_emotion_race(update, context, image_path):
    my_message = await update.message.reply_text("Analyzing age, emotion, race...")

    annotated_img, results = await analyze_face(image_path)

    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=my_message.message_id)

    if annotated_img is not None:
        result_path = os.path.join(f"images/{update.message.from_user.id}", "annotated_" + os.path.basename(image_path))
        cv2.imwrite(result_path, annotated_img)
        with open(result_path, "rb") as img:
            await update.message.reply_photo(img)
        await update.message.reply_text("Analysis complete.")
    else:
        await update.message.reply_text("Error: analysis failed.")

# --- Текстовый хэндлер ---
async def text_handler(update, context):
    text = update.message.text
    if text == "Object detection":
        context.user_data['mode'] = 'yolo'
        await update.message.reply_text("Send a photo for object detection.")
    elif text == "Age/Emotion/Race":
        context.user_data['mode'] = 'face'
        await update.message.reply_text("Send a photo for age/emotion/race analysis.")
    else:
        await help_text(update, context)

# --- Общий хэндлер фото ---
async def photo_handler(update, context):
    if not update.message.photo:
        await update.message.reply_text("Please send a photo first.")
        return

    user_id = update.message.from_user.id
    user_dir = f"images/{user_id}"
    os.makedirs(user_dir, exist_ok=True)

    new_file = await update.message.photo[-1].get_file()
    image_name = os.path.basename(new_file.file_path)
    image_path = os.path.join(user_dir, image_name)
    await new_file.download_to_drive(image_path)

    mode = context.user_data.get('mode', 'yolo')
    if mode == 'yolo':
        await object_detection(update, context, image_path)
    elif mode == 'face':
        await age_emotion_race(update, context, image_path)

# --- Основная функция ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

if __name__ == "__main__":
    main()