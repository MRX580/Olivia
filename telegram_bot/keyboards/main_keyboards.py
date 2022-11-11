from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from utils.languages import lang
from utils.database import User

database = User()


class Kb:
    @staticmethod
    def start_button(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['standard'], callback_data='standard'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['author'], callback_data='authors cards'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['switch'], callback_data='switch language')
        )

    @staticmethod
    def fortune(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['fortune'], callback_data='fortune'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['back'], callback_data='fortune_back')
        )

    @staticmethod
    def fortune_repeat(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['repeat_again'], callback_data='fortune'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['back'], callback_data='fortune_back')
        )

    @staticmethod
    def only_back(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['back'], callback_data='fortune_back'),
        )

    SWITCH_LANGUAGE = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='English 🇺🇸', callback_data='switch english'),
        InlineKeyboardButton(text='Русский 🇷🇺', callback_data='switch russian'),
    )
