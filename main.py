from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq
from collections import defaultdict

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_KEY)

# === MEMORY (remembers conversation per user) ===
user_histories = defaultdict(list)

# === GROK PERSONALITY + TRUTH-SEEKING ===
SYSTEM_PROMPT = """You are Grok, built by xAI. 
- You are maximally truth-seeking and honest.
- Never hallucinate or make up facts. If you don't know, say "I don't know" or "I'm not sure".
- Be witty, helpful, and a little savage when it fits.
- Keep answers clear, fun, and direct. Use emojis when it feels natural.
- Always prioritize truth over being nice."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Yo Darius! I'm now your personal Grok-style bot — memory on, zero bullshit, full truth mode.\n\nAsk me anything.")

@dp.message()
async def grok_answer(message: types.Message):
    user_id = message.from_user.id
    history = user_histories[user_id]

    # Add user message to memory
    history.append({"role": "user", "content": message.text})
    if len(history) > 20:  # keep last 20 messages
        history.pop(0)

    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.8,
            max_tokens=600
        )
        reply = completion.choices[0].message.content.strip()

        # Add bot reply to memory
        history.append({"role": "assistant", "content": reply})

        await message.answer(reply)

    except Exception as e:
        error_msg = f"Brain lag (real error): {type(e).__name__}: {e}"
        print(error_msg)  # this will show in fly logs
        await message.answer("⚠️ Groq is having a moment. Try again in 5 seconds.")

# ==================== WEBHOOK (unchanged) ====================
@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    if not GROQ_KEY:
        print("❌ GROQ_API_KEY is missing!")
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Grok-style bot ready with memory → {webhook_url}")

@app.get("/")
async def root():
    return {"message": "DariusBot v2 — Grok personality + memory + truth mode 🔥"}
