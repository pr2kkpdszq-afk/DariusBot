from fastapi import FastAPI
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

app = FastAPI()

# Get your token from Fly.io secrets (set with: fly secrets set TELEGRAM_TOKEN=your-token-here)
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set! Add it via fly secrets set TELEGRAM_TOKEN=...")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Hey Darius! I'm your bot—alive on Fly.io. What’s up? 😎")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"You said: {message.text}")

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
async def root():
    return {"message": "Hello from DariusBot on Fly.io!"}




