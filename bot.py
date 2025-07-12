import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
CHANNEL_USERNAME = "@CinemaZone1"  # یوزرنیم کانال تو
SUPPORT_ID = 7774213647  # ایدی عددی خودت (ادمین)
SUPPORT_USERNAME = "Cinemazone1support"  # یوزرنیم پشتیبانی (برای متن و دکمه)

# لیست پست‌های کانال برای چک لایک (به صورت message_idهای واقعی کانالت)
REQUIRED_CHANNEL_POSTS = [1, 2, 3, 4, 5]  # باید واقعی جایگزین کنی

# دکمه های اصلی
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("ارتباط با پشتیبانی", callback_data="support")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("آپلود فیلم جدید", callback_data="upload")],
        [InlineKeyboardButton("بازگشت", callback_data="back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]])

# بررسی عضویت کانال
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# چک ری‌اکشن روی پست‌های کانال
async def check_reactions(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    # متاسفانه API رسمی تلگرام ری‌اکشن‌ها رو نمیده به ربات، 
    # بنابراین اینجا فرض میکنیم که کاربر ری‌اکشن زده (برای مثال یا با دیتابیس خودت جایگزین کن)
    # اگر میخوای واقعی چک کنی باید از روش‌های غیررسمی یا دیتابیس استفاده کنی.
    return True

# هندلر استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_membership(user_id, context):
        await update.message.reply_text(
            "سلام! خوش آمدید.\nبرای دریافت فیلم‌ها از منوی زیر استفاده کنید.",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا باید عضو کانال ما شوید.",
            reply_markup=main_menu_keyboard()
        )

# هندلر کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "support":
        if await check_membership(user_id, context):
            # پیام کاربر را به ادمین ارسال کن
            await context.bot.send_message(
                chat_id=SUPPORT_ID,
                text=f"کاربر [{query.from_user.full_name}](tg://user?id={user_id}) درخواست پشتیبانی داده است.",
                parse_mode="Markdown"
            )
            await query.message.reply_text("پیام شما به پشتیبانی ارسال شد. منتظر پاسخ باشید.", reply_markup=back_keyboard())
        else:
            await query.message.reply_text(
                "برای استفاده از این امکان ابتدا باید عضو کانال شوید.",
                reply_markup=main_menu_keyboard()
            )
    elif query.data == "upload":
        # فقط ادمین دسترسی دارد
        if user_id == SUPPORT_ID:
            await query.message.reply_text("لطفا فیلم یا فایل خود را ارسال کنید.", reply_markup=back_keyboard())
            context.user_data["upload_mode"] = True
        else:
            await query.message.reply_text("شما دسترسی لازم را ندارید.", reply_markup=back_keyboard())
    elif query.data == "back":
        if user_id == SUPPORT_ID:
            await query.message.reply_text("منوی مدیریت", reply_markup=admin_menu_keyboard())
        else:
            await query.message.reply_text("منوی اصلی", reply_markup=main_menu_keyboard())

# هندلر دریافت فایل (فیلم یا داکیومنت)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != SUPPORT_ID:
        await update.message.reply_text("شما اجازه ارسال فایل ندارید.")
        return
    if not context.user_data.get("upload_mode", False):
        await update.message.reply_text("ابتدا روی دکمه 'آپلود فیلم جدید' کلیک کنید.")
        return

    file = update.message.document or update.message.video
    if not file:
        await update.message.reply_text("لطفا فقط فایل ویدیویی یا داکیومنت ارسال کنید.")
        return

    # ذخیره فایل و دریافت لینک
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else "فیلم شما"

    # ارسال لینک به مدیر
    file_link = f"https://t.me/{context.bot.username}?start={file_id}"
    context.user_data["upload_mode"] = False

    await update.message.reply_text(f"فیلم با موفقیت آپلود شد.\nلینک برای ارسال به کاربران:\n{file_link}")

# هندلر درخواست فیلم از کاربر
async def get_film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_membership(user_id, context):
        await update.message.reply_text(
            "برای دریافت فیلم ابتدا باید عضو کانال شوید.",
            reply_markup=main_menu_keyboard()
        )
        return

    if not await check_reactions(user_id, context):
        await update.message.reply_text(
            "برای دریافت فیلم ابتدا باید حداقل 5 ری‌اکشن روی پست‌های کانال بدهید.",
            reply_markup=main_menu_keyboard()
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text("لینک فیلم موجود نیست.")
        return

    file_id = args[0]

    # ارسال لینک فایل به کاربر
    await update.message.reply_text(
        f"فیلم آماده است:\nبرای مشاهده روی لینک زیر کلیک کنید:\nhttps://t.me/{context.bot.username}?start={file_id}",
        reply_markup=main_menu_keyboard()
    )

    # ارسال هشدار 30 ثانیه ای و حذف خودکار
    msg = await update.message.reply_text("این پیام پس از ۳۰ ثانیه حذف خواهد شد.")
    await asyncio.sleep(30)
    try:
        await msg.delete()
    except:
        pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای شروع /start را بزنید.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور ناشناخته. لطفا /start را بزنید.")

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("getfilm", get_film))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL, handle_document))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    await application.run_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
    except RuntimeError:
        asyncio.run(main())
