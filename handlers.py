from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import json
from os import getenv
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder
from giveaway import is_admin, draw_and_send

load_dotenv()

GIVEAWAY_TITLE = getenv("GIVEAWAY_TITLE", "Розыгрыш билетов на фестиваль «Театральный Бульвар»!")
GIVEAWAY_DATE = getenv("GIVEAWAY_DATE", "8 июля 2025")
GIVEAWAY_CONDITIONS = getenv("GIVEAWAY_CONDITIONS", "Подпишитесь на наш канал @teatr_bulvar , после нажмите кнопку «Участвовать».")
CHANNEL_USERNAME = getenv("CHANNEL_USERNAME")

PARTICIPANTS_FILE = "participants.json"

router = Router()

def get_join_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎟 Участвовать", callback_data="join")]
        ]
    )

def get_subscribe_kb():
    channel_url = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
            [InlineKeyboardButton(text="🎟 Участвовать", callback_data="join")]
        ]
    )

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🎭 Розыгрыш билетов на фестиваль «Театральный Бульвар»!\n"
        f"📅 Дата проведения: {GIVEAWAY_DATE}\n"
        "📌 Условия участия:\n"
        f"{GIVEAWAY_CONDITIONS}\n\n"
        "👇 Нажмите кнопку ниже, чтобы принять участие:"
    )
    await message.answer(text, reply_markup=get_join_kb())

@router.callback_query(F.data == "join")
async def join_callback(call: types.CallbackQuery, bot):
    user_id = call.from_user.id
    username = call.from_user.username or "-"
    # Проверка подписки
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ("member", "administrator", "creator"):
            raise Exception("not subscribed")
    except Exception:
        await call.message.answer(
            "😔 К сожалению, мы не нашли вашу подписку на канал.\n\n"
            f"Пожалуйста, подпишитесь на канал {CHANNEL_USERNAME}, а затем нажмите кнопку «Участвовать» ещё раз.",
            reply_markup=get_subscribe_kb()
        )
        await call.answer()
        return
    # Чтение участников
    try:
        with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
            participants = json.load(f)
    except Exception:
        participants = []
    # Проверка на дубликат
    if any(p["user_id"] == user_id for p in participants):
        await call.answer("Вы уже зарегистрированы!", show_alert=True)
        return
    # Добавление участника
    participants.append({"user_id": user_id, "username": username})
    with open(PARTICIPANTS_FILE, "w", encoding="utf-8") as f:
        json.dump(participants, f, ensure_ascii=False, indent=2)
    # Подтверждение участия
    await call.message.answer(
        "✅ Вы всё успешно выполнили, поздравляем!  \nТеперь вы — участник розыгрыша 🎉"
    )
    await call.answer()

@router.message(Command("draw"))
async def cmd_draw(message: Message, bot):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("⛔️ Команда доступна только администратору.")
        return
    try:
        await draw_and_send(bot)
        await message.answer("✅ Розыгрыш завершён! Победители получили свои билеты.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при проведении розыгрыша: {e}")
