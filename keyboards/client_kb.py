from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('📦Каталог')
b2 = KeyboardButton('⚙️Настройки')
b3 = KeyboardButton('ℹ️Помощь')
b4 = KeyboardButton('🛒Корзина')
b5 = KeyboardButton('📝История заказов')
b6 = KeyboardButton('💬Отзывы')

kb_client_menu = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client_menu.row(b1, b2).row(b4, b5).row(b3, b6)

b12 = KeyboardButton('Регистрация')
b22 = KeyboardButton('Данные')
b32 = KeyboardButton('Удалить')
b42 = KeyboardButton('Назад')

kb_client_settings = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client_settings.row(b12, b22).add(b32).add(b42)

b123 = KeyboardButton('Посмотреть отзывы')
b124 = KeyboardButton('Написать отзыв')

kb_client_review = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client_review.row(b123, b124).add(b42)
