import sqlite3
from pyshorteners import Shortener
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# Connect to the database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Database table creation
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER UNIQUE,
                   is_premium INTEGER DEFAULT 0)''')

# Function to handle the '/start' command
def start(update, context):
    user_id = update.effective_user.id
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            # Premium user
            context.bot.send_message(chat_id=user_id, text="Welcome, premium user! You have direct file access.")
        else:
            # Non-premium user
            context.bot.send_message(chat_id=user_id, text="Welcome! Please use the /file command to get the shortened URL.")
    else:
        # New user
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        context.bot.send_message(chat_id=user_id, text="Welcome! Please use the /subscribe command to become a premium user.")

# Function to handle the '/subscribe' command
def subscribe(update, context):
    user_id = update.effective_user.id
    cursor.execute("UPDATE users SET is_premium=1 WHERE user_id=?", (user_id,))
    conn.commit()
    context.bot.send_message(chat_id=user_id, text="Congratulations! You are now a premium user.")

# Function to handle the '/cancel' command
def cancel_subscription(update, context):
    user_id = update.effective_user.id
    cursor.execute("UPDATE users SET is_premium=0 WHERE user_id=?", (user_id,))
    conn.commit()
    context.bot.send_message(chat_id=user_id, text="Your subscription has been canceled. You are now a non-premium user.")

# Function to handle the '/file' command
def file_command(update, context):
    user_id = update.effective_user.id
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            # Premium user
            context.bot.send_document(chat_id=user_id, document=open('file.mkv', 'rb'))
        else:
            # Non-premium user
            shortener = Shortener()
            short_url = shortener.short('https://example.com/file.mkv')
            context.bot.send_message(chat_id=user_id, text=f"Here is the URL: {short_url}")

# Create the updater and dispatcher
updater = Updater('YOUR_TELEGRAM_BOT_TOKEN', use_context=True)
dispatcher = updater.dispatcher

# Add command handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('subscribe', subscribe))
dispatcher.add_handler(CommandHandler('cancel', cancel_subscription))
dispatcher.add_handler(CommandHandler('file', file_command))

# Start the bot
updater.start_polling()
