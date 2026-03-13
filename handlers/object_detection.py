# bot/handlers/object_detection.py
import os
import glob
import cv2
from telegram import InputFile
from telegram.error import TimedOut
from ultralytics import YOLO

# --- Загружаем модель YOLOv8 (CPU) один раз при импорте ---
model = YOLO(os.path.join("models", "yolov8n.pt"))

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

    try:
        with open(result_jpg, "rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
        await status_msg.edit_text("Detected image")
    except TimedOut:
        await status_msg.edit_text("Error: sending photo timed out")