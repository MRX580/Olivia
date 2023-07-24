from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from utils.languages import lang
from utils.database import User

database = User()


class Kb:

    HISTORY_FULL = lambda data: InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='...', callback_data=data)
        )

    TEXT_FULL = lambda data: InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=lang[database.get_language(data)]['know_more'], callback_data='full_text')
    )\
        # .add( InlineKeyboardButton(text=lang[database.get_language(data)]['like'], callback_data='like reaction'),
        # InlineKeyboardButton(text=lang[database.get_language(data)]['dislike'], callback_data='dislike reaction'))

    HISTORY_BACK = lambda data: InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='⤴️', callback_data=data+'_back')
        )

    ADD_REACTION = lambda data: InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text=lang[database.get_language(data)]['like'], callback_data='like reaction'),
        InlineKeyboardButton(text=lang[database.get_language(data)]['dislike'], callback_data='dislike reaction'),
    )

    BACK_TO_FORTUNE = lambda data: InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text=lang[database.get_language(data)]['back_to_fortune'], callback_data='back_to_fortune')
    )

    LANGUAGES = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='🇺🇸', callback_data='switch english'),
        InlineKeyboardButton(text='🇷🇺', callback_data='switch russian'),
    )

    LANGUAGES_COMMAND = lambda data: InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='🇺🇸', callback_data='switch english_command'),
        InlineKeyboardButton(text='🇷🇺', callback_data='switch russian_command'),
    ).add(InlineKeyboardButton(text=lang[database.get_language(data)]['back_to_fortune'], callback_data='back_to_fortune'))

    PAYMENT = InlineKeyboardMarkup(resize_keyboard=True, row_width=2).add(
        InlineKeyboardButton('Bitcoin(BTC)', callback_data='bitcoin_address'),
        InlineKeyboardButton('Ethereum(ETH)', callback_data='ethereum_address'),
        InlineKeyboardButton('Ripple(XRP)', callback_data='ripple_address')
    )