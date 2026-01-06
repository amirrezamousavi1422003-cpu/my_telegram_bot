import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time

# تنظیمات اولیه
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) # آیدی عددی شما
is_active = True
user_last_msg_time = {} # برای جلوگیری از اسپم

# لیست سلام‌ها به زبان‌های مختلف
GREETINGS = ["سلام", "hello", "hi", "hola", "bonjour", "salaam", "درود"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات مدیریت سلام فعال شد!")

async def toggle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    if update.effective_user.id == ADMIN_ID:
        is_active = not is_active
        status = "روشن" if is_active else "خاموش"
        await update.message.reply_text(f"وضعیت ربات: {status}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    if not is_active or not update.message.text:
        return

    user_id = update.effective_user.id
    current_time = time.time()
    text = update.message.text.lower()

    # سیستم ضد اسپم (هر کاربر هر ۱۰ ثانیه فقط یک جواب می‌گیرد)
    if user_id in user_last_msg_time:
        if current_time - user_last_msg_time[user_id] < 10:
            return

    # بررسی وجود سلام در پیام
    if any(greet in text for greet in GREETINGS):
        user_last_msg_time[user_id] = current_time
        await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز! خوش آمدی.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("toggle", toggle_bot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if _name_ == "__main__":
    main()
