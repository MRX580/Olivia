from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from utils.languages import lang
from utils.database import User

database = User()


class Kb:

    HISTORY_FULL = lambda data: InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='♾', callback_data=data)
        )

    TEXT_FULL = lambda m: InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=lang[database.get_language(m)]['know_more'], callback_data='full_text')
        )

    HISTORY_BACK = lambda data: InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='⤴️', callback_data=data+'_back')
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

    GET_CARD = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['fortune'],
        lang[database.get_language(m)]['past_present_future']
    )

    FULL_TEXT = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['fortune_again'],
        lang[database.get_language(m)]['thx'],
    )

    FULL_TEXT_WITHOUT_THX = lambda m: ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(m)]['fortune_again']
    )

    MENU_3_CARDS = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        'Вытянуть три карты',
        'Другой расклад'
    )

    AFTER_END_SESSION = lambda m: ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(m)]['after_session']
    )

    PPF_MENU = lambda m, data: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['open_past'] if not data['past'] else '',
        lang[database.get_language(m)]['open_present']if not data['present'] else '',
        lang[database.get_language(m)]['open_future']if not data['future'] else ''
    )


