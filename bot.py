import asyncio
import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

# --- تنظیمات ربات ---
BOT_TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
ADMIN_ID = 7774213647
CHANNEL_USERNAME = "cinema_zone_channel"  # بدون @
SUPPORT_USERNAME = "Cinemazone1support"  # بدون @

# تنظیم لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def is_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in [
            ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR
        ]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False


async def send_join_channel(update: Update):
    keyboard = [
        [InlineKeyboardButton("عضویت در کانال 🎬", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! برای استفاده از ربات ابتدا باید عضو کانال شوید.",
        reply_markup=reply_markup
    )


async def send_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("دریافت فیلم 🎥", callback_data="get_movie")],
        [InlineKeyboardButton("ارتباط با پشتیبانی 🛠", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("کانال فیلم و سریال 🎬", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "خوش آمدید! شما عضو کانال هستید.\n"
        "لطفا گزینه مورد نظر خود را انتخاب کنید.",
        reply_markup=reply_markup
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_member(user_id, context):
        await send_main_menu(update)
    else:
        await send_join_channel(update)


# وقتی دکمه "دریافت فیلم" کلیک شد
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not await is_member(user_id, context):
        await query.edit_message_text(
            "برای استفاده از این بخش باید ابتدا عضو کانال شوید."
        )
        return

    # فقط مدیر می‌تواند لینک فیلم بفرستد
    if user_id == ADMIN_ID:
        await query.edit_message_text(
            "برای ارسال لینک فیلم دستور زیر را در چت وارد کنید:\n"
            "/sendlink <لینک فیلم>"
        )
    else:
        await query.edit_message_text(
            "در حال حاضر فقط مدیر می‌تواند لینک فیلم ارسال کند.\n"
            "برای درخواست فیلم لطفا با پشتیبانی تماس بگیرید."
        )


# دستور ارسال لینک فیلم (فقط مدیر)
async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("شما اجازه ارسال لینک فیلم را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("لطفا لینک فیلم را بعد از دستور /sendlink وارد کنید.")
        return

    link = context.args[0]
    text = f"🎬 فیلم جدید آماده دانلود است:\n{link}"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("👍", callback_data="react_1"),
        InlineKeyboardButton("❤️", callback_data="react_2"),
        InlineKeyboardButton("🔥", callback_data="react_3"),
        InlineKeyboardButton("🎉", callback_data="react_4"),
        InlineKeyboardButton("😮", callback_data="react_5"),
    ]])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )


# هندل واکنش‌ها به پیام فیلم
async def reaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not await is_member(user_id, context):
        await query.edit_message_text("برای واکنش دادن باید عضو کانال باشید.")
        return

    emojis = {
        "react_1": "👍",
        "react_2": "❤️",
        "react_3": "🔥",
        "react_4": "🎉",
        "react_5": "😮",
    }
    emoji = emojis.get(query.data, "")
    # حذف دکمه‌ها پس از واکنش
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{query.from_user.first_name} به این پیام واکنش {emoji} داد."
    )


# حذف پیام‌های ارسالی کسانی که عضو کانال نیستند
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        try:
            await update.message.delete()
            warning_msg = await update.message.reply_text(
                "شما عضو کانال نیستید!\n"
                "لطفا ابتدا عضو کانال شوید."
            )
            # حذف پیام هشدار بعد 30 ثانیه
            await asyncio.sleep(30)
            await warning_msg.delete()
        except Exception as e:
            logger.error(f"Error deleting message or warning: {e}")


async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendlink", send_link))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^get_movie$"))
    application.add_handler(CallbackQueryHandler(reaction_handler, pattern=r"react_\d"))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), message_handler))

    await application.run_polling()


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    import asyncio
    asyncio.run(main())
