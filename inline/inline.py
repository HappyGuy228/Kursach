from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_category1 = InlineKeyboardButton('Сапоги', callback_data='Категория 1')
button_category2 = InlineKeyboardButton('Ботинки', callback_data='Категория 2')
button_category3 = InlineKeyboardButton('Туфли', callback_data='Категория 3')

keyboard = InlineKeyboardMarkup(row_width=1)
keyboard.add(button_category1, button_category2, button_category3)

