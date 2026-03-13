import os

from handlers.object_detection import object_detection
from handlers.face_analysis import age_emotion_race


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