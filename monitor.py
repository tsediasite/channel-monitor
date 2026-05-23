import os
import json
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))
THRESHOLD = int(os.getenv("THRESHOLD", 5))
STATE_FILE = "state.json"
INTERVAL = 300  # 300 секунд = 5 хвилин

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_count": None}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

async def check_subscribers(bot):
    count = await bot.get_chat_member_count(CHANNEL_ID)
    state = load_state()
    last_count = state.get("last_count")

    print(f"Підписників зараз: {count}")

    if last_count is None:
        save_state({"last_count": count})
        await bot.send_message(
            chat_id=MY_CHAT_ID,
            text=f"✅ Моніторинг запущено\nПідписників зараз: {count}"
        )
        return

    diff = count - last_count

    if abs(diff) >= THRESHOLD:
        if diff < 0:
            emoji = "🔴"
            direction = f"відписалось {abs(diff)}"
        else:
            emoji = "🟢"
            direction = f"підписалось {diff}"

        message = (
            f"{emoji} Зміна підписників!\n\n"
            f"Канал: @obmen_usd\n"
            f"Було: {last_count}\n"
            f"Стало: {count}\n"
            f"Зміна: {direction}"
        )

        await bot.send_message(chat_id=MY_CHAT_ID, text=message)
        print("Сповіщення надіслано")
    else:
        print(f"Зміна {diff} — в межах норми")

    save_state({"last_count": count})

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Моніторинг запущено. Перевірка кожні 5 хвилин.")
    
    while True:
        try:
            await check_subscribers(bot)
        except Exception as e:
            print(f"Помилка: {e}")
        
        await asyncio.sleep(INTERVAL)  # чекаємо 5 хвилин

if __name__ == "__main__":
    asyncio.run(main())
