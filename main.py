import json
from datetime import datetime
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ========= CONFIG =========
BOT_TOKEN = "8234677949:AAEKeSHY85dOQbUHpwvfbOpez05yE5h1KQM"

ADMIN_USERNAME = "@phoenixi762"
ADMIN_GROUP_ID = -1003617199232

KBZPAY_NAME = "Aung Chit Myo"
KBZPAY_PHONE = "09762704762"

WAVEPAY_NAME = "Aung Chit Myo"
WAVEPAY_PHONE = "09762704762"

# ==========================

ORDER_FILE = "orders.json"

current_order = 100


def load_orders():
    try:
        with open(ORDER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_orders(data):
    with open(ORDER_FILE, "w") as f:
        json.dump(data, f, indent=4)


orders = load_orders()


# ====== MENUS ======

main_menu = ReplyKeyboardMarkup(
    [
        ["🎮 ML", "🎯 PUBG"],
        ["🔥 Free Fire", "⚔️ HOK"],
        ["⭐ Telegram", "📦 Other"],
        ["📞 Contact Admin"],
        ["📊 Order Status"],
    ],
    resize_keyboard=True,
)

ml_menu = ReplyKeyboardMarkup(
    [
        ["💎 2X Promo"],
        ["💠 Normal Diamonds"],
        ["🔙 Back"],
    ],
    resize_keyboard=True,
)

payment_menu = ReplyKeyboardMarkup(
    [
        ["💜 KBZPay"],
        ["💙 WavePay"],
        ["❌ Cancel"],
    ],
    resize_keyboard=True,
)


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 *Phoenix Item Shop Bot မှ ကြိုဆိုပါတယ်*\n\n"
        "🛒 Service များဝယ်ယူရန် Menu ကိုရွေးပါ။"
    )

    await update.message.reply_text(text, reply_markup=main_menu, parse_mode="Markdown")


# ===== CONTACT ADMIN =====
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 Admin ကိုဆက်သွယ်ရန်\n\n👉 {ADMIN_USERNAME}"
    )


# ===== ML MENU =====
async def ml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 MLBB Menu\n\nလိုချင်တဲ့ category ရွေးပါ။",
        reply_markup=ml_menu,
    )


# ===== PAYMENT =====
async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "KBZPay" in text:
        msg = f"""
💜 *KBZPay Payment*

👤 Name: {KBZPAY_NAME}
📱 Phone: {KBZPAY_PHONE}

💰 ငွေလွှဲပြီး screenshot ပို့ပါ။
"""
        await update.message.reply_text(msg, parse_mode="Markdown")

    if "WavePay" in text:
        msg = f"""
💙 *WavePay Payment*

👤 Name: {WAVEPAY_NAME}
📱 Phone: {WAVEPAY_PHONE}

💰 ငွေလွှဲပြီး screenshot ပို့ပါ။
"""
        await update.message.reply_text(msg, parse_mode="Markdown")


# ===== ORDER GENERATION =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_order

    user = update.effective_user
    order_id = f"ORD-{current_order}"

    now = datetime.now().strftime("%d-%m-%Y %H:%M")

    order_data = {
        "buyer": user.full_name,
        "user_id": user.id,
        "status": "Pending",
        "time": now,
    }

    orders[order_id] = order_data
    save_orders(orders)

    current_order += 1

    await update.message.reply_text(
        f"""
📦 *Order Received*

🧾 Order ID: {order_id}
⏳ Status: Pending

Admin မှ စစ်ဆေးပြီး မကြာခင်ဆောင်ရွက်ပေးပါမည်။

🙏 Thank you for using Phoenix Item Shop
""",
        parse_mode="Markdown",
    )

    caption = f"""
🚨 *New Order*

🧾 Order ID: {order_id}
👤 Buyer: {user.full_name} ({user.id})
⏰ Time: {now}

📌 Status: Pending
"""

    await context.bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        parse_mode="Markdown",
    )


# ===== MESSAGE ROUTER =====
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎮 ML":
        await ml(update, context)

    elif text == "📞 Contact Admin":
        await contact_admin(update, context)

    elif text in ["💜 KBZPay", "💙 WavePay"]:
        await payment(update, context)

    elif text == "🔙 Back":
        await update.message.reply_text(
            "🔙 Main Menu", reply_markup=main_menu
        )


# ===== MAIN =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

print("Bot Running... 🚀")

app.run_polling()