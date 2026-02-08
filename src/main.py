import asyncio; import logging; import requests; import re
from rates import CURRENCY_ALIASES, TARGET_CURRENCIES
from aiogram import Bot, Dispatcher, types, F
from config import TOKEN, API_URL, DEVELOPER
from rates_emoji import CURRENCY_EMOJI
from aiogram.filters import Command
from keyboards import keyboard


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("""
🤖 <b>Я помогу тебе с конвертацией валют</b>.

❔ <b>Как пользоваться</b>:
Просто напиши сумму и валюту из списка — например, "100 usd" или "50 eur". Для удобства больших сумм можно использовать сокращения: "1к usd".

💰 <b>Какие валюты работают</b>:
🇺🇸USD | 🇪🇺EUR | 🇨🇳CNY | 🇮🇳INR | 🇯🇵JPY | 🇦🇺AUD | 🇧🇬BGN | 🇧🇷BRL | 🇨🇦CAD | 🇨🇭CHF | 🇨🇿CZK | 🇩🇰DKK | 🇬🇧GBP | 🇭🇰HKD | 🇭🇺HUF | 🇮🇩IDR | 🇮🇱ILS | 🇮🇸ISK | 🇰🇷KRW | 🇲🇽MXN | 🇲🇾MYR | 🇳🇴NOK | 🇳🇿NZD | 🇵🇭PHP | 🇵🇱PLN | 🇷🇴RON | 🇸🇪SEK | 🇸🇬SGD | 🇹🇭THB | 🇹🇷TRY | 🇿🇦ZAR

<b>Давай попробуем? Пиши любую сумму!</b>""", parse_mode="HTML", reply_markup=keyboard)


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


async def build_currency_text(message_text: str):
    amount, base_currency = parse_message(message_text)
    if not amount or not base_currency:
        return None, "Напиши сумму и валюту из списка"
    try:
        rates = get_rates(base_currency)
    except:
        return None, "Не удалось получить курсы валют."
    text = f"{CURRENCY_EMOJI.get(base_currency, '')} <b>{base_currency}</b> <code>{amount}</code>:\n\n"
    for target in TARGET_CURRENCIES:
        if target == base_currency or target not in rates:
            continue
        converted = amount * rates[target]
        text += f"{CURRENCY_EMOJI.get(target, '')} <b>{target}</b>: <code>{converted:.2f}</code>\n"
    return text, None


@dp.message(Command("rates"))
async def rates_cmd(message: types.Message):
    text, error = await build_currency_text("100 usd")
    await message.answer(text + DEVELOPER, parse_mode="HTML", disable_web_page_preview=True)


@dp.callback_query(F.data.startswith("btn_cur"))
async def btn_cur(callback: types.CallbackQuery):
    text, error = await build_currency_text(callback.message.text)
    if error:
        await callback.message.answer(error)
        await callback.answer()
        return
    await callback.message.answer(text + DEVELOPER, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())