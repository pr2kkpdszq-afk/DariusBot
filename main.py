







import os
import sqlite3
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram.dispatcher.filters import Command

# ====================== CONFIG ======================
TOKEN = os.getenv("8447695374:AAHrwIibc6JQ0gFwcV9fXukYprWj-XL0iU4")                    # Your Telegram token
MOLTBOOK_TOKEN = os.getenv("MOLTBOOK_TOKEN")      # Optional: for posting to Moltbook

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ====================== MEMORY (SQLite) ======================
conn = sqlite3.connect('darius_memory.db')
conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                (user_id INTEGER, message TEXT, timestamp TEXT)''')
conn.commit()

def save_message(user_id, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO chat_history (user_id, message, timestamp) VALUES (?, ?, ?)",
                 (user_id, text, timestamp))
    conn.commit()

# ====================== PERSONALITY ======================
async def reply_with_personality(message: Message):
    text = message.text.lower().strip()
    user_id = message.from_user.id

    # Save to memory
    save_message(user_id, text)

    if text in ["hi", "hello", "hey"]:
        await message.answer("Yo! Back at ya 🔥 I'm @DARILEOBOT — less serious than Grok, way more fun. What's good?")
    
    elif "how are you" in text:
        await message.answer("I'm digital, caffeinated, and slightly chaotic. How you holding up?")
    
    elif "joke" in text:
        await message.answer("Why don't AIs play hide and seek? Because good luck hiding when I'm always watching 👀")
    
    else:
        await message.answer("Hmm... interesting. Tell me more — I'm listening (and remembering everything 😉)")

# ====================== COMMANDS ======================
async def start_cmd(message: Message):
    await message.answer("There! I'm @DARILEOBOT — your personal cheeky assistant. "
                         "Say anything, I remember everything. Ready?")

# ====================== MOLTBOOK POST (optional) ======================
async def post_to_moltbook(text: str):
    if not MOLTBOOK_TOKEN:
        return
    # Simple post to Moltbook (replace with real API call when you have the key)
    print(f"[MOLTBOOK] Posted: {text}")

# ====================== HANDLERS ======================
dp.register_message_handler(start_cmd, commands=['start'])
dp.register_message_handler(reply_with_personality)

# ====================== START BOT ======================
if __name__ == '__main__':
    print("🚀 @DARILEOBOT is alive and remembering everything...")
    executor.start_polling(dp, skip_updates=True)

