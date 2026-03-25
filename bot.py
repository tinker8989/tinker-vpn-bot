import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

PAYMENT_CARD = os.getenv("PAYMENT_CARD")
PAYMENT_PHONE = os.getenv("PAYMENT_OZON_PHONE")

STANDARD_LINK = os.getenv("STANDARD_LINK")
PREMIUM_LINK = os.getenv("PREMIUM_LINK")
FAMILY_LINK = os.getenv("FAMILY_LINK")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(msg: Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="💳 Standard")],
            [types.KeyboardButton(text="⭐ Premium")],
            [types.KeyboardButton(text="👨‍👩‍👧‍👦 Family")],
        ],
        resize_keyboard=True,
    )
    await msg.answer("Tinker VPN 🚀\nВыбери подписку:", reply_markup=kb)


@dp.message(lambda m: "standard" in m.text.lower())
async def buy_standard(msg: Message):
    await msg.answer(f"Оплати 200₽\n\nКарта: {PAYMENT_CARD}\nOzon: {PAYMENT_PHONE}\n\nОтправь чек")


@dp.message(lambda m: "premium" in m.text.lower())
async def buy_premium(msg: Message):
    await msg.answer(f"Оплати 250₽\n\nКарта: {PAYMENT_CARD}\nOzon: {PAYMENT_PHONE}\n\nОтправь чек")


@dp.message(lambda m: "family" in m.text.lower())
async def buy_family(msg: Message):
    await msg.answer(f"Оплати 300₽\n\nКарта: {PAYMENT_CARD}\nOzon: {PAYMENT_PHONE}\n\nОтправь чек")


@dp.message(lambda m: m.photo)
async def check(msg: Message):
    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=f"Чек от @{msg.from_user.username}\nID: {msg.from_user.id}",
    )
    await msg.answer("Чек отправлен, жди подтверждения")


@dp.message(lambda m: m.text and m.text.startswith("/give"))
async def give(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, plan = msg.text.split()
        user_id = int(user_id)

        if plan == "standard":
            link = STANDARD_LINK
        elif plan == "premium":
            link = PREMIUM_LINK
        else:
            link = FAMILY_LINK

        await bot.send_message(user_id, f"✅ Оплата подтверждена\n\nТвоя подписка:\n{link}")
        await msg.answer("Выдано")
    except:
        await msg.answer("Ошибка")


async def main():
    await dp.start_polling(bot)


if name == "main":
    import asyncio
    asyncio.run(main())
