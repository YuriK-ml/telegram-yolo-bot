# bot/handlers/face_analysis.py
import os
import cv2
import glob
from telegram import InputFile
from telegram.error import TimedOut
from deepface import DeepFace

# --- Анализ лица через DeepFace ---
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

# --- Очистка папки пользователя (повтор для модуля) ---
def cleanup_user_images(user_id, keep_last=5):
    user_dir = f"images/{user_id}"
    files = sorted(
        glob.glob(os.path.join(user_dir, "*")),
        key=os.path.getmtime
    )
    for f in files[:-keep_last]:
        os.remove(f)

# --- Функция Age/Emotion/Race ---
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