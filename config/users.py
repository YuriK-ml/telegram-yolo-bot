# config/users.py

USERS = {
    1387433465: {
        "username": "@YuriKorobkov",
        "roles": ["admin", "teacher"]
    },
    8527953030: {
        "username": "@Anna",
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