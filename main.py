import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # example: https://phoenix-item-bot.onrender.com

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")
if not APP_URL:
    raise ValueError("APP_URL is missing")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = APP_URL + WEBHOOK_PATH

bot_app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Phoenix Item Shop Bot မှ ကြိုဆိုပါတယ်")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong ✅")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("ping", ping))

api = FastAPI()

@api.on_event("startup")
async def on_startup():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    await bot_app.start()

@api.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

@api.on_event("shutdown")
async def on_shutdown():
    await bot_app.stop()
    await bot_app.shutdown()
