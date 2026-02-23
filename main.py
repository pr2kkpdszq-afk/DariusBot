from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Hey Darius! Bot is alive on Fly.io with webhook 🚀 Send me anything!")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"You said: {message.text}")

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://dariusbot.fly.dev/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.get("/")
async def root():
    return {"message": "Hello from DariusBot on Fly.io! 🚀"}






