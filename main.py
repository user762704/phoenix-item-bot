import json
import logging
import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Any

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================================
# CONFIG
# =========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN")
BOTMIN_USERNAME = "@phoenixi762"
ADMIN_GROUP_ID = -1003617199232
ADMIN_USER_ID = 6499351439  # admin telegram user id

KBZPAY_NAME = "Aung Chit Myo"
KBZPAY_PHONE = "09762704762"

WAVEPAY_NAME = "Aung Chit Myo"
WAVEPAY_PHONE = "09762704762"

ORDERS_FILE = "orders.json"
PRICES_FILE = "prices.json"
ORDER_COUNTER_FILE = "order_counter.json"

TIME_FORMAT = "%d-%m-%Y %I:%M %p"

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =========================================================
# DEFAULT PRICES
# =========================================================
DEFAULT_PRICES = {
    "mobile_legends": {
        "💥 2X Promo": {
            "💎 50+50 Diamonds — 3300 Ks": 3300,
            "💎 150+150 Diamonds — 9500 Ks": 9500,
            "💎 250+250 Diamonds — 15200 Ks": 15200,
            "💎 500+500 Diamonds — 31000 Ks": 31000,
        },
        "💎 Normal": {
            "🎫 Weekly Pass — 6200 Ks": 6200,
            "🎟️ Weekly Elite Bundle — 3300 Ks": 3300,
            "👑 Month Epic Bundle — 15900 Ks": 15900,
            "🌙 Twilight Pass — 32500 Ks": 32500,
            "💎 11 Diamonds — 850 Ks": 850,
            "💎 22 Diamonds — 1650 Ks": 1650,
            "💎 44 Diamonds — 3180 Ks": 3180,
            "💎 86 Diamonds — 5000 Ks": 5000,
            "💎 172 Diamonds — 9850 Ks": 9850,
            "💎 257 Diamonds — 14700 Ks": 14700,
            "💎 343 Diamonds — 19200 Ks": 19200,
            "💎 429 Diamonds — 24100 Ks": 24100,
            "💎 515 Diamonds — 29030 Ks": 29030,
            "💎 600 Diamonds — 33570 Ks": 33570,
            "💎 706 Diamonds — 38560 Ks": 38560,
            "💎 963 Diamonds — 52780 Ks": 52780,
            "💎 1049 Diamonds — 57810 Ks": 57810,
            "💎 1135 Diamonds — 62650 Ks": 62650,
            "💎 1412 Diamonds — 77000 Ks": 77000,
        },
    },
    "pubg": {
        "🏷️ Items": {
            "📦 Weekly Deal Pack 1 — 4000 Ks": 4000,
            "📦 Weekly Deal Pack 2 — 11690 Ks": 11690,
            "🛡️ Weekly Mythic Emblem — 14600 Ks": 14600,
            "🎁 First Purchase Pack — 4000 Ks": 4000,
            "⬆️ Upgradable Pack — 11700 Ks": 11700,
            "🔥 Mythic Emblem Pack — 19400 Ks": 19400,
            "✨ Prime 1 Month — 4000 Ks": 4000,
            "✨ Prime 3 Months — 11550 Ks": 11550,
            "✨ Prime 1 Year — 46000 Ks": 46000,
            "🌟 Prime Plus 1 Month — 38240 Ks": 38240,
            "🌟 Prime Plus 3 Months — 114700 Ks": 114700,
            "🌟 Prime Plus 1 Year — 45600 Ks": 45600,
            "🎖️ Elite Pack Lv 1-50 — 23220 Ks": 23220,
            "🎖️ Elite Pack Lv 1-100 — 46560 Ks": 46560,
            "🏆 Elite Pack Plus Lv 1-100 — 106230 Ks": 106230,
            "🔫 60 UC — 3950 Ks": 3950,
            "🔫 120 UC — 7700 Ks": 7700,
            "🔫 180 UC — 11560 Ks": 11560,
            "🔫 325 UC — 19440 Ks": 19440,
            "🔫 445 UC — 26720 Ks": 26720,
            "🔫 660 UC — 38500 Ks": 38500,
            "🔫 985 UC — 55870 Ks": 55870,
            "🔫 1045 UC — 60880 Ks": 60880,
        }
    },
    "free_fire": {
        "🏷️ Items": {
            "🎁 Newbie Bundle — 950 Ks": 950,
            "🗓️ Weekly Lite — 1850 Ks": 1850,
            "🎫 Weekly Membership — 7050 Ks": 7050,
            "🎫 Monthly Membership — 25000 Ks": 25000,
            "📦 Lv 6 Package — 1400 Ks": 1400,
            "📦 Lv 10 Package — 2400 Ks": 2400,
            "📦 Lv 15 Package — 2400 Ks": 2400,
            "📦 Lv 20 Package — 2400 Ks": 2400,
            "📦 Lv 25 Package — 2400 Ks": 2400,
            "📦 Lv 30 Package — 3450 Ks": 3450,
            "⚡ Evo Access 3D — 2000 Ks": 2000,
            "⚡ Evo Access 7D — 3300 Ks": 3300,
            "⚡ Evo Access 30D — 9390 Ks": 9390,
            "💎 100 Diamonds — 3600 Ks": 3600,
            "💎 341 Diamonds — 10700 Ks": 10700,
            "💎 572 Diamonds — 17500 Ks": 17500,
            "💎 1166 Diamonds — 34930 Ks": 34930,
        }
    },
    "hok": {
        "🏷️ Items": {
            "🗓️ Weekly Card — 4400 Ks": 4400,
            "🗓️ Weekly Card Plus — 12900 Ks": 12900,
            "🍀 Double Token Lucky — 1350 Ks": 1350,
            "🛒 Standard Purchase — 4770 Ks": 4770,
            "💠 Premium Purchase — 1350 Ks": 1350,
            "🎖️ Honor Point Value Pack — 1350 Ks": 1350,
            "🪙 16 Token — 820 Ks": 820,
            "🪙 80 Token — 3800 Ks": 3800,
            "🪙 240 Token — 11100 Ks": 11100,
            "🪙 400 Token — 18630 Ks": 18630,
            "🪙 560 Token — 26060 Ks": 26060,
            "🪙 830 Token — 37100 Ks": 37100,
        }
    },
    "telegram_services": {
        "⭐ Star": {
            "⭐ 200 Star — 14300 Ks": 14300,
            "❤️ 100 — 300 Ks": 300,
            "❤️ 1k — 1200 Ks": 1200,
            "❤️ 10k — 10500 Ks": 10500,
        },
        "👑 Premium": {
            "👑 3 Months — 55500 Ks": 55500,
            "👑 6 Months — 75500 Ks": 75500,
            "👑 1 Year — 138500 Ks": 138500,
        },
    },
}

CATEGORY_LABELS = {
    "mobile_legends": "🎮 Mobile Legends",
    "pubg": "🎯 PUBG",
    "free_fire": "🔥 Free Fire",
    "hok": "⚔️ HOK",
    "telegram_services": "⭐ Telegram",
}

# =========================================================
# FILE HELPERS
# =========================================================
def load_json_file(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(default)


def save_json_file(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


prices_data = load_json_file(PRICES_FILE, DEFAULT_PRICES)
orders_data = load_json_file(ORDERS_FILE, {})


def get_next_order_id() -> str:
    data = load_json_file(ORDER_COUNTER_FILE, {"last_number": 99})
    next_number = int(data.get("last_number", 99)) + 1
    data["last_number"] = next_number
    save_json_file(ORDER_COUNTER_FILE, data)
    return f"ORD-{next_number}"


def save_orders() -> None:
    save_json_file(ORDERS_FILE, orders_data)


def save_prices() -> None:
    save_json_file(PRICES_FILE, prices_data)


# =========================================================
# KEYBOARDS
# =========================================================
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎮 Mobile Legends"), KeyboardButton("🎯 PUBG")],
            [KeyboardButton("🔥 Free Fire"), KeyboardButton("⚔️ HOK")],
            [KeyboardButton("⭐ Telegram"), KeyboardButton("📦 Other")],
            [KeyboardButton("📞 Contact Admin")],
            [KeyboardButton("📊 Order Status")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def simple_keyboard(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    kb_rows = [[KeyboardButton(text) for text in row] for row in rows]
    return ReplyKeyboardMarkup(kb_rows, resize_keyboard=True, one_time_keyboard=False)


def ml_keyboard() -> ReplyKeyboardMarkup:
    return simple_keyboard(
        [
            ["💥 2X Promo"],
            ["💎 Normal"],
            ["🔙 Back"],
        ]
    )


def telegram_keyboard() -> ReplyKeyboardMarkup:
    return simple_keyboard(
        [
            ["⭐ Star"],
            ["👑 Premium"],
            ["🔙 Back"],
        ]
    )


def item_list_keyboard(category_key: str, section_key: str) -> ReplyKeyboardMarkup:
    item_names = list(prices_data[category_key][section_key].keys())
    rows = [[name] for name in item_names]
    rows.append(["🔙 Back"])
    return simple_keyboard(rows)


def payment_keyboard() -> ReplyKeyboardMarkup:
    return simple_keyboard(
        [
            ["💜 KBZPay"],
            ["💙 WavePay"],
            ["❌ Cancel"],
        ]
    )


def buy_again_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🛒 Buy Again", callback_data="buy_again")]]
    )


def admin_order_inline(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Complete", callback_data=f"complete:{order_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel:{order_id}"),
            ],
            [
                InlineKeyboardButton("⏳ Pending", callback_data=f"pending:{order_id}"),
            ],
        ]
    )


# =========================================================
# USER STATE HELPERS
# =========================================================
def reset_user_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["flow"] = {}
    context.user_data["awaiting"] = None


def set_flow_value(context: ContextTypes.DEFAULT_TYPE, key: str, value: Any) -> None:
    if "flow" not in context.user_data:
        context.user_data["flow"] = {}
    context.user_data["flow"][key] = value


def get_flow_value(context: ContextTypes.DEFAULT_TYPE, key: str, default: Any = None) -> Any:
    return context.user_data.get("flow", {}).get(key, default)


def current_time_str() -> str:
    return datetime.now().strftime(TIME_FORMAT)


def buyer_display_name(user) -> str:
    if user.username:
        return f"@{user.username}"
    return f"{user.full_name} (ID: {user.id})"


# =========================================================
# PRICE / TEXT HELPERS
# =========================================================
def rebuild_price_line(item_line: str, new_price: int) -> str:
    clean_name = item_line.split(" — ")[0].strip()
    return f"{clean_name} — {new_price} Ks"


def normalize_category_input(text: str) -> str | None:
    t = text.strip().lower()
    mapping = {
        "ml": "mobile_legends",
        "mobile_legends": "mobile_legends",
        "mobile legends": "mobile_legends",
        "pubg": "pubg",
        "freefire": "free_fire",
        "free_fire": "free_fire",
        "free fire": "free_fire",
        "hok": "hok",
        "telegram": "telegram_services",
        "tg": "telegram_services",
        "telegram_services": "telegram_services",
    }
    return mapping.get(t)


def find_item_and_update_price(category_key: str, item_keyword: str, new_price: int) -> str | None:
    item_keyword = item_keyword.lower().strip()
    category_data = prices_data.get(category_key, {})
    for section_key, items in category_data.items():
        for old_line in list(items.keys()):
            if item_keyword in old_line.lower():
                value = items.pop(old_line)
                _ = value
                new_line = rebuild_price_line(old_line, new_price)
                items[new_line] = new_price
                # preserve ordering roughly
                items_sorted = dict(sorted(items.items(), key=lambda kv: list(items.keys()).index(kv[0]) if kv[0] in items else 0))
                category_data[section_key] = items_sorted
                prices_data[category_key] = category_data
                save_prices()
                return new_line
    return None


def find_category_section_by_item(category_key: str, item_line: str) -> str | None:
    for section_key, items in prices_data.get(category_key, {}).items():
        if item_line in items:
            return section_key
    return None


def account_prompt_for(category_key: str) -> str:
    if category_key == "mobile_legends":
        return (
            "📝 ကျေးဇူးပြု၍ *Game ID* ကို ဒီပုံစံနဲ့ပို့ပါ။\n\n"
            "📌 Example:\n"
            "`12345678(54321)`"
        )
    if category_key == "pubg":
        return (
            "📝 ကျေးဇူးပြု၍ *PUBG ID* ကိုပို့ပါ။\n\n"
            "📌 Name ထည့်ချင်ရင်လည်းရပါတယ်။"
        )
    if category_key == "free_fire":
        return (
            "📝 ကျေးဇူးပြု၍ *Free Fire UID* ကိုပို့ပါ။\n\n"
            "📌 Name ထည့်ချင်ရင်လည်းရပါတယ်။"
        )
    if category_key == "hok":
        return "📝 ကျေးဇူးပြု၍ *Account UID* ကိုပို့ပါ။"
    if category_key == "telegram_services":
        return (
            "📝 ကျေးဇူးပြု၍ Telegram account ကိုပို့ပါ။\n\n"
            "📌 Example:\n"
            "`@username`\n"
            "သို့မဟုတ်\n"
            "`09xxxxxxxxx`"
        )
    return "📝 ကျေးဇူးပြု၍ လိုအပ်သော account info ကိုပို့ပါ။"


def is_valid_account_input(category_key: str, text: str) -> bool:
    text = text.strip()
    if category_key == "mobile_legends":
        return bool(re.fullmatch(r"\d+\(\d+\)", text))
    if category_key in {"pubg", "free_fire", "hok"}:
        return len(text) >= 3
    if category_key == "telegram_services":
        return text.startswith("@") or bool(re.fullmatch(r"\+?\d{7,15}", text.replace(" ", "")))
    return len(text) >= 3


# =========================================================
# COMMANDS
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_user_state(context)
    await update.message.reply_text(
        "🔥 *Phoenix Item Shop Bot မှ ကြိုဆိုပါတယ်*\n"
        "ကျေးဇူးပြု၍ Menu ရွေးပါ။",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"📞 *Admin ကိုဆက်သွယ်ရန်*\n\n👉 {ADMIN_USERNAME}",
        parse_mode="Markdown",
    )


async def order_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["awaiting"] = "order_status_id"
    await update.message.reply_text(
        "📊 *Order Status စစ်ရန်*\n\n"
        "ကျေးဇူးပြု၍ Order ID ပို့ပါ။\n"
        "📌 Example: `ORD-100`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🏠 Main Menu",
        reply_markup=main_menu_keyboard(),
    )


async def help_admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        return
    await update.message.reply_text(
        "🛠️ *Admin Commands*\n\n"
        "`/setprice <category> <keyword> <price>`\n"
        "Example: `/setprice ml 86 5200`\n\n"
        "`/showprice <category>`\n"
        "Example: `/showprice ml`\n\n"
        "`/resetprice <category>`\n"
        "Example: `/resetprice ml`",
        parse_mode="Markdown",
    )


async def setprice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Usage:\n`/setprice <category> <keyword> <price>`\n"
            "Example: `/setprice ml 86 5200`",
            parse_mode="Markdown",
        )
        return

    category_input = context.args[0]
    category_key = normalize_category_input(category_input)
    if not category_key:
        await update.message.reply_text("❌ Category မမှန်ပါ။")
        return

    try:
        new_price = int(context.args[-1])
    except ValueError:
        await update.message.reply_text("❌ Price က number ဖြစ်ရပါမယ်။")
        return

    item_keyword = " ".join(context.args[1:-1])
    updated_line = find_item_and_update_price(category_key, item_keyword, new_price)
    if not updated_line:
        await update.message.reply_text("❌ Item မတွေ့ပါ။ keyword ပြန်စစ်ပါ။")
        return

    await update.message.reply_text(
        f"✅ Price Updated\n\n{updated_line}"
    )


async def showprice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage:\n`/showprice <category>`\nExample: `/showprice ml`",
            parse_mode="Markdown",
        )
        return

    category_key = normalize_category_input(context.args[0])
    if not category_key:
        await update.message.reply_text("❌ Category မမှန်ပါ။")
        return

    category_data = prices_data.get(category_key, {})
    lines = [f"📋 *{CATEGORY_LABELS.get(category_key, category_key)} Price List*"]
    for section_key, items in category_data.items():
        lines.append(f"\n*{section_key}*")
        for item_line in items.keys():
            lines.append(f"• {item_line}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def resetprice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage:\n`/resetprice <category>`\nExample: `/resetprice ml`",
            parse_mode="Markdown",
        )
        return

    category_key = normalize_category_input(context.args[0])
    if not category_key:
        await update.message.reply_text("❌ Category မမှန်ပါ။")
        return

    prices_data[category_key] = deepcopy(DEFAULT_PRICES[category_key])
    save_prices()
    await update.message.reply_text(f"♻️ {CATEGORY_LABELS.get(category_key, category_key)} price ကို default ပြန်ထားပြီးပါပြီ။")


# =========================================================
# MENU NAVIGATION
# =========================================================
async def open_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str) -> None:
    reset_user_state(context)
    set_flow_value(context, "category_key", category_key)

    if category_key == "mobile_legends":
        await update.message.reply_text(
            "🎮 *Mobile Legends*\n\nကျေးဇူးပြု၍ အမျိုးအစားရွေးပါ။",
            parse_mode="Markdown",
            reply_markup=ml_keyboard(),
        )
        return

    if category_key == "telegram_services":
        await update.message.reply_text(
            "⭐ *Telegram Services*\n\nကျေးဇူးပြု၍ အမျိုးအစားရွေးပါ။",
            parse_mode="Markdown",
            reply_markup=telegram_keyboard(),
        )
        return

    section_key = "🏷️ Items"
    set_flow_value(context, "section_key", section_key)
    await update.message.reply_text(
        f"{CATEGORY_LABELS[category_key]}\n\n📌 ကျေးဇူးပြု၍ Item ရွေးပါ။",
        reply_markup=item_list_keyboard(category_key, section_key),
    )


async def open_section(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str, section_key: str) -> None:
    set_flow_value(context, "category_key", category_key)
    set_flow_value(context, "section_key", section_key)
    await update.message.reply_text(
        f"{CATEGORY_LABELS[category_key]}\n\n📌 {section_key} မှာ Item ရွေးပါ။",
        reply_markup=item_list_keyboard(category_key, section_key),
    )


async def handle_item_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, item_line: str) -> None:
    category_key = get_flow_value(context, "category_key")
    section_key = get_flow_value(context, "section_key")

    if not category_key or not section_key:
        await show_main_menu(update, context)
        return

    if item_line not in prices_data.get(category_key, {}).get(section_key, {}):
        await update.message.reply_text("❌ Item မတွေ့ပါ။")
        return

    set_flow_value(context, "item_line", item_line)
    context.user_data["awaiting"] = "account_info"

    await update.message.reply_text(
        f"🛒 *ရွေးထားသော Item*\n\n{item_line}\n\n{account_prompt_for(category_key)}",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


# =========================================================
# PAYMENT / ORDER CREATION
# =========================================================
async def send_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str) -> None:
    set_flow_value(context, "payment_method", method)
    context.user_data["awaiting"] = "payment_screenshot"

    if method == "KBZPay":
        msg = (
            "💜 *KBZPay Payment*\n\n"
            f"👤 Name: `{KBZPAY_NAME}`\n"
            f"📱 Phone: `{KBZPAY_PHONE}`\n\n"
            "📸 ငွေလွှဲပြီး screenshot ပို့ပါ။"
        )
    else:
        msg = (
            "💙 *WavePay Payment*\n\n"
            f"👤 Name: `{WAVEPAY_NAME}`\n"
            f"📱 Phone: `{WAVEPAY_PHONE}`\n\n"
            "📸 ငွေလွှဲပြီး screenshot ပို့ပါ။"
        )

    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=payment_keyboard(),
    )


def create_order_record(user, flow: dict[str, Any]) -> dict[str, Any]:
    return {
        "order_id": flow["order_id"],
        "time": flow["time"],
        "buyer_name": user.full_name,
        "buyer_username": user.username or "",
        "buyer_id": user.id,
        "buyer_display": buyer_display_name(user),
        "category_key": flow["category_key"],
        "category_label": CATEGORY_LABELS.get(flow["category_key"], flow["category_key"]),
        "section_key": flow.get("section_key", ""),
        "item_line": flow["item_line"],
        "account_info": flow["account_info"],
        "payment_method": flow["payment_method"],
        "status": flow.get("status", "Pending"),
        "cancel_reason": flow.get("cancel_reason", ""),
        "admin_message_id": None,
        "screenshot_file_id": flow["screenshot_file_id"],
    }


def format_admin_caption(order: dict[str, Any]) -> str:
    lines = [
        "🚨 *New Order*",
        "",
        f"🧾 Order ID: {order['order_id']}",
        f"⏰ Time: {order['time']}",
        f"🎮 Category: {order['category_label']}",
        f"🛍️ Item: {order['item_line']}",
        f"🆔 Account: {order['account_info']}",
        f"💳 Payment: {order['payment_method']}",
        "",
        f"👤 Buyer: {order['buyer_display']}",
        "",
    ]

    status = order["status"]
    if status == "Completed":
        lines.append("📌 Status: Completed ✅")
    elif status == "Cancelled":
        lines.append("📌 Status: Cancelled ❌")
        if order.get("cancel_reason"):
            lines.append(f"📝 Reason: {order['cancel_reason']}")
    else:
        lines.append("📌 Status: Pending ⏳")

    return "\n".join(lines)


def format_buyer_success(order: dict[str, Any]) -> str:
    return (
        "📦 *Order Received*\n\n"
        f"🧾 Order ID: {order['order_id']}\n"
        f"⏰ Time: {order['time']}\n"
        f"🛍️ Item: {order['item_line']}\n\n"
        "📌 Status: Pending ⏳\n\n"
        "Admin မှ စစ်ဆေးပြီး မကြာခင်ဆောင်ရွက်ပေးပါမည်။\n\n"
        "🙏 Thank you for using Phoenix Item Shop"
    )


async def finalize_order_with_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    flow = context.user_data.get("flow", {})
    user = update.effective_user

    if not flow.get("account_info"):
        await update.message.reply_text("❌ Game ID / Account info မရှိသေးပါ။")
        return

    if not flow.get("payment_method"):
        await update.message.reply_text("❌ Payment method မရွေးရသေးပါ။")
        return

    photo = update.message.photo[-1]
    order_id = get_next_order_id()

    flow["order_id"] = order_id
    flow["time"] = current_time_str()
    flow["status"] = "Pending"
    flow["screenshot_file_id"] = photo.file_id

    order = create_order_record(user, flow)
    orders_data[order_id] = order
    save_orders()

    sent = await context.bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=photo.file_id,
        caption=format_admin_caption(order),
        parse_mode="Markdown",
        reply_markup=admin_order_inline(order_id),
    )
    orders_data[order_id]["admin_message_id"] = sent.message_id
    save_orders()

    await update.message.reply_text(
        format_buyer_success(order),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    reset_user_state(context)


# =========================================================
# ADMIN BUTTONS
# =========================================================
async def handle_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_USER_ID:
        return

    data = query.data
    action, order_id = data.split(":", 1)

    if order_id not in orders_data:
        return

    order = orders_data[order_id]

    if action == "pending":
        order["status"] = "Pending"
        order["cancel_reason"] = ""
        save_orders()
        await query.edit_message_caption(
            caption=format_admin_caption(order),
            parse_mode="Markdown",
            reply_markup=admin_order_inline(order_id),
        )
        return

    if action == "complete":
        order["status"] = "Completed"
        order["cancel_reason"] = ""
        save_orders()

        await query.edit_message_caption(
            caption=format_admin_caption(order),
            parse_mode="Markdown",
            reply_markup=admin_order_inline(order_id),
        )

        await context.bot.send_message(
            chat_id=order["buyer_id"],
            text=(
                "📦 *Order Update*\n\n"
                f"🧾 Order ID: {order_id}\n"
                "📌 Status: Completed ✅\n"
                "ဖြည့်သွင်းပြီးပါပြီ။\n\n"
                "🙏 Thank you for using Phoenix Item Shop"
            ),
            parse_mode="Markdown",
            reply_markup=buy_again_inline(),
        )
        return

    if action == "cancel":
        context.bot_data["cancel_waiting_admin"] = update.effective_user.id
        context.bot_data["cancel_waiting_order_id"] = order_id
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                f"❌ *Cancel Reason ထည့်ပါ*\n\n"
                f"Order ID: `{order_id}`\n"
                "ကျေးဇူးပြု၍ cancel reason ပို့ပါ။"
            ),
            parse_mode="Markdown",
        )
        return


async def handle_buy_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="🛒 နောက်တစ်ခါဝယ်ယူရန် Menu ရွေးပါ။",
        reply_markup=main_menu_keyboard(),
    )


# =========================================================
# TEXT ROUTER
# =========================================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    awaiting = context.user_data.get("awaiting")

    # -------- Cancel reason by admin --------
    waiting_admin = context.bot_data.get("cancel_waiting_admin")
    waiting_order_id = context.bot_data.get("cancel_waiting_order_id")
    if waiting_admin == update.effective_user.id and waiting_order_id:
        order = orders_data.get(waiting_order_id)
        if order:
            order["status"] = "Cancelled"
            order["cancel_reason"] = text
            save_orders()

            try:
                await context.bot.edit_message_caption(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=order["admin_message_id"],
                    caption=format_admin_caption(order),
                    parse_mode="Markdown",
                    reply_markup=admin_order_inline(waiting_order_id),
                )
            except Exception as e:
                logger.warning("Failed editing caption: %s", e)

            await context.bot.send_message(
                chat_id=order["buyer_id"],
                text=(
                    "📦 *Order Update*\n\n"
                    f"🧾 Order ID: {waiting_order_id}\n"
                    "📌 Status: Cancelled ❌\n\n"
                    f"📝 Reason: {text}\n\n"
                    "အသေးစိတ်အတွက် admin ကိုဆက်သွယ်ပါ။\n"
                    "🙏 Thank you for using Phoenix Item Shop"
                ),
                parse_mode="Markdown",
                reply_markup=buy_again_inline(),
            )

        context.bot_data["cancel_waiting_admin"] = None
        context.bot_data["cancel_waiting_order_id"] = None
        await update.message.reply_text("✅ Cancel reason သိမ်းပြီးပါပြီ။")
        return

    # -------- Awaiting order status id --------
    if awaiting == "order_status_id":
        order_id = text.upper()
        order = orders_data.get(order_id)
        context.user_data["awaiting"] = None

        if not order:
            await update.message.reply_text(
                "❌ Order ID မတွေ့ပါ။\n\n📌 Example: ORD-100",
                reply_markup=main_menu_keyboard(),
            )
            return

        status_emoji = "⏳"
        status_text = "Pending"
        if order["status"] == "Completed":
            status_emoji = "✅"
            status_text = "Completed"
        elif order["status"] == "Cancelled":
            status_emoji = "❌"
            status_text = "Cancelled"

        msg = (
            "📊 *Order Status*\n\n"
            f"🧾 Order ID: {order_id}\n"
            f"⏰ Time: {order['time']}\n"
            f"🛍️ Item: {order['item_line']}\n"
            f"📌 Status: {status_text} {status_emoji}"
        )
        if order["status"] == "Cancelled" and order.get("cancel_reason"):
            msg += f"\n📝 Reason: {order['cancel_reason']}"

        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        return

    # -------- Awaiting account info --------
    if awaiting == "account_info":
        category_key = get_flow_value(context, "category_key")
        if not is_valid_account_input(category_key, text):
            await update.message.reply_text(
                "❌ Format မမှန်ပါ။\n\n" + account_prompt_for(category_key),
                parse_mode="Markdown",
            )
            return

        set_flow_value(context, "account_info", text)
        context.user_data["awaiting"] = None
        await update.message.reply_text(
            "💳 *Payment Method ရွေးပါ။*",
            parse_mode="Markdown",
            reply_markup=payment_keyboard(),
        )
        return

    # -------- Main menu entries --------
    if text == "🎮 Mobile Legends":
        await open_category(update, context, "mobile_legends")
        return

    if text == "🎯 PUBG":
        await open_category(update, context, "pubg")
        return

    if text == "🔥 Free Fire":
        await open_category(update, context, "free_fire")
        return

    if text == "⚔️ HOK":
        await open_category(update, context, "hok")
        return

    if text == "⭐ Telegram":
        await open_category(update, context, "telegram_services")
        return

    if text == "📦 Other":
        await update.message.reply_text(
            "📦 *Other Services*\n\nComing Soon...\nလိုအပ်ပါက admin ကိုဆက်သွယ်ပါ။",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        return

    if text == "📞 Contact Admin":
        await contact_admin(update, context)
        return

    if text == "📊 Order Status":
        await order_status_command(update, context)
        return

    if text == "🔙 Back":
        category_key = get_flow_value(context, "category_key")
        section_key = get_flow_value(context, "section_key")

        if category_key == "mobile_legends" and section_key:
            set_flow_value(context, "section_key", None)
            await update.message.reply_text(
                "🎮 *Mobile Legends*\n\nကျေးဇူးပြု၍ အမျိုးအစားရွေးပါ။",
                parse_mode="Markdown",
                reply_markup=ml_keyboard(),
            )
            return

        if category_key == "telegram_services" and section_key:
            set_flow_value(context, "section_key", None)
            await update.message.reply_text(
                "⭐ *Telegram Services*\n\nကျေးဇူးပြု၍ အမျိုးအစားရွေးပါ။",
                parse_mode="Markdown",
                reply_markup=telegram_keyboard(),
            )
            return

        await show_main_menu(update, context)
        return

    # -------- ML sections --------
    if text == "💥 2X Promo":
        await open_section(update, context, "mobile_legends", "💥 2X Promo")
        return

    if text == "💎 Normal":
        await open_section(update, context, "mobile_legends", "💎 Normal")
        return

    # -------- Telegram sections --------
    if text == "⭐ Star":
        await open_section(update, context, "telegram_services", "⭐ Star")
        return

    if text == "👑 Premium":
        await open_section(update, context, "telegram_services", "👑 Premium")
        return

    # -------- Payment --------
    if text == "💜 KBZPay":
        await send_payment_info(update, context, "KBZPay")
        return

    if text == "💙 WavePay":
        await send_payment_info(update, context, "WavePay")
        return

    if text == "❌ Cancel":
        reset_user_state(context)
        await update.message.reply_text(
            "❌ Order ကို cancel လုပ်ပြီးပါပြီ။",
            reply_markup=main_menu_keyboard(),
        )
        return

    # -------- Item selection --------
    category_key = get_flow_value(context, "category_key")
    section_key = get_flow_value(context, "section_key")
    if category_key and section_key:
        if text in prices_data.get(category_key, {}).get(section_key, {}):
            await handle_item_selection(update, context, text)
            return

    # -------- Silent ignore admin-like commands from buyer --------
    if text.startswith("/"):
        return

    # fallback
    await update.message.reply_text(
        "📌 ကျေးဇူးပြု၍ Menu ထဲကနေရွေးပါ။",
        reply_markup=main_menu_keyboard(),
    )


# =========================================================
# PHOTO HANDLER
# =========================================================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("awaiting") != "payment_screenshot":
        await update.message.reply_text(
            "📸 Screenshot ကို payment step ရောက်မှပို့ပါ။",
            reply_markup=main_menu_keyboard(),
        )
        return

    flow = context.user_data.get("flow", {})
    if not flow.get("account_info"):
        await update.message.reply_text("❌ Game ID / Account info မရှိသေးပါ။")
        return
    if not flow.get("payment_method"):
        await update.message.reply_text("❌ Payment method မရွေးရသေးပါ။")
        return

    await finalize_order_with_photo(update, context)


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adminhelp", help_admin_commands))
    app.add_handler(CommandHandler("setprice", setprice_command))
    app.add_handler(CommandHandler("showprice", showprice_command))
    app.add_handler(CommandHandler("resetprice", resetprice_command))

    app.add_handler(CallbackQueryHandler(handle_admin_button, pattern=r"^(complete|cancel|pending):"))
    app.add_handler(CallbackQueryHandler(handle_buy_again, pattern=r"^buy_again$"))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Phoenix Item Shop Bot is running 🚀")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()