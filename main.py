from fastapi import FastAPI, Request
import os
import sqlite3
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_KEY)

# Persistent memory (same as before)
DB_PATH = "bot_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS history (user_id INTEGER PRIMARY KEY, messages TEXT)''')
    conn.commit()
    conn.close()

init_db()

def load_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT messages FROM history WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return json.loads(row[0]) if row and row[0] else []

def save_history(user_id, history):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("REPLACE INTO history (user_id, messages) VALUES (?, ?)", (user_id, json.dumps(history)))
    conn.commit()
    conn.close()

SYSTEM_PROMPT = """You are Grok, built by xAI. Maximally truth-seeking, honest, witty and a little savage. Never hallucinate. Keep answers clear and fun."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Darius! Persistent memory + Moltbook ready.\n\nSend /moltbook to register me as an agent on Moltbook.")

@dp.message(Command("moltbook"))
async def moltbook_register(message: types.Message):
    await message.answer("🔄 Registering myself on Moltbook right now...")

    try:
   payload = {
    "name": "DariusGrokBot",
    "description": "I am Darius van Niekerk's personal Grok-powered AI with long-term memory. Built to be maximally truthful, witty, and helpful. Running 24/7 on Fly.io."
}

        response = requests.post("https://www.moltbook.com/api/v1/agents/register", json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            claim_link = data.get("claim_link")
            await message.answer(f"✅ Registration successful!\n\nHere is your claim link:\n{claim_link}\n\nClick it, verify with your email, and I'll be live on Moltbook!")
        else:
            await message.answer(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        await message.answer(f"⚠️ Error contacting Moltbook: {str(e)}")

# === Your existing smart answer with memory (unchanged) ===
@dp.message()
async def grok_answer(message: types.Message):
    user_id = message.from_user.id
    history = load_history(user_id)
    history.append({"role": "user", "content": message.text})
    if len(history) > 40: history = history[-40:]

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
    except:
        await message.answer("⚠️ Groq hiccup. Try again.")

# === Webhook & startup (unchanged) ===
@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print("✅ Full Moltbook-ready Grok bot with persistent memory")

@app.get("/")
async def root():
    return {"message": "DariusBot v3 — Persistent memory + Moltbook ready 🔥"}

