from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot.utils.languages import lang
from telegram_bot.utils.database import User

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

    FIRST_APRIL = lambda user_lang: InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text=lang[user_lang]['fool_card_button'], callback_data='start_fortune')
    )

    USDT_DONATE_BACK = lambda data: InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text=lang[database.get_language(data)]['usdt_donate_back'],
                             callback_data='usdt_donate_back')
    )

    DONATE = (lambda data: InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
              .add(
        InlineKeyboardButton(text="8 USDT", callback_data='8_USDT'),
        InlineKeyboardButton(text="11 USDT", callback_data='11_USDT'),
        InlineKeyboardButton(text="88 USDT", callback_data='88_USDT')
    )
              .add(
        InlineKeyboardButton(text=lang[database.get_language(data)]['share_link_with_olivia'], switch_inline_query="")
    )
              .add(
        InlineKeyboardButton(text=lang[database.get_language(data)]['back_to_fortune'], callback_data='back_to_fortune')
    )
              )

