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

    GET_CARD = lambda m: ReplyKeyboardMarkup(resize_keyboard=True).add(
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

