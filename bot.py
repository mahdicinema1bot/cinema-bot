import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)

# اطلاعات شما
BOT_TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc"
ADMIN_ID = 7774213647
CHANNEL_USERNAME = "cinema_zone_channel"  # بدون @
SUPPORT_USERNAME = "Cinemazone1support"  # بدون @

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# چک عضویت در کانال
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False


# شروع ربات و پیام خوش آمد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_membership(user_id, context):
        await send_main_menu(update)
    else:
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام! برای استفاده از ربات ابتدا باید عضو کانال شوید.",
            reply_markup=reply_markup
        )


# منوی اصلی بعد عضویت
async def send_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("ارتباط با پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "خوش آمدید! برای درخواست فیلم یا سریال با پشتیبانی در ارتباط باشید.",
        reply_markup=reply_markup
    )


# فقط مدیر اجازه داره لینک فیلم بفرسته
async def send_film_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("شما اجازه ارسال لینک فیلم را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("لطفا لینک فیلم را بعد از دستور /sendlink وارد کنید.")
        return

    link = context.args[0]
    text = f"فیلم جدید آماده دانلود است:\n{link}"

    keyboard = [
        [InlineKeyboardButton("👍", callback_data="react_1"),
         InlineKeyboardButton("❤️", callback_data="react_2"),
         InlineKeyboardButton("🔥", callback_data="react_3"),
         InlineKeyboardButton("🎉", callback_data="react_4"),
         InlineKeyboardButton("😮", callback_data="react_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


# هندل کردن ری‌اکشن‌ها
async def react_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not await check_membership(user_id, context):
        await query.edit_message_text("برای واکنش دادن باید عضو کانال باشید.")
        return

    emoji_map = {
        "react_1": "👍",
        "react_2": "❤️",
        "react_3": "🔥",
        "react_4": "🎉",
        "react_5": "😮",
    }
    reaction = emoji_map.get(query.data, "")
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{query.from_user.first_name} به این پیام واکنش {reaction} داد."
    )


# هندل پیام‌های ناشناس یا بدون عضویت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_membership(user_id, context):
        await update.message.delete()
        await update.message.reply_text(
            "شما عضو کانال نیستید! ابتدا باید عضو شوید تا بتوانید از ربات استفاده کنید."
        )
        return


async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendlink", send_film_link))
    application.add_handler(CallbackQueryHandler(react_callback))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))

    await application.run_polling()


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
