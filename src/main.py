import asyncio; import logging; import requests; import re

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TOKEN, API_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

CURRENCY_ALIASES = {
    "доллар": "USD",
    "долларов": "USD",
    "бакс": "USD",
    "баксов": "USD",

    "евро": "EUR",

    "руб": "RUB",
    "рубль": "RUB",
    "рублей": "RUB",

    "тенге": "KZT",
    "тг": "KZT",
}


TARGET_CURRENCIES = ["USD", "EUR", "RUB", "KZT"]


button_currency = InlineKeyboardButton(text="Курсы", callback_data="btn_cur")
button_commands = InlineKeyboardButton(text="Все команды", callback_data="btn_cmd")

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [button_currency],
        [button_commands]
    ])

def get_rates(base_currency: str) -> dict:
    response = requests.get(API_URL, params={"from": base_currency}, timeout=10)
    response.raise_for_status()
    return response.json()["rates"]


def parse_message(text: str):
    text = text.lower()

    amount_match = re.search(r"\d+(\.\d+)?", text)
    if not amount_match:
        return None, None

    amount = float(amount_match.group())

    for word, code in CURRENCY_ALIASES.items():
        if word in text:
            return amount, code

    return None, None


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("""
🤖 <b>Я помогу тебе с конвертацией валют</b>.

❔ <b>Как пользоваться</b>:
Напиши мне сумму и валюту — например, "100 USD" или можешь использовать символы типа "50€" или "1000₽". Если лень писать много нулей, пиши сокращённо: "1к рублей".

💰 <b>Какие валюты работают</b>:
- <b>Фиат</b>: 🇺🇸USD | 🇪🇺EUR | 🇷🇺RUB | 🇺🇦UAH | 🇧🇾BYN | 🇰🇿KZT | 🇨🇳CNY | 🇮🇳INR | 🇺🇿UZS

- <b>Крипта</b>: 🔱BTC | ♦ETH | 💎TON | 🕵XMR | 🫗NOT | 🐶DOGS

- <b>Другие</b>: 🎲ROBUX

<b>Давай попробуем? Пиши любую сумму!</b>""", parse_mode="HTML", reply_markup=keyboard)


@dp.message()
async def convert_handler(message: types.Message):
    amount, base_currency = parse_message(message.text)

    if not amount or not base_currency:
        await message.answer("Не понял 🤷‍♂️\nПример: 10 долларов")
        return

    try:
        rates = get_rates(base_currency)

        lines = [f"{amount} {base_currency} ≈"]

        for cur in TARGET_CURRENCIES:
            if cur == base_currency:
                continue
            if cur in rates:
                value = round(amount * rates[cur], 2)
                lines.append(f"{value} {cur}")

        await message.answer("\n".join(lines))

    except Exception:
        await message.answer("Ошибка получения курсов 😕")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())