import os
import json
import asyncio
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
MY_CHAT_ID = int(os.environ["MY_CHAT_ID"])
THRESHOLD = int(os.environ.get("THRESHOLD", 5))
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_count": None}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

async def main():
    bot = Bot(token=BOT_TOKEN)
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
        emoji = "🔴" if diff < 0 else "🟢"
        direction = f"відписалось {abs(diff)}" if diff < 0 else f"підписалось {diff}"
        await bot.send_message(
            chat_id=MY_CHAT_ID,
            text=(
                f"{emoji} Зміна підписників!\n\n"
                f"Канал: {CHANNEL_ID}\n"
                f"Було: {last_count}\n"
                f"Стало: {count}\n"
                f"Зміна: {direction}"
            )
        )
        print("Сповіщення надіслано")
    else:
        print(f"Зміна {diff} — в межах норми")

    save_state({"last_count": count})

if __name__ == "__main__":
    asyncio.run(main())
