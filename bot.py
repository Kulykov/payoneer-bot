import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# --------------------------------------------------
#  CONFIG (ЗДЕСЬ ТОЛЬКО ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ!)
# --------------------------------------------------
# Перед запуском добавь в Render:
# TOKEN=твой_телеграм_токен
# CRYPTOBOT_TOKEN=твой_криптобот_токен
# PRICE=10
# --------------------------------------------------

TOKEN = os.getenv("TOKEN")
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
PRICE = 10

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --------------------------------------------------
#   КНОПКИ
# --------------------------------------------------

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("🛒 Купить аккаунты"))
main_menu.add(KeyboardButton("ℹ️ О боте"))

back_menu = ReplyKeyboardMarkup(resize_keyboard=True)
back_menu.add(KeyboardButton("⬅️ Назад в меню"))

# Инлайн-кнопки выбора количества

def amount_keyboard():
    kb = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 11):
        buttons.append(InlineKeyboardButton(text=str(i), callback_data=f"amount_{i}"))
    kb.add(*buttons)
    return kb

# --------------------------------------------------
#   COMMANDS
# --------------------------------------------------

@dp.message_handler(commands=["start", "menu"])
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в *Sale Payoneer*!\n\n"
        "Здесь вы можете приобрести Payoneer аккаунты по выгодной цене.",
        parse_mode="Markdown",
        reply_markup=main_menu
    )

# --------------------------------------------------
#   ОБРАБОТКА ТЕКСТОВЫХ КНОПОК
# --------------------------------------------------

@dp.message_handler(lambda m: m.text == "🛒 Купить аккаунты")
async def buy_accounts(message: types.Message):
    await message.answer(
        "Выберите количество аккаунтов (1–10):",
        reply_markup=back_menu,
        reply_markup_inline=amount_keyboard()  # Ошибка: нельзя два reply_markup
    )

# Исправим: выводим одну клаву, затем инлайн

@dp.message_handler(lambda m: m.text == "🛒 Купить аккаунты")
async def buy_accounts_fixed(message: types.Message):
    await message.answer(
        "Выберите количество аккаунтов (1–10):",
        reply_markup=back_menu
    )
    await message.answer(
        "Количество:",
        reply_markup=amount_keyboard()
    )


@dp.message_handler(lambda m: m.text == "ℹ️ О боте")
async def about(message: types.Message):
    await message.answer(
        "Этот бот продаёт проверенные Payoneer аккаунты.\n"
        "Цена: 10$ за аккаунт. Оплата через CryptoBot.",
        reply_markup=back_menu
    )

@dp.message_handler(lambda m: m.text == "⬅️ Назад в меню")
async def back(message: types.Message):
    await start(message)

# --------------------------------------------------
#   INLINE CALLBACKS
# --------------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith("amount_"))
async def choose_amount(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    total = amount * PRICE

    pay_url = f"https://t.me/CryptoBot?start=merchant-{CRYPTOBOT_TOKEN}-{total}"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💳 Оплатить через CryptoBot", url=pay_url))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_buy"))

    await callback.message.edit_text(
        f"Вы выбрали: *{amount} аккаунтов*\n"
        f"Цена за штуку: {PRICE}$\n"
        f"Итого к оплате: *{total}$*",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "back_buy")
async def back_to_amount(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите количество аккаунтов (1–10):",
        reply_markup=amount_keyboard()
    )
    await callback.answer()

# --------------------------------------------------
#   START BOT
# --------------------------------------------------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

