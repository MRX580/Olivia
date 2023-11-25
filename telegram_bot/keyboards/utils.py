from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


h_m_keyboard = lambda h=12, m=0: InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text='+', callback_data='plus_h'),
    InlineKeyboardButton(text='+', callback_data='plus_m'),
    InlineKeyboardButton(text=f'{h}h', callback_data='12h'),
    InlineKeyboardButton(text=f'{m}m', callback_data='00m'),
    InlineKeyboardButton(text='-', callback_data='minus_h'),
    InlineKeyboardButton(text='-', callback_data='minus_m'),
    InlineKeyboardButton(text='select', callback_data='select_h_m'),
)