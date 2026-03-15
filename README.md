# AgeBot

## Описание (на русском)
AgeBot — это развлекательно-образовательный чат-бот для Telegram.

Основные возможности:  
- Распознавание объектов на изображениях.  
- Определение возраста и настроения человека по фотографии.  
- Прохождение теста на английском языке с обеспечением обратной связи с преподавателем.  

Бот позволяет пользователю весело и интересно взаимодействовать с платформой и наблюдать за результатами.

---

## Description (in English)
AgeBot is an educational and entertaining Telegram bot.

Features include:  
- Object recognition in images.  
- Age and mood detection from photos.  
- English test with results sent to teachers, providing immediate feedback.  

The bot offers engaging and interactive experiences for individual users, combining learning with fun.

---

## Technical Details & Installation
Requirements include Python 3.10+, the python-telegram-bot library (v20+ async version), and other dependencies listed in requirements.txt. To install, clone the repository, create and activate a virtual environment, install dependencies, configure local accounts in config/test_accounts.py and set bot token and other secrets via environment variables. Run the bot with Python. The .gitignore is configured to exclude virtual environments, logs, local test accounts, and other sensitive files. Async handlers provide fast, non-blocking responses. Teachers and admins are configured in config/users.py.
