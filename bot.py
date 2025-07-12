import logging import os import asyncio from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

برای لاگ‌گیری

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

اطلاعات ربات

TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc" ADMIN_ID = 7774213647  # آی‌دی عددی مدیر CHANNEL_USERNAME = "@cinema_zone_channel" SUPPORT_USERNAME = "@Cinemazone1support"

پیام خوش‌آمد و چک عضویت

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user chat_id = update.effective_chat.id

# چک عضویت
member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
if member.status not in ("member", "administrator", "creator"):
    keyboard = [[InlineKeyboardButton("عضویت در کانال 🎬", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
    await update.message.reply_text(
        "🔒 برای استفاده از ربات، ابتدا در کانال عضو شوید سپس دوباره /start را بزنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return

keyboard = [
    [InlineKeyboardButton("🎥 ارسال فیلم (مدیر)", callback_data="upload")],
    [InlineKeyboardButton("🆘 ارتباط با پشتیبانی", callback_data="support")]
]
if str(user.id) == str(ADMIN_ID):
    await update.message.reply_text(f"🎬 خوش آمدی مدیر عزیز!", reply_markup=InlineKeyboardMarkup(keyboard))
else:
    await update.message.reply_text(f"🎬 خوش آمدی به ربات سینمایی!", reply_markup=InlineKeyboardMarkup(keyboard))

هندل دکمه‌ها

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user await query.answer()

# چک عضویت
member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
if member.status not in ("member", "administrator", "creator"):
    keyboard = [[InlineKeyboardButton("عضویت در کانال 🎬", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
    await query.message.reply_text(
        "❗️برای ادامه، ابتدا عضو کانال شوید و مجدد /start را بزنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return

if query.data == "support":
    await context.bot.send_message(ADMIN_ID, f"📩 پیام جدید از کاربر @{user.username or user.id}.")
    await query.message.reply_text("✅ پیام شما به پشتیبانی ارسال شد.")

elif query.data == "upload":
    if str(user.id) == str(ADMIN_ID):
        await query.message.reply_text("🎬 فایل یا ویدیوی خود را ارسال کنید.")
    else:
        await query.message.reply_text("⛔️ فقط مدیر به این بخش دسترسی دارد.")

ذخیره فایل و ساخت لینک اشتراک

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user if str(user.id) != str(ADMIN_ID): return file = update.message.document or update.message.video if not file: return file_id = file.file_id # ساخت لینک اختصاصی دریافت فایل link = f"https://t.me/{context.bot.username}?start={file_id}" await update.message.reply_text(f"✅ لینک اختصاصی: {link}") context.bot_data[file_id] = file_id

ارسال فایل برای کسانی که لینک را دارند

async def send_file_by_link

