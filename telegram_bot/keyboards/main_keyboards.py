from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ReplyKeyboardMarkup
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
    def text_full(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['know_more'], callback_data='full_text')
        )

    @staticmethod
    def history_back(data):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='⤴️', callback_data=data+'_back')
        )

    @staticmethod
    def get_card(message: Message or CallbackQuery):
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(message)]['fortune'], callback_data='fortune-1d')
        )

    LANGUAGES = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='🇺🇸', callback_data='switch english'),
        InlineKeyboardButton(text='🇷🇺', callback_data='switch russian'),
    )


    LANGUAGES_COMMAND = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='🇺🇸', callback_data='switch english_command'),
        InlineKeyboardButton(text='🇷🇺', callback_data='switch russian_command'),
    )

class KbReply:
    @staticmethod
    def GET_CARD(message: Message or CallbackQuery):
        return ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(message)]['fortune']
    )

    @staticmethod
    def FULL_TEXT(message: Message or CallbackQuery):
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(message)]['fortune_again'],
        lang[database.get_language(message)]['thx'],
    )

    @staticmethod
    def FULL_TEXT_WITHOUT_THX(message: Message or CallbackQuery):
        return ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(message)]['fortune_again']
    )

