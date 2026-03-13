# handlers/button_handlers.py
from telegram import Update
from telegram.ext import ContextTypes

from handlers.object_detection import object_detection
from handlers.face_analysis import age_emotion_race
from handlers.english_test import english_test_handler
from handlers.text_commands import help_text

async def object_detection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    context.user_data['mode'] = 'yolo'
    await update.message.reply_text(
        "Send a photo for object detection",
        reply_markup=main_menu_keyboard
    )

async def age_emotion_race_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, main_menu_keyboard):
    context.user_data['mode'] = 'face'
    await update.message.reply_text(
        "Send a photo for age/emotion/race analysis",
        reply_markup=main_menu_keyboard
    )