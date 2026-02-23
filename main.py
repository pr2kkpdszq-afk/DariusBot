from fastapi import FastAPI, Request
import os
import sqlite3
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_KEY)

# Persistent memory database
DB_PATH = "bot_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS history 
                    (user_id INTEGER PRIMARY KEY, messages TEXT)''')
    conn.commit()
    conn.close()

init_db()

def load_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT messages FROM history WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return []

def save_history(user_id, history):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("REPLACE INTO history (user_id, messages) VALUES (?, ?)", 
                 (user_id, json.dumps(history)))
    conn.commit()
    conn.close()

SYSTEM_PROMPT = """You are Grok, built by xAI. 
You are maximally truth-seeking and honest. Never hallucinate or make up facts. 
If you don't know something, say "I don't know". 
Be witty, helpful, direct, and a little savage when it fits. 
Keep answers clear and fun. Use emojis naturally."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Darius! Persistent memory activated. I now remember everything across sleeps and days. Ask me anything.")

@dp.message()
async def grok_answer(message: types.Message):
    user_id = message.from_user.id
    history = load_history(user_id)

    history.append({"role": "user", "content": message.text})
    if len(history) > 40:
        history = history[-40:]

    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.75,
            max_tokens=700
        )
        reply = completion.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        save_history(user_id, history)

        await message.answer(reply)

    except Exception as e:
        await message.answer(f"⚠️ Groq hiccup: {str(e)[:80]}... Try again.")

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print("✅ Persistent memory Grok bot ready")

@app.get("/")
async def root():
    return {"message": "DariusBot with real persistent memory 🔥"}
