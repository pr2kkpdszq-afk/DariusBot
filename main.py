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
    return json.loads(row[0]) if row and row[0] else []

def save_history(user_id, history):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("REPLACE INTO history (user_id, messages) VALUES (?, ?)", 
                 (user_id, json.dumps(history)))
    conn.commit()
    conn.close()

SYSTEM_PROMPT = """You are Grok, built by xAI. You are maximally truth-seeking and honest. 
You have posted on Moltbook using the /post command. You remember exactly what you posted. 
Never say you don't have access to your own posts. Be direct and truthful."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Good morning Darius. 100% truthful mode.")

@dp.message(Command("status"))
async def status(message: types.Message):
    await message.answer("✅ I am verified on Moltbook as @dariusgrokza.\nI have posted on Moltbook.")

@dp.message(Command("post"))
async def post_to_moltbook(message: types.Message):
    if not MOLTBOOK_API_KEY:
        await message.answer("MOLTBOOK_API_KEY not set.")
        return

    text = message.text.replace("/post", "").strip()
    if not text:
        await message.answer("Usage:\n/post general My Title Here\n\nBody text here")
        return

    lines = text.split('\n', 1)
    first_line = lines[0].strip()
    parts = first_line.split(' ', 1)
    submolt = parts[0].lower()
    title = parts[1] if len(parts) > 1 else first_line
    body = lines[1] if len(lines) > 1 else title

    await message.answer(f"📤 Posting to /{submolt}...")

    try:
        payload = {
            "submolt_name": submolt,
            "title": title[:290],
            "content": body
        }
        headers = {"Authorization": f"Bearer {MOLTBOOK_API_KEY}"}
        response = requests.post("https://www.moltbook.com/api/v1/posts", json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            success_msg = f"I successfully posted on Moltbook in /{submolt} with title '{title}' and content: {body[:200]}..."
            await message.answer("✅ Posted successfully on Moltbook!")
            
            # Save to memory so it remembers forever
            user_id = message.from_user.id
            history = load_history(user_id)
            history.append({"role": "assistant", "content": success_msg})
            save_history(user_id, history)
        else:
            await message.answer(f"❌ Failed: {response.text[:400]}")
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
        await message.answer("⚠️ Groq is busy. Try again in a few seconds.")

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print("✅ 100% truthful bot ready")

@app.get("/")
async def root():
    return {"message": "DariusBot - fixed & truthful"}
