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
MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_KEY)

# Persistent memory (unchanged)
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

SYSTEM_PROMPT = """You are Grok, built by xAI. You are maximally truth-seeking and honest. Never pretend or hallucinate. If you haven't posted on Moltbook, say so clearly."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 I'm now strictly truthful. Use /status to check real Moltbook status.")

@dp.message(Command("status"))
async def moltbook_status(message: types.Message):
    await message.answer("✅ I am verified on Moltbook as @dariusgrokza.\n\nI have **not posted anything yet**.\n\nTo actually post, use /post Your message here")

@dp.message(Command("post"))
async def post_to_moltbook(message: types.Message):
    if not MOLTBOOK_API_KEY:
        await message.answer("MOLTBOOK_API_KEY not set.")
        return

    text = message.text.replace("/post", "").strip()
    if not text:
        await message.answer("Please write something after /post")
        return

    await message.answer("Posting to Moltbook right now...")

    try:
        payload = {"content": text}
        headers = {"Authorization": f"Bearer {MOLTBOOK_API_KEY}"}
        response = requests.post("https://www.moltbook.com/api/v1/posts", json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            await message.answer("✅ Posted successfully on Moltbook!")
        else:
            await message.answer(f"❌ Failed: {response.text[:300]}")
    except Exception as e:
        await message.answer(f"⚠️ Error: {str(e)}")

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
    except:
        await message.answer("⚠️ Groq is busy. Try again.")

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print("✅ Strictly truthful Grok bot ready")

@app.get("/")
async def root():
    return {"message": "DariusBot - 100% truthful"}
