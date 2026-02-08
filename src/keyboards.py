from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_currency = InlineKeyboardButton(text="Курсы", callback_data="btn_cur")
button_commands = InlineKeyboardButton(text="Все команды", callback_data="btn_cmd")

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [button_currency],
        [button_commands]
    ])