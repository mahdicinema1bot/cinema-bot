import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import asyncio

# ✅ توکن ربات
TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"

# ✅ آیدی عددی مدیریت
ADMIN_ID = 7774213647

# ✅ آیدی کانال و پشتیبانی
CHANNEL_USERNAME = "@cinema_zone_channel"
SUPPORT_ID = "@Cinemazone1support"

# ذخیره لینک‌ها (کلید = کد، مقدار = file_id)
file_links = {}

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [
        [InlineKeyboardButton("🎬 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("🆘 ارتباط با پشتیبانی", url=f"https://t.me/{SUPPORT_ID[1:]}")]
    ]

    if user.id == ADMIN_ID:
        buttons.append([InlineKeyboardButton("🎥 بخش مدیریت", callback_data="admin_panel")])

    await update.message.reply_text(
        f"سلام {user.first_name} 👋\n\n"
        f"🎉 خوش آمدید به ربات سینما زون!\n"
        f"برای فعال شدن کامل ربات، ابتدا عضو کانال زیر شوید:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ دکمه مدیریت برای خودت
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ فقط مدیریت به این بخش دسترسی دارد.")
        return
    await query.edit_message_text("📤 لطفاً یک فیلم یا فایل آپلود کنید تا لینک ساخته شود.")

# ✅ آپلود توسط مدیر
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ فقط مدیریت می‌تواند فایل آپلود کند.")
        return

    file = update.message.document or update.message.video
    if not file:
        await update.message.reply_text("❗ لطفاً یک فایل یا ویدیو ارسال کنید.")
        return

    file_id = file.file_id
    link_code = file.file_unique_id[-6:]
    file_links[link_code] = file_id

    await update.message.reply_text(f"✅ لینک ساخته شد:\n🔗 /send_{link_code}")

# ✅ ارسال فایل فقط در صورت عضویت
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    code = command.replace("/send_", "")
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["left", "kicked"]:
            warning = await update.message.reply_text("⛔ برای دریافت فایل، ابتدا عضو کانال شوید و سپس مجدداً /start بزنید.")
            await asyncio.sleep(30)
            await warning.delete()
            return
    except Exception:
        await update.message.reply_text("⚠️ خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.")
        return

    if code in file_links:
        await update.message.reply_document(file_links[code])
    else:
        await update.message.reply_text("❌ فایل پیدا نشد.")

# ✅ راه‌اندازی ربات
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^/send_"), send_file))

    print("✅ ربات سینما زون روشن شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
