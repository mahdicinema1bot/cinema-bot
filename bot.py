import asyncio import logging import os from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update from telegram.ext import ( Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes )

========================= تنظیمات =========================

BOT_TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc" ADMIN_ID = 7774213647 CHANNEL_ID = "@Cinemazone1" SUPPORT_ID = "@Cinemazone1support"

========================= لاگ‌گیری =========================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

========================= بررسی عضویت =========================

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE): try: member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id) return member.status in ("member", "creator", "administrator") except: return False

========================= استارت =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id if not await is_user_member(user_id, context): keyboard = [[InlineKeyboardButton("✅ عضویت در کانال", url=f"https://t.me/{CHANNEL_ID[1:]}")], [InlineKeyboardButton("🔄 بررسی عضویت", callback_data="check_membership")]] await update.message.reply_text("👋 خوش اومدی! برای استفاده از ربات ابتدا در کانال عضو شو:", reply_markup=InlineKeyboardMarkup(keyboard)) return

keyboard = [
    [InlineKeyboardButton("🎥 ارسال فیلم (فقط مدیریت)", callback_data="upload_film")],
    [InlineKeyboardButton("📞 ارتباط با پشتیبانی", callback_data="support")]
]
if user_id == ADMIN_ID:
    await update.message.reply_text("🎬 به پنل مدیریت خوش اومدی:", reply_markup=InlineKeyboardMarkup(keyboard))
else:
    await update.message.reply_text("✅ شما عضو کانال هستی. خوش آمدی!", reply_markup=InlineKeyboardMarkup(keyboard))

========================= چک عضویت =========================

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() user_id = query.from_user.id

if await is_user_member(user_id, context):
    await query.edit_message_text("✅ عضویت شما تایید شد. مجدداً /start را بزنید.")
else:
    await query.edit_message_text("❌ هنوز عضو نشدی! لطفاً عضو شو و دوباره امتحان کن.")

========================= ارتباط با پشتیبانی =========================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user_id = query.from_user.id if not await is_user_member(user_id, context): await query.answer() await query.edit_message_text("❌ ابتدا در کانال عضو شوید سپس مجدداً /start را بزنید.") return await query.answer() await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 پیام جدید از @{query.from_user.username or user_id}") await query.edit_message_text("📬 پیام خود را همین‌جا بفرستید. پشتیبان به زودی پاسخ می‌دهد.")

========================= هندل پیام‌های پشتیبانی =========================

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.from_user.id != ADMIN_ID: await context.bot.send_message(chat_id=ADMIN_ID, text=f"✉️ پیام از @{update.message.from_user.username}: {update.message.text}") await update.message.reply_text("✅ پیام شما به پشتیبانی ارسال شد.") else: await update.message.reply_text("📌 این پیام از طرف مدیریت است.")

========================= مدیریت: دریافت فیلم و ساخت لینک =========================

user_videos = {}

async def upload_film(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() if query.from_user.id != ADMIN_ID: await query.edit_message_text("❌ فقط مدیریت می‌تواند فیلم آپلود کند.") return await query.edit_message_text("📤 لطفاً فیلم را ارسال کنید.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.from_user.id != ADMIN_ID: return message = await update.message.reply_text("✅ لینک فیلم ساخته شد. به کاربران بده:") user_videos[update.message.message_id] = update.message await update.message.reply_text(f"🎬 برای دیدن فیلم، ابتدا عضو کانال شوید و سپس /start را بزنید.")

========================= اجرای اصلی =========================

async def main(): application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
application.add_handler(CallbackQueryHandler(support, pattern="support"))
application.add_handler(CallbackQueryHandler(upload_film, pattern="upload_film"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL, handle_document))

# اجرای ربات
await application.initialize()
await application.start()
await application.updater.start_polling()
await application.updater.idle()

if name == 'main': import nest_asyncio nest_asyncio.apply() asyncio.run(main())

