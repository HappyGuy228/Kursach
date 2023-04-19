from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_category1 = InlineKeyboardButton('Категория 1', callback_data='Категория 1', icon_color='7322096')
button_category2 = InlineKeyboardButton('Категория 2', callback_data='Категория 2')
button_category3 = InlineKeyboardButton('Категория 3', callback_data='Категория 3')

keyboard = InlineKeyboardMarkup(row_width=1)
keyboard.add(button_category1, button_category2, button_category3)

