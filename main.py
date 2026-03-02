import asyncio
import binascii
import re
import json
import os
import httpx
from datetime import datetime
from Crypto.Cipher import AES
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURATION ---
# Using the token you provided
BOT_TOKEN = "8312590213:AAHSuBYHdk1Y4m-TrZNnuZM5g6LBZNuKTXE"
ADMIN_ID = 7602773447
DAILY_LIMIT = 10
USAGE_FILE = "user_usage.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://usesir.gt.tc/"
}

# --- USAGE TRACKING ---
def get_usage_data():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_usage_data(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_limit(user_id):
    if user_id == ADMIN_ID:
        return True, "∞"
    
    usage = get_usage_data()
    today = datetime.now().strftime("%Y-%m-%d")
    uid = str(user_id)
    
    if uid not in usage or usage[uid].get("date") != today:
        usage[uid] = {"count": 0, "date": today}
    
    if usage[uid]["count"] >= DAILY_LIMIT:
        return False, usage[uid]["count"]
    
    usage[uid]["count"] += 1
    save_usage_data(usage)
    return True, usage[uid]["count"]

# --- CORE LOGIC ---
def solve_challenge(html):
    try:
        matches = re.findall(r'toNumbers\("([a-f0-9]+)"\)', html)
        if len(matches) < 3: return None
        a, b, c = [binascii.unhexlify(x) for x in matches[:3]]
        cipher = AES.new(a, AES.MODE_CBC, iv=b)
        return binascii.hexlify(cipher.decrypt(c)).decode('utf-8')
    except: return None

async def search_database(num, client):
    url = "https://usesir.gt.tc/illfuvkyourpussy"
    if "__test" not in client.cookies:
        r1 = await client.get(url, params={"sex": num}, headers=HEADERS)
        cookie = solve_challenge(r1.text)
        if cookie:
            client.cookies.set("__test", cookie, domain="usesir.gt.tc")
    r2 = await client.get(url, params={"sex": num}, headers=HEADERS)
    return r2.json()

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🚀 **Bot Live on Railway 24/7**\n\n"
        "🔍 Use `/search <number>`\n"
        f"📊 Daily Limit: {DAILY_LIMIT}\n"
    )
    if update.effective_user.id == ADMIN_ID:
        welcome += "⚡ _Admin mode active._"
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    allowed, count = check_limit(user_id)
    
    if not allowed:
        await update.message.reply_text(f"🚫 Limit reached! ({DAILY_LIMIT}/{DAILY_LIMIT})")
        return

    if not context.args:
        await update.message.reply_text("❓ Please provide a number.")
        return

    num = re.sub(r'\D', '', context.args[0])
    if len(num) > 10 and num.startswith('91'): num = num[2:]
    
    status_msg = await update.message.reply_text(f"🔍 Searching... [{count}/{DAILY_LIMIT}]")

    async with httpx.AsyncClient(follow_redirects=True, timeout=25.0) as client:
        try:
            data = await search_database(num, client)
            if data.get("success") and data.get("result"):
                res = "📁 **Results Found**\n\n"
                for item in data["result"]:
                    res += (
                        f"👤 **Name:** {item.get('name')}\n"
                        f"🆔 **Aadhar:** `{item.get('aadhar_number')}`\n"
                        f"📍 **Addr:** {str(item.get('address')).replace('!', ' ')}\n"
                        f"──────────────────\n"
                    )
                await status_msg.edit_text(res, parse_mode="Markdown")
            else:
                await status_msg.edit_text("❌ No records found.")
        except Exception:
            await status_msg.edit_text("⚠️ Connection error.")

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    print("Bot is running on Railway...")
    app.run_polling()
