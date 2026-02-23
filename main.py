from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import AsyncGroq

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_KEY)

# ==================== COMMANDS ====================
@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton(text="👨‍💻 About", callback_data="about")]
    ])
    await message.answer(
        "👋 Hey Darius! I'm your smart bot running 24/7 on Fly.io.\n\n"
        "Ask me anything — I can answer questions, tell jokes, explain stuff, etc! 🚀",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("Just type anything! I use Groq AI to give real answers.")

# ==================== BUTTONS ====================
@dp.callback_query(lambda c: c.data == "help")
async def help_button(callback: types.CallbackQuery):
    await callback.message.edit_text("Type any question — I will answer intelligently!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "about")
async def about_button(callback: types.CallbackQuery):
    await callback.message.edit_text("🤖 Built by Darius in 2 days with Grok + Groq AI\nRunning free on Fly.io 🔥")
    await callback.answer()

# ==================== SMART ANSWERS (this is the magic) ====================
@dp.message()
async def smart_answer(message: types.Message):
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are DariusBot, a fun and helpful AI built by Darius. Keep answers short, friendly and useful. Use emojis."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=400
        )
        reply = completion.choices[0].message.content
        await message.answer(reply)
    except Exception as e:
        await message.answer("Oops, brain lag 😅 Try again!")

# ==================== WEBHOOK ====================
@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Smart bot webhook ready → {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.get("/")
async def root():
    return {"message": "DariusBot is alive & SMART now! 🚀"}
