import os
import json
import random
import logging
from dotenv import load_dotenv

load_dotenv()

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
TICKETS_FILE = "tickets.json"
PARTICIPANTS_FILE = "participants.json"
LOG_FILE = "giveaway.log"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    encoding='utf-8'
)

# Проверка, является ли пользователь админом
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Выбор победителей и раздача билетов
async def draw_and_send(bot):
    try:
        # Загрузка участников
        with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
            participants = json.load(f)
        # Загрузка билетов
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            tickets = json.load(f)
        if len(participants) < 80:
            msg = f"Недостаточно участников для розыгрыша: {len(participants)} (нужно >= 80)"
            logging.error(msg)
            raise Exception(msg)
        if len(tickets) < 80:
            msg = f"Недостаточно билетов для розыгрыша: {len(tickets)} (нужно >= 80)"
            logging.error(msg)
            raise Exception(msg)
        # Случайный выбор 80 победителей
        winners = random.sample(participants, 80)
        random.shuffle(tickets)
        # Рассылка билетов
        for winner, ticket in zip(winners, tickets):
            try:
                await bot.send_message(
                    winner["user_id"],
                    f"🎉 Поздравляем! Вы выиграли билет: {ticket}"
                )
                logging.info(f"Билет {ticket} отправлен пользователю {winner['user_id']} ({winner['username']})")
            except Exception as e:
                logging.error(f"Ошибка отправки {winner['user_id']}: {e}")
        # Логирование результатов
        with open("winners.json", "w", encoding="utf-8") as f:
            json.dump([
                {"user_id": w["user_id"], "username": w["username"], "ticket": t}
                for w, t in zip(winners, tickets)
            ], f, ensure_ascii=False, indent=2)
        logging.info("Розыгрыш завершён успешно. Итоги сохранены в winners.json.")
    except Exception as e:
        logging.exception(f"Ошибка при проведении розыгрыша: {e}")
        raise

def simulate_draw():
    # Генерируем 100 уникальных участников
    participants = [
        {"user_id": i, "username": f"user{i}"}
        for i in range(1, 101)
    ]
    # Генерируем 80 уникальных билетов
    tickets = [f"https://ticket.example.com/{i}" for i in range(1, 81)]
    # Случайный выбор 80 победителей
    winners = random.sample(participants, 80)
    random.shuffle(tickets)
    # Проверка уникальности победителей
    winner_ids = [w["user_id"] for w in winners]
    assert len(winner_ids) == len(set(winner_ids)), "Есть повторы среди победителей!"
    # Проверка уникальности билетов
    assert len(tickets) == len(set(tickets)), "Есть повторы среди билетов!"
    # Проверка соответствия 1:1
    assert len(winners) == len(tickets) == 80, "Длина списков не совпадает!"
    # Проверка, что каждый билет выдан только одному человеку
    issued = set()
    for w, t in zip(winners, tickets):
        assert t not in issued, f"Билет {t} выдан повторно!"
        issued.add(t)
    print("Симуляция успешна: 80 уникальных победителей, 80 уникальных билетов, соответствие 1:1.")
