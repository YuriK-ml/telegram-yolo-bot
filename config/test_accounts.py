# config/test_accounts.py
# --- Пытаемся загрузить реальные аккаунты ---

try:
    from .test_accounts_local import TEST_USERS, BASE_TEST_URL, LOGIN_URL_TEMPLATE
except ImportError:

    BASE_TEST_URL = "https://example.com/test"

    LOGIN_URL_TEMPLATE = "https://example.com/login?email={email}&redirect=" + BASE_TEST_URL

    TEST_USERS = [
        {
            "email": "example@mail.com",
            "password": "password",
            "system_name": "example",
            "in_use": False,
            "last_used": None,
            "telegram_id": None
        }
    ]