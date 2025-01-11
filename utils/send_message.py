from telegram import Bot
from config import tg_bot_token

async def send_message_to_user(tg_id, message, **args):
    bot = Bot(token=tg_bot_token)
    await bot.send_message(chat_id=tg_id, text=message, **args)
