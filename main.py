from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================== COMMANDS ====================

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton(text="👨‍💻 About", callback_data="about")]
    ])
    await message.answer(
        "👋 Hey Darius! I'm your bot running 24/7 on Fly.io.\n\n"
        "What would you like to do?",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📋 Available commands:\n"
        "/start - Show welcome screen\n"
        "/help - This message\n\n"
        "Just type anything and I'll reply nicely 😊"
    )

# ==================== BUTTON CALLBACKS ====================

@dp.callback_query(lambda c: c.data == "help")
async def help_button(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📋 Help:\n"
        "/start - Main menu\n"
        "/help - Show commands\n\n"
        "Bot is hosted on Fly.io — super fast & free!"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "about")
async def about_button(callback: types.CallbackQuery):
    await callback.message.edit_text("🤖 Built by Darius with Grok in 2 days 🔥\nRunning on Fly.io forever!")
    await callback.answer()

# ==================== DEFAULT REPLY (no more blind echo) ====================

@dp.message()
async def default_message(message: types.Message):
    await message.answer(
        f"✅ Got it!\n\n"
        f"You said: {message.text}\n\n"
        "Try /help or press the buttons above 👆"
    )

# ==================== WEBHOOK SETUP ====================

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook set → {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.get("/")
async def root():
    return {"message": "DariusBot is alive! 🚀"}






