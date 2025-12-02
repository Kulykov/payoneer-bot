import os
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PRICE_PER_ACCOUNT = 10  # 10$ за аккаунт

# ---------------- КНОПКИ ---------------------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="buy")],
    ])

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

def amount_menu():
    kb = []
    for i in range(1, 11):
        kb.append([InlineKeyboardButton(text=f"{i} аккаунтов — {i * PRICE_PER_ACCOUNT}$",
                                        callback_data=f"amount_{i}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ----------------- ПРИВЕТСТВИЕ ----------------------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я бот-магазин для покупки аккаунтов.\n\nВыберите действие:",
        reply_markup=main_menu()
    )

# ----------------- ВЫБОР КОЛИЧЕСТВА -----------------
@dp.callback_query(F.data == "buy")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите количество аккаунтов:",
        reply_markup=amount_menu()
    )

@dp.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu()
    )

# ----------------- ОПЛАТА ---------------------------
async def create_crypto_invoice(amount_usd: int):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    payload = {
        "amount": amount_usd,
        "currency_type": "usd",
        "asset": "USDT",
        "description": f"Покупка аккаунтов на сумму {amount_usd}$",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()

@dp.callback_query(F.data.startswith("amount_"))
async def choose_amount(callback: CallbackQuery):
    count = int(callback.data.split("_")[1])
    total_price = count * PRICE_PER_ACCOUNT

    invoice = await create_crypto_invoice(total_price)
    if not invoice or "result" not in invoice:
        await callback.message.answer("Ошибка при создании инвойса!")
        return

    pay_url = invoice["result"]["pay_url"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])
    await callback.message.edit_text(
        f"Вы выбрали: {count} аккаунтов.\n"
        f"Сумма к оплате: {total_price}$\n\n"
        f"Нажмите кнопку ниже для оплаты:",
        reply_markup=kb
    )

# ------------------ ЗАПУСК -------------------------
if __name__ == "__main__":
    dp.run_polling(bot)
