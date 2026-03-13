from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, InputFile
from dotenv import load_dotenv
from ultralytics import YOLO
from deepface import DeepFace
import os
import cv2
import glob
import asyncio
from telegram.error import TimedOut

load_dotenv()
TOKEN = os.environ.get("TOKEN_Family")

# --- Загружаем модель YOLOv8 (CPU) ---
model = YOLO(os.path.join("models", "yolov8n.pt"))

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

    color = (0, 0, 255)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.5, img.shape[0] / 1000)
    thickness = max(1, int(font_scale * 2))

    for idx, face in enumerate(results):
        x, y, w, h = face["region"]["x"], face["region"]["y"], face["region"]["w"], face["region"]["h"]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

        print(f"Face {idx + 1}:")
        lines = [
            f"Gender: {face['dominant_gender']}",
            f"Age: {face['age']}",
            f"Emotion: {face['dominant_emotion']}",
            f"Race: {face['dominant_race']}"
        ]
        for text in lines:
            print("  ", text)

        for i, text in enumerate(lines):
            text_y = y - 10 - i*25
            if text_y < 0:
                text_y = y + 15 + i*25
            cv2.putText(img, text, (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

    return img, results

# --- Команды ---
async def start(update, context):
    await update.message.reply_text("Choose a function:", reply_markup=reply_markup)

async def help_text(update, context):
    await update.message.reply_text(update.message.text)

# --- Очистка папки пользователя ---
def cleanup_user_images(user_id, keep_last=5):
    user_dir = f"images/{user_id}"
    files = sorted(
        glob.glob(os.path.join(user_dir, "*")),
        key=os.path.getmtime
    )
    for f in files[:-keep_last]:
        os.remove(f)

# --- Object detection ---
async def object_detection(update, context, image_path):
    # --- промежуточное сообщение ---
    status_msg = await update.message.reply_text("Detecting objects...")

    results_yolo = model.predict(
        image_path,
        conf=0.5,
        save=True,
        project="runs/detect",
        name=str(update.message.from_user.id),
        exist_ok=True,
        device="cpu",
        imgsz=640
    )

    result_path = os.path.join("runs/detect", str(update.message.from_user.id), os.path.basename(image_path))
    if not os.path.exists(result_path):
        await status_msg.edit_text("Error: result not found")
        return

    img = cv2.imread(result_path)
    if img is None:
        await status_msg.edit_text("Error: result image unreadable")
        return

    max_dim = 700
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)))

    user_dir = f"images/{update.message.from_user.id}"
    os.makedirs(user_dir, exist_ok=True)
    result_jpg = os.path.join(user_dir, "detected_" + os.path.basename(result_path))
    cv2.imwrite(result_jpg, img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    cleanup_user_images(update.message.from_user.id, keep_last=5)

    # --- Отправка изображения с подписью и замена текста ---
    try:
        with open(result_jpg, "rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
        # заменяем промежуточное сообщение на итоговую подпись
        await status_msg.edit_text("Detected image")
    except TimedOut:
        await status_msg.edit_text("Error: sending photo timed out")

# --- Age/Emotion/Race ---
async def age_emotion_race(update, context, image_path):
    status_msg = await update.message.reply_text("Analyzing age, emotion, race...")

    annotated_img, results = await analyze_face(image_path)
    if annotated_img is None:
        await status_msg.edit_text("Error: analysis failed")
        return

    user_dir = f"images/{update.message.from_user.id}"
    os.makedirs(user_dir, exist_ok=True)
    result_path = os.path.join(user_dir, "annotated_" + os.path.basename(image_path))

    max_dim = 700
    h, w = annotated_img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        annotated_img = cv2.resize(annotated_img, (int(w*scale), int(h*scale)))

    cv2.imwrite(result_path, annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    cleanup_user_images(update.message.from_user.id, keep_last=5)

    try:
        with open(result_path, "rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
        # заменяем промежуточное сообщение на итоговую подпись
        await status_msg.edit_text("Analyzed image")
    except TimedOut:
        await status_msg.edit_text("Error: sending photo timed out")

# --- Текстовый хэндлер ---
async def text_handler(update, context):
    text = update.message.text
    if text == "Object detection":
        context.user_data['mode'] = 'yolo'
        await update.message.reply_text("Send a photo for object detection")
    elif text == "Age/Emotion/Race":
        context.user_data['mode'] = 'face'
        await update.message.reply_text("Send a photo for age/emotion/race analysis")
    else:
        await help_text(update, context)

# --- Общий хэндлер фото ---
async def photo_handler(update, context):
    if not update.message.photo:
        await update.message.reply_text("Please send a photo first")
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
    app = (
        Application.builder()
        .token(TOKEN)
        .read_timeout(180)
        .write_timeout(180)
        .connect_timeout(180)
        .pool_timeout(180)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

if __name__ == "__main__":
    main()