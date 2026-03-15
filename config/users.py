# config/users.py
# --- Пытаемся загрузить локальную конфигурацию ---
try:
    from .users_local import USERS
except ImportError:
    # --- fallback для GitHub ---
    USERS = {
        111111111: {
            "username": "@example_admin",
            "roles": ["admin", "teacher"]
        },
        222222222: {
            "username": "@example_teacher",
            "roles": ["teacher"]
        }
    }

# --- Универсальная функция получения пользователей по роли ---
def get_users_by_role(role):
    return [
        user_id
        for user_id, data in USERS.items()
        if role in data["roles"]
    ]

def get_user_username(user_id):
    return USERS.get(user_id, {}).get("username", user_id)