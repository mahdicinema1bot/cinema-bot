import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)

# --- تنظیمات اولیه ---
TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
ADMIN_ID = 7774213647  # آیدی عددی تلگرام خودت
CHANNEL_USERNAME = "@cinema_zone_channel"  # یوزرنیم کانال (با @)

# --- دیتا ذخیره‌شده ساده به صورت دیکشنری (موقعی که ربات ری‌استارت میشه پاک میشه)
data = {
    "files": {},  # لینک‌ها و فایل‌های آپلود شده به شکل {کد: {"file_id": ..., "title": ...}}
    "force_join": True,
    "admin_id": ADMIN_ID,
    "channel_username": CHANNEL_USERNAME,
    "waiting_for_support_msg": set(),  # کاربرانی که در حال نوشتن پیام پشتیبانی هستند
    "waiting_for_file": False,
    "waiting_file_user": None,
    "file_code_counter": 0,
}

# --- کد وضعیت Conversation برای گرفتن پیام پشتیبانی و فایل ---
SUPPORT_MSG, ADMIN_UPLOAD = range(2)

# --- کیبوردها ---

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("ارتباط با پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("مدیریت", callback_data="admin")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]])

# --- توابع کمکی ---

async def check_membership(user_id, bot, channel_username):
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
        else:
            return False
    except:
        return False

# --- هندلرها ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name}!\n"
        "برای استفاده کامل ربات لطفا ابتدا عضو کانال ما شوید.\n"
        f"{CHANNEL_USERNAME}\n\n"
        "بعد از عضو شدن، /start را دوباره بزنید.",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("از منو زیر یکی را انتخاب کنید.", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "support":
        # فرستادن پیام به حالت دریافت پیام پشتیبانی
        data["waiting_for_support_msg"].add(user.id)
        await query.edit_message_text(
            "لطفا پیام خود را بنویسید و ارسال کنید. پس از ارسال، پیام شما به من (پشتیبان) خواهد رسید.",
            reply_markup=back_button_keyboard()
        )

    elif query.data == "admin":
        if user.id == ADMIN_ID:
            await query.edit_message_text(
                "خوش آمدید به پنل مدیریت. لطفا فایل ویدئویی یا سند را اینجا ارسال کنید.",
                reply_markup=back_button_keyboard()
            )
            data["waiting_for_file"] = True
            data["waiting_file_user"] = user.id
        else:
            await query.edit_message_text(
                "❌ شما دسترسی مدیریت ندارید.",
                reply_markup=back_button_keyboard()
            )

    elif query.data == "back_main":
        await query.edit_message_text("منوی اصلی:", reply_markup=main_menu_keyboard())

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in data["waiting_for_support_msg"]:
        text = update.message.text
        # ارسال پیام به ادمین
        user = update.effective_user
        msg = f"پیام پشتیبانی از @{user.username} (id: {user.id}):\n\n{text}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text("✅ پیام شما به پشتیبانی ارسال شد. به زودی پاسخ می‌دهیم.")
        data["waiting_for_support_msg"].remove(user_id)
    else:
        await update.message.reply_text("از منو استفاده کنید.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if data["waiting_for_file"] and data["waiting_file_user"] == user_id:
        # ذخیره فایل و دادن کد به ادمین
        file = update.message.document or update.message.video
        if not file:
            await update.message.reply_text("لطفا فقط فایل ویدئو یا سند ارسال کنید.")
            return

        data["file_code_counter"] += 1
        code = f"file{data['file_code_counter']}"
        file_id = file.file_id
        title = file.file_name if hasattr(file, 'file_name') else "فیلم جدید"

        data["files"][code] = {"file_id": file_id, "title": title}
        data["waiting_for_file"] = False
        data["waiting_file_user"] = None

        await update.message.reply_text(
            f"✅ فایل با موفقیت ذخیره شد.\n"
            f"کد لینک فیلم: /send_{code}\n\n"
            "کاربران برای دریافت فیلم باید ابتدا عضو کانال شوند و سپس دستور را ارسال کنند."
        )
    else:
        await update.message.reply_text("شما اجازه آپلود فایل ندارید.")

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not text.startswith("/send_"):
        return

    code = text[6:]
    if code not in data["files"]:
        await update.message.reply_text("❌ فایل پیدا نشد.")
        return

    # چک عضویت
    joined = await check_membership(user_id, context.bot, CHANNEL_USERNAME)
    if not joined:
        warning = await update.message.reply_text(
            f"⚠️ لطفا ابتدا عضو کانال شوید:\n{CHANNEL_USERNAME}\n"
            "سپس دوباره /start را بزنید تا فیلم برایتان ارسال شود."
        )
        await asyncio.sleep(30)
        await warning.delete()
        return

    file_id = data["files"][code]["file_id"]
    await update.message.reply_document(file_id)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور ناشناخته است. لطفا از منو استفاده کنید.")

# --- تنظیم و اجرای ربات ---

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL, handle_document))
    application.add_handler(MessageHandler(filters.Regex(r"^/send_"), send_file))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
