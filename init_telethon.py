import os
from dotenv import load_dotenv
from telethon import TelegramClient, errors
from telethon.sessions import StringSession

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
if not API_ID or not API_HASH:
    print("❗ Установи API_ID и API_HASH в .env")
    exit(1)

def main():
    print("=== Инициализация Telethon клиентской сессии ===")
    session_str = os.getenv('TELEGRAM_SESSION_STRING')
    if session_str:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    else:
        client = TelegramClient(StringSession(), API_ID, API_HASH)

    async def start_flow():
        await client.connect()
        if not await client.is_user_authorized():
            phone = input("📱 Введи свой телефон (международный формат): ")
            await client.send_code_request(phone)
            code = input("📩 Введи код из Telegram: ")
            try:
                await client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                pw = input("🔐 Введи пароль двухфакторной аутентификации: ")
                await client.sign_in(password=pw)
        me = await client.get_me()
        print(f"✅ Успешно вошёл как {me.username} [{me.id}]")

        saved = client.session.save()
        print("\n📌 TELEGRAМ_SESSION_STRING:\n")
        print(saved)
        print("\n🔒 Сохрани эту строку в .env как TELEGRAM_SESSION_STRING")
        await client.disconnect()

    client.loop.run_until_complete(start_flow())

if __name__ == "__main__":
    main()