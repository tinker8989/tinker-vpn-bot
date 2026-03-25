import asyncio
import os
import sqlite3
import time
import logging
from typing import Optional, List, Tuple, Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
)

# Настройка логирования для отслеживания ошибок
logging.basicConfig(level=logging.INFO)

# =====================================================================
# ⚙️ КОНФИГУРАЦИЯ (Заполни свои данные)
# =====================================================================
BOT_TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ"  # Вставь сюда токен от BotFather
ADMIN_ID = 000000000           # Вставь свой ID (можно узнать у @userinfobot)
DB_PATH = "orders.sqlite"

# Ссылки проекта
TG_CHANNEL = "https://t.me/tinkervpn"
AGREEMENT_URL = "https://telegra.ph/Soglashenie-03-10-3"

# =====================================================================
# 📑 СОСТОЯНИЯ FSM
# =====================================================================
class AdminStates(StatesGroup):
    broadcast_wait = State()
    price_wait = State()
    keys_wait = State()

# =====================================================================
# 🗄 ФУНКЦИИ БАЗЫ ДАННЫХ
# =====================================================================
def db_init():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
            plan TEXT, status TEXT DEFAULT 'pending', created_at INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS vpn_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT, plan TEXT, key_value TEXT UNIQUE)""")
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.commit()

def db_upsert_user(user_id, username, first_name):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO users (user_id, username, first_name, joined_at) 
            VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET 
            username=excluded.username, first_name=excluded.first_name""",
            (user_id, username, first_name, int(time.time())))

# =====================================================================
# 🎹 КЛАВИАТУРЫ (КРАСИВОЕ ОФОРМЛЕНИЕ)
# =====================================================================
def kb_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💎 Купить подписку"), KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="📝 Инструкция"), KeyboardButton(text="🆘 Поддержка")]
    ], resize_keyboard=True)

def kb_choose_plan():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Standart — 150₽", callback_data="buy_standard")],
        [InlineKeyboardButton(text="⚡ Premium — 300₽", callback_data="buy_premium")],
        [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Family — 600₽", callback_data="buy_family")],
        [InlineKeyboardButton(text="🔴 ОТМЕНА", callback_data="cancel_action")] # Красный акцент
    ])

def kb_admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="➕ Добавить ключи", callback_data="adm_add_keys")],
        [InlineKeyboardButton(text="🚫 УДАЛИТЬ КЛЮЧИ", callback_data="adm_del_keys")],
        [InlineKeyboardButton(text="⚙️ Настройки цен", callback_data="adm_prices")]
    ])

# =====================================================================
# 🤖 ОБРАБОТЧИКИ (HANDLERS)
# =====================================================================
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: Message):
    db_upsert_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(
        f"<b>Привет, {message.from_user.first_name}!</b> 🚀\n\n"
        f"Добро пожаловать в <b>Tinker VPN</b>. Мы обеспечиваем максимальную скорость и конфиденциальность.",
        reply_markup=kb_main_menu()
    )

@dp.message(F.text == "💎 Купить подписку")
async def process_buy(message: Message):
    await message.answer("✨ <b>Выберите ваш тарифный план:</b>", reply_markup=kb_choose_plan())

@dp.callback_query(F.data == "cancel_action")
async def cancel_btn(callback: CallbackQuery):
    await callback.answer("Действие отменено")
    await callback.message.edit_text("Вы вернулись в главное меню. Используйте кнопки ниже 👇")

@dp.message(Command("admin"))
async def admin_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🏗 <b>Панель администратора</b>", reply_markup=kb_admin_panel())

# =====================================================================
# 🚀 ЗАПУСК
# =====================================================================
async def main():
    db_init()
    print("--- БОТ ЗАПУЩЕН ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
