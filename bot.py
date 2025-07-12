bot.py - نسخه کامل و بدون ارور ربات تلگرام

import os import logging import asyncio import nest_asyncio from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

فعال کردن پشتیبانی از اجرای همزمان در asyncio

nest_asyncio.apply()

تنظیمات لاگ

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO ) logger = logging.getLogger(name)

توکن ربات و اطلاعات مدیریتی

BOT_TOKEN = "7289610239:AAH8lsGfH1V--Jc_WnM9dxisAaAeW--Vdvc" ADMIN_ID = 5094400970 CHANNEL_USERNAME = "@cinema_zone_channel" SUPPORT_USERNAME = "@cinema_support_bot"  # ربات یا کانال پشتیبانی

دکمه‌های منو اصلی

def get_main_keyboard(): return InlineKeyboardMarkup([ [InlineKeyboardButton("🎬 فیلم جدید", callback_data="new_movie")], [InlineKeyboardButton("📩 ارتباط با پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")] ])

بررسی عضویت

async def is_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool: try: member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id) return member.status in ["member", "administrator", "creator"] except: return False

شروع

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user if not await is_member(user.id, context): keyboard = InlineKeyboardMarkup([ [InlineKeyboardButton("عضویت در کانال ✅", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")], [InlineKeyboardButton("🔄 بررسی عضویت", callback_data="check_join")] ]) await update.message.reply_text("برای استفاده از ربات ابتدا در کانال عضو شوید.", reply_markup=keyboard) return await update.message.reply_text(f"سلام {user.first_name}!\nبه ربات سینما خوش اومدی 🍿", reply_markup=get_main_keyboard())

بررسی دکمه عضویت

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user_id =
