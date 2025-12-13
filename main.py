import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, Text

# ------------------ CONFIG ------------------
TOKEN = os.getenv("TOKEN")  # Telegram token
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")  # CryptoBot token
PRICE = 10

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ KEYBOARDS ------------------

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Купить аккаунты")],
        [KeyboardButton(text="ℹ️ О боте")]
    ],
    resize_keyboard=True
)

# Кнопка "Назад"
back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True
)

# Inline-кнопки для выбора количества аккаунтов
def amount_keyboard():
    kb = InlineKeyboardBuilder()
    for i in range(1, 11):
        kb.button(text=str(i), callback_data=f"amount:{i}")
    kb.adjust(5)
    return kb.as_markup()

# Inline-кнопка оплаты
def payment_keyboard(total):
    kb = InlineKeyboardBuilder()
    pay_url = f"https://t.me/CryptoBot?start=merchant-{CRYPTOBOT_TOKEN}-{total}"
    kb.button(text="💳 Оплатить через CryptoBot", url=pay_url)
    kb.button(text="⬅️ Назад", callback_data="back_buy")
    kb.adjust(1)
    return kb.as_markup()

# ------------------ HANDLERS ------------------

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в *Sale Payoneer*!\n\n"
        "Здесь вы можете приобрести Payoneer аккаунты по выгодной цене.",
        parse_mode="Markdown",
        reply_markup=main_menu
    )

# Главное меню
@dp.message(Text("⬅️ Назад в меню"))
async def back(message: types.Message):
    await start(message)

@dp.message(Text("🛒 Купить аккаунты"))
async def buy_accounts(message: types.Message):
    await message.answer(
        "Выберите количество аккаунтов (1–10):",
        reply_markup=back_menu
    )
    await message.answer(
        "Количество:",
        reply_markup=amount_keyboard()
    )

@dp.message(Text("ℹ️ О боте"))
async def about(message: types.Message):
    await message.answer(
        "Этот бот продаёт проверенные Payoneer аккаунты.\n"
        f"Цена: {PRICE}$ за аккаунт. Оплата через CryptoBot.",
        reply_markup=back_menu
    )

# Callback для выбора количества
@dp.callback_query(lambda c: c.data.startswith("amount:"))
async def choose_amount(callback: types.CallbackQuery):
    amount = int(callback.data.split(":")[1])
    total = amount * PRICE
    await callback.message.edit_text(
        f"Вы выбрали: *{amount} аккаунтов*\n"
        f"Цена за штуку: {PRICE}$\n"
        f"Итого к оплате: *{total}$*",
        parse_mode="Markdown",
        reply_markup=payment_keyboard(total)
    )
    await callback.answer()

# Callback для кнопки "Назад" в оплате
@dp.callback_query(Text("back_buy"))
async def back_to_amount(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите количество аккаунтов (1–10):",
        reply_markup=amount_keyboard()
    )
    await callback.answer()

# ------------------ RUN BOT ------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
