import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

CHANNEL_ID = "@cinema_zone_channel"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # چک عضویت در کانال
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text("🎬 خوش اومدی! عضو کانال هستی ✅")
        else:
            raise Exception("Not a member")
    except:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/cinema_zone_channel")]
        ])
        await update.message.reply_text(
            "برای استفاده از ربات باید اول عضو کانال بشی 👇", 
            reply_markup=keyboard
        )

def main():
    TOKEN = os.environ['BOT_TOKEN']
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))  # برای هر پیامی هم همون واکنش

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
