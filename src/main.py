import asyncio; import logging; import requests; import re
from rates import CURRENCY_ALIASES, TARGET_CURRENCIES
from aiogram import Bot, Dispatcher, types
from rates_emoji import CURRENCY_EMOJI
from aiogram.filters import Command
from config import TOKEN, API_URL
from keyboards import keyboard

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


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
async def convert_currency(message: types.Message):
    amount, base_currency = parse_message(message.text)
    if not amount or not base_currency:
        return
    try:
        rates = get_rates(base_currency)
    except:
        await message.answer("Не удалось получить курсы валют.")
        return
    text = f"{CURRENCY_EMOJI.get(base_currency, '')} <b>{base_currency}</b> <code>{amount}</code>:\n\n"
    for target in TARGET_CURRENCIES:
        if target == base_currency or target not in rates:
            continue
        converted = amount * rates[target]
        text += f"{CURRENCY_EMOJI.get(target, '')} <b>{target}</b>: <code>{converted:.2f}</code>\n"
    await message.answer(text, parse_mode="HTML")


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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())