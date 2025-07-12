import logging
import asyncio
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
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ====== تنظیمات اصلی ======
TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
CHANNEL_USERNAME = "cinema_zone_channel"  # یوزرنیم کانال بدون @
SUPPORT_USER_ID = 7774213647  # ایدی تلگرام خودت (ادمین)
REQUIRED_REACTIONS = 5  # حداقل تعداد واکنش در 5 پست اخیر

# ====== لاگینگ ======
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====== چک عضویت ======
async def is_user_member(app: Application, user_id: int) -> bool:
    try:
        member = await app.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
        ]
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False

# ====== چک ری‌اکشن (تخمینی) ======
async def has_enough_reactions(app: Application, user_id: int) -> bool:
    # توجه: تلگرام API رسمی برای واکنش (ری‌اکشن) در بات‌ها نداره،
    # اینجا یک نمونه ساختگی است و باید با روش دیگه یا API های غیررسمی بررسی کنی.
    # برای نمونه اینجا فرض میکنیم همیشه True برمیگردد
    return True  # یا False برای تست

# ====== منوی اصلی کاربران (غیرمدیر) ======
async def user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == SUPPORT_USER_ID:
        # ادمین منو مخصوص
        await admin_menu(update, context)
        return

    is_member = await is_user_member(context.application, user_id)
    if not is_member:
        # کاربر عضو نیست فقط لینک عضویت نشون بده بدون دکمه ارتباط با پشتیبانی
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال 🎬", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام!\nبرای استفاده از ربات باید ابتدا عضو کانال ما شوید.",
            reply_markup=reply_markup,
        )
        return

    # اگر عضو بود
    # دکمه ارتباط با پشتیبانی و لینک عضویت (این دکمه برای اطمینان دوباره عضو شدم باشه)
    keyboard = [
        [InlineKeyboardButton("ارتباط با پشتیبانی 📞", callback_data="support")],
        [InlineKeyboardButton("لینک کانال 🎬", url=f"https://t.me/{CHANNEL_USERNAME}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! خوش آمدید. برای ارسال فیلم و سریال منتظر پیام از مدیریت باشید.",
        reply_markup=reply_markup,
    )

# ====== منوی ادمین ======
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("آپلود فیلم/سریال 🎬", callback_data="upload_media")],
        [InlineKeyboardButton("ارسال فیلم به اعضا 📤", callback_data="send_media")],
        [InlineKeyboardButton("تنظیمات ⚙️", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("پنل مدیریت:", reply_markup=reply_markup)

# ====== هندلر دکمه‌ها ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != SUPPORT_USER_ID and query.data != "support":
        await query.answer("دسترسی ندارید.", show_alert=True)
        return

    data = query.data
    await query.answer()

    if data == "support":
        # فقط وقتی عضو کانال هست پیام پشتیبانی نشون بده
        is_member = await is_user_member(context.application, user_id)
        if not is_member:
            await query.edit_message_text("برای ارتباط با پشتیبانی ابتدا عضو کانال شوید.")
            return
        await query.edit_message_text("برای ارتباط با پشتیبانی لطفا پیام خود را اینجا ارسال کنید.")
        context.user_data["awaiting_support"] = True

    elif data == "upload_media":
        await query.edit_message_text("لطفا فایل فیلم یا سریال را ارسال کنید.")
        context.user_data["awaiting_upload"] = True

    elif data == "send_media":
        if "uploaded_file" not in context.bot_data:
            await query.edit_message_text("ابتدا فیلم یا سریالی آپلود کنید.")
            return
        await query.edit_message_text("در حال ارسال فیلم به اعضا...")

        # ارسال فیلم به اعضا (فقط به کسانی که عضو کانال هستند و واکنش کافی دارند)
        count_sent = 0
        async for member in context.application.bot.get_chat_administrators(f"@{CHANNEL_USERNAME}"):
            pass  # نمی‌توان اعضای کانال را با این روش گرفت؛ تلگرام API رسمی نداره
        # پس به عنوان نمونه فقط خود مدیر میفرستیم
        try:
            await context.bot.send_document(
                chat_id=SUPPORT_USER_ID,
                document=context.bot_data["uploaded_file"],
                caption="فیلم جدید از مدیر"
            )
            count_sent += 1
        except Exception as e:
            logger.error(f"Error sending media: {e}")
        await query.edit_message_text(f"فیلم به {count_sent} نفر ارسال شد. (نمونه فقط به مدیر ارسال شد)")

    elif data == "settings":
        await query.edit_message_text("در حال حاضر تنظیمات ندارد.")

# ====== هندلر پیام‌ها ======
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # اگر مدیر هست
    if user_id == SUPPORT_USER_ID:
        if context.user_data.get("awaiting_upload"):
            # ذخیره فایل ارسالی
            file = update.message.document or update.message.video
            if not file:
                await update.message.reply_text("لطفا فقط فایل ویدیو یا سند ارسال کنید.")
                return
            file_id = file.file_id
            context.bot_data["uploaded_file"] = file_id
            await update.message.reply_text("فایل با موفقیت دریافت شد.\nبرای ارسال به اعضا از منوی مدیریت استفاده کنید.")
            context.user_data["awaiting_upload"] = False
            return

    # اگر پیام برای ارتباط با پشتیبانی باشه
    if context.user_data.get("awaiting_support"):
        await update.message.reply_text("پیام شما به پشتیبانی ارسال شد. به زودی پاسخ داده می‌شود.")
        # ارسال پیام به مدیر
        try:
            user = update.effective_user
            await context.bot.send_message(
                chat_id=SUPPORT_USER_ID,
                text=(
                    f"پیام پشتیبانی از کاربر:\n"
                    f"نام: {user.full_name}\n"
                    f"آیدی: {user.id}\n"
                    f"یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
                    f"متن: {update.message.text}"
                )
            )
        except Exception as e:
            logger.error(f"Error forwarding support message: {e}")
        context.user_data["awaiting_support"] = False
        return

    # بقیه کاربران هیچ پیام متنی نمی‌تونن بفرستن

# ====== استارت ======
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await user_start(update, context)

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), message_handler))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
