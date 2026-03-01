import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIGURATION =================
# 1. Replace with your actual Telegram Bot Token
TOKEN = '8772711375:AAHzZDZPT8FrVmvvOmLiGrhtB5B8TbwG_Yo'

# 2. Replace with your __test cookie value from your browser
MY_COOKIE = 'PASTE_YOUR_COOKIE_HERE'
# =================================================

# Enable logging to see what the bot is doing in the Koyeb logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hello! I am your API Bot.\n\n"
        "Send me an ID (e.g., vvk1411), and I will fetch the data for you.\n"
        "Note: If I stop responding, your cookie might have expired!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches data from the API using the user's input as the ID."""
    user_id = update.message.text.strip()
    api_url = f"https://usesir.gt.tc/instakinum?id={user_id}"
    
    # Show 'typing' in Telegram so the user knows we are working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Headers to mimic a real mobile browser to help bypass security
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }
    
    # This cookie is the 'key' that unlocks the website's security
    cookies = {
        '__test': MY_COOKIE
    }

    try:
        # Send the request to the API
        response = requests.get(api_url, headers=headers, cookies=cookies, timeout=15)
        
        # Check if we were blocked by the JavaScript challenge
        if "slowAES" in response.text or "javascript" in response.text.lower():
            await update.message.reply_text(
                "❌ **Security Blocked**\n\n"
                "The `__test` cookie has expired. Please get a new one from your "
                "browser and update the `main.py` file on GitHub."
            )
        else:
            # If successful, send the API data back to the user
            # We use [:4000] to ensure we don't exceed Telegram's message limit
            await update.message.reply_text(f"✅ **Results:**\n\n{response.text[:4000]}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error connecting to API: {str(e)}")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Register the command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C or the process is stopped
    print("Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
