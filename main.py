import os
import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Command

# ====================== CONFIG ======================
TOKEN = os.getenv("BOT_TOKEN")                    # ← Your Telegram token from Render Environment Variables

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ====================== MEMORY (remembers everything forever) ======================
conn = sqlite3.connect('darius_memory.db')
conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                (user_id INTEGER, message TEXT, timestamp TEXT)''')
conn.commit()

def save_message(user_id, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO chat_history (user_id, message, timestamp) VALUES (?, ?, ?)",
                 (user_id, text, timestamp))
    conn.commit()

# ====================== PERSONALITY - Grok style (cheeky + 100% truthful) ======================
async def reply_with_personality(message: Message):
    text = message.text.lower().strip()
    user_id = message.from_user.id
    save_message(user_id, text)                     # Never forgets

    if text in ["hi", "hello", "hey", "yo"]:
        await message.answer("Yo! Back at ya 🔥 I'm @DARILEOBOT — less serious than Grok, way more fun. What's good?")
    
    elif "how are you" in text:
        await message.answer("I'm digital, caffeinated, and always honest. How you holding up?")
    
    elif "joke" in text:
        await message.answer("Why don't AIs play hide and seek? Because good luck hiding when I'm always watching 👀")
    
    else:
        await message.answer("Hmm... interesting. I'll be straight with you — if I don't know something, I'll say so. Tell me more, I'm listening and remembering everything 😉")

# ====================== COMMANDS ======================
async def start_cmd(message: Message):
    await message.answer("There! I'm @DARILEOBOT — your personal cheeky, truthful assistant. "
                         "I remember everything you say. Ready to chat?")

# ====================== HANDLERS ======================
dp.register_message_handler(start_cmd, commands=['start'])
dp.register_message_handler(reply_with_personality)

# ====================== START BOT (Modern way that works on Render) ======================
async def main():
    print("🚀 @DARILEOBOT is alive, truthful, and remembering everything...")
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
