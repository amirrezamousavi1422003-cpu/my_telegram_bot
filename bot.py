import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time

# --- بخش وب‌سرور برای زنده نگه داشتن در Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Alive!")

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- تنظیمات ربات تلگرام ---
TOKEN = os.getenv("BOT_TOKEN")
is_active = True
user_last_msg_time = {}
GREETINGS = ["سلام", "hello", "hi", "درود", "چطوری", "hey"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات فعال شد! ادمین‌ها با /toggle کنترل می‌کنند.")

async def toggle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    user_status = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        is_active = not is_active
        status = "✅ روشن" if is_active else "❌ خاموش"
        await update.message.reply_text(f"وضعیت: {status}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    if not is_active or not update.message.text: return
    text = update.message.text.lower()
    if any(greet in text for greet in GREETINGS):
        await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز!")

def main():
    # روشن کردن وب‌سرور در یک رشته (Thread) جداگانه
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # اجرای ربات
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("toggle", toggle_bot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot and Health Server are running...")
    app.run_polling()

if __name__ == "__main__":
    main()
