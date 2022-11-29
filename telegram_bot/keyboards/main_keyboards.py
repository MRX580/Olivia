from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from utils.languages import lang
from utils.database import User

database = User()


class Kb:
    @staticmethod
    def start_button(message: Message or CallbackQuery):
        keyboard = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['day_card'], callback_data='fortune-1d'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['clarify'], callback_data='clarify'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['relationship'], callback_data='relationship'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['look_future'], callback_data='look_future'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['add_wisdom'], callback_data='add_wisdom'),
        )
        keyboard.row(
            InlineKeyboardButton(text=lang[database.get_language(message)]['switch'], callback_data='switch language'))
        return keyboard

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
    def fortune_menu(message: Message or CallbackQuery):
        keyboard = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['1-d'], callback_data='fortune-1d'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['7-d'], callback_data='fortune-7d'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['30-d'], callback_data='fortune-30d'),
            InlineKeyboardButton(text=lang[database.get_language(message)]['common'], callback_data='fortune'),
        )
        keyboard.row(InlineKeyboardButton(text=lang[database.get_language(message)]['back'], callback_data='fortune_back'))
        return keyboard

    @staticmethod
    def only_back(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['back'], callback_data='fortune_back'),
        )

    @staticmethod
    def history_full(data):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='♾', callback_data=data)
        )

    @staticmethod
    def history_back(data):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='⤴️', callback_data=data+'_back')
        )

    @staticmethod
    def get_card():
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='Вытянуть карту', callback_data='fortune-1d')
        )

    FULL_TEXT = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Узнать больше', callback_data='full_text'),
        InlineKeyboardButton(text='Погадать ещё раз', callback_data='fortune_again'),
        InlineKeyboardButton(text='Спасибо', callback_data='thx'),
    )

    FULL_TEXT_WITHOUT_THX = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Узнать больше', callback_data='full_text'),
        InlineKeyboardButton(text='Погадать ещё раз', callback_data='fortune_again'),
    )

    BACK_TEXT_WITHOUT_THX = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Погадать ещё раз', callback_data='fortune_again'),
    )

    BACK_TEXT = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Погадать ещё раз', callback_data='fortune_again'),
        InlineKeyboardButton(text='Спасибо', callback_data='thx'),
    )

    SWITCH_LANGUAGE = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='English 🇺🇸', callback_data='switch english'),
        InlineKeyboardButton(text='Русский 🇷🇺', callback_data='switch russian'),
    )
