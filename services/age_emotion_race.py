# age_emotion_race.py
import cv2
import numpy as np
from deepface import DeepFace

def analyze_face(image_path):
    """
    Analyze face(s) in an image for age, gender, emotion, race.
    Returns annotated image and results dictionary.
    """
    # --- Загружаем изображение ---
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # --- Конвертируем в RGB для DeepFace ---
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # --- Распознаем лица и анализируем ---
    results = DeepFace.analyze(
        img_path=img_rgb,
        actions=["age", "gender", "emotion", "race"],
        detector_backend="retinaface",
        enforce_detection=False
    )

    # --- Цвет и стиль текста/рамок ---
    color = (0, 0, 255)  # красный (BGR)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.5, img.shape[0] / 1000)
    thickness = max(1, int(font_scale * 2))

    # --- Добавляем рамки, текст и выводим данные ---
    for idx, face in enumerate(results):
        x, y, w, h = face["region"]["x"], face["region"]["y"], face["region"]["w"], face["region"]["h"]
        # Рисуем рамку
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

        # Текстовые данные
        lines = [
            f"Gender: {face['dominant_gender']}",
            f"Age: {face['age']}",
            f"Emotion: {face['dominant_emotion']}",
            f"Race: {face['dominant_race']}"
        ]

        # Печатаем текст в консоль для отладки
        print(f"Face {idx + 1}:")
        for text in lines:
            print("  ", text)

        # Рисуем текст над рамкой (сверху)
        for i, text in enumerate(lines):
            cv2.putText(img, text, (x, max(y - 10 - i*25, 0)), font, font_scale, color, thickness, cv2.LINE_AA)

    return img, results

# --- Тестирование ---
if __name__ == "__main__":
    test_image = "images_age\YuriK.jpeg"  # Путь к тестовому изображению
    annotated_img, results = analyze_face(test_image)

    # --- Показываем результат ---
    cv2.imshow("Annotated", annotated_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()