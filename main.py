import asyncio
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

TELEGRAM_TOKEN = "8447695374:AAHrwIibc6JQ0gFwcV9fXukYprWj-XL0iU4"  # replace with your real token

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot=bot)
async def start_cmd(message: Message):
    await message.answer("There! I'm @DARILEOBOT. What do you need?")

dp.register_message_handler(start_cmd, commands= )
async def start(message: Message):
    await message.answer("Hey there! I'm @DARILEOBOT. What do you need?")

dp.register_message_handler(on_message)
async def echo(message: Message):
    await message.answer(message.text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())


