import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatMember,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# ====== تنظیمات اولیه ======
TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
CHANNEL_USERNAME = "@cinema_zone_channel"
SUPPORT_USERNAME = "@Cinemazone1support"
ADMIN_USER_ID = 7774213647

# ====== تنظیمات لاگ ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====== دیکشنری برای ذخیره فیلم‌ها (لینک‌ها) ======
# فقط مدیر می‌تواند لینک اضافه کند
movie_links = []

# ====== بررسی عضویت در کانال ======
async def is_member(update: Update, user_id: int) -> bool:
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if chat_member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]:
        return True
    else:
        await update.message.reply_text(
            f"لطفاً ابتدا در کانال {CHANNEL_USERNAME} عضو شوید و سپس دوباره /start را بزنید."
        )
        return False

# ====== پیام خوش آمد ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # چک عضویت
    try:
        is_in_channel = await check_channel_membership(update, context)
        if not is_in_channel:
            return
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        await update.message.reply_text("مشکلی پیش آمده، لطفاً دوباره تلاش کنید.")
        return

    keyboard = [
        [InlineKeyboardButton("📺 دریافت فیلم", callback_data="get_movie")],
        [InlineKeyboardButton("📞 ارتباط با پشتیبانی", callback_data="support")],
    ]

    # اگر مدیر است دکمه مدیریت را هم اضافه کن
    if user_id == ADMIN_USER_ID:
        keyboard.append([InlineKeyboardButton("🎬 مدیریت فیلم‌ها", callback_data="manage_movies")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "سلام! خوش آمدید به ربات سینما زون.\n"
        "برای استفاده کامل از ربات لطفا از دکمه‌های زیر استفاده کنید.",
        reply_markup=reply_markup,
    )

# ====== دکمه بازگشت ======
def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ====== هندلر دکمه‌ها ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # چک عضویت
    try:
        is_in_channel = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if is_in_channel.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await query.edit_message_text(
                f"❌ شما عضو کانال {CHANNEL_USERNAME} نیستید!\nلطفا ابتدا عضو شوید.",
                reply_markup=None,
            )
            return
    except Exception as e:
        logger.error(f"Error checking membership in button_handler: {e}")
        await query.edit_message_text("مشکلی پیش آمده، لطفا دوباره تلاش کنید.")
        return

    data = query.data

    if data == "back":
        await query.edit_message_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📺 دریافت فیلم", callback_data="get_movie")],
                    [InlineKeyboardButton("📞 ارتباط با پشتیبانی", callback_data="support")],
                    *([[InlineKeyboardButton("🎬 مدیریت فیلم‌ها", callback_data="manage_movies")]] if user_id == ADMIN_USER_ID else []),
                ]
            ),
        )
        return

    if data == "get_movie":
        if not movie_links:
            await query.edit_message_text("فیلمی فعلا اضافه نشده است.", reply_markup=back_button())
            return
        # برای نمونه فقط لینک اول را میفرستیم
        await query.edit_message_text(
            "برای دریافت فیلم روی لینک زیر کلیک کنید:\n" + movie_links[-1],
            reply_markup=back_button(),
        )
        return

    if data == "support":
        # ارتباط با پشتیبانی فقط اگر عضو کانال باشه
        # ارسال پیامی به پشتیبانی با مشخصات کاربر
        await query.edit_message_text(
            f"برای ارتباط با پشتیبانی لطفا به آیدی زیر پیام دهید:\n{SUPPORT_USERNAME}",
            reply_markup=back_button(),
        )
        return

    if data == "manage_movies":
        if user_id != ADMIN_USER_ID:
            await query.edit_message_text("❌ فقط مدیر مجاز است.", reply_markup=back_button())
            return
        await query.edit_message_text(
            "📤 لطفا فیلم یا لینک فیلم را ارسال کنید تا اضافه شود.\n"
            "همچنین می‌توانید لینک‌ها را مدیریت کنید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
                ]
            ),
        )
        return

# ====== دریافت فیلم/لینک توسط مدیر ======
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ شما اجازه ارسال فیلم ندارید.")
        return

    file_link = None
    # اگر فایل ارسال شده
    if update.message.document:
        file = update.message.document
        file_link = await context.bot.get_file(file.file_id)
        file_link = file_link.file_path
    # اگر ویدیو ارسال شده
    elif update.message.video:
        file = update.message.video
        file_link = await context.bot.get_file(file.file_id)
        file_link = file_link.file_path
    # اگر متن (لینک) ارسال شده
    elif update.message.text:
        file_link = update.message.text.strip()

    if not file_link:
        await update.message.reply_text("❌ فایل یا لینک معتبر ارسال کنید.")
        return

    # ذخیره لینک
    movie_links.append(file_link)

    await update.message.reply_text(f"🎉 لینک/فیلم با موفقیت ذخیره شد!\nتعداد فیلم‌ها: {len(movie_links)}")

# ====== پیام هشدار موقت (30 ثانیه) ======
async def temporary_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    msg = await update.message.reply_text(text)
    await asyncio.sleep(30)
    try:
        await msg.delete()
    except:
        pass

# ====== هندلر پیام‌ها ======
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط اعضا اجازه پیام دادن و دیدن لینک دارند
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text(
                f"❌ برای استفاده ابتدا عضو کانال {CHANNEL_USERNAME} شوید."
            )
            return
    except Exception:
        await update.message.reply_text(
            f"❌ برای استفاده ابتدا عضو کانال {CHANNEL_USERNAME} شوید."
        )
        return

    # اگر پیام مدیر است و حاوی لینک است
    if user_id == ADMIN_USER_ID and update.message.text:
        movie_links.append(update.message.text.strip())
        await update.message.reply_text("🎉 لینک با موفقیت اضافه شد!")
        return

    await update.message.reply_text("❌ پیام نامعتبر یا فرمان نادرست.")

# ====== هندلر خطا ======
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# ====== اجرای ربات ======
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.TEXT & ~filters.COMMAND, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_error_handler(error_handler)

    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # رفع ارور حلقه در حال اجرا

    import asyncio
    asyncio.run(main())
