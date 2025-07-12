from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# توکن رباتت رو اینجا بذار (موقتاً برای تست)
TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # پیام خوش آمد گویی با لینک کانال
    await update.message.reply_text(
        "سلام! خوش آمدید به ربات سینما زون 🎬\n"
        "برای دریافت فیلم‌ها و سریال‌ها به کانال ما مراجعه کنید:\n"
        "https://t.me/cinema_zone_channel"
    )

def main():
    app = Application.builder().token(TOKEN).build()

    # تعریف دستور /start
    app.add_handler(CommandHandler("start", start))

    print("ربات داره کار میکنه...")
    app.run_polling()

if __name__ == "__main__":
    main()
