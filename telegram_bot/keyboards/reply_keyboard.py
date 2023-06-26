from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from utils.languages import lang
from utils.database import User

database = User()

class KbReply:

    GET_CARD = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['fortune_choice'],
        lang[database.get_language(m)]['past_present_future'],
        lang[database.get_language(m)]['aks_chatgpt_choice']
    )

    FULL_TEXT = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['fortune_again_choice'],
        lang[database.get_language(m)]['thx'],
    )

    FULL_TEXT_WITHOUT_THX = lambda m: ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(m)]['fortune_again_choice']
    )

    MAIN_MENU = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
        lang[database.get_language(m)]['divination_choice'],
        # lang[database.get_language(m)]['human_design']
    )

    MENU_3_CARDS = lambda m: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['get_3_cards_choice'],
        lang[database.get_language(m)]['another_alignment_choice']
    )

    AFTER_END_SESSION = lambda m: ReplyKeyboardMarkup(resize_keyboard=True).add(
        lang[database.get_language(m)]['after_session_choice']
    )

    PPF_MENU = lambda m, data: ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        lang[database.get_language(m)]['open_past'] if not data['past'] else '',
        lang[database.get_language(m)]['open_present']if not data['present'] else '',
        lang[database.get_language(m)]['open_future']if not data['future'] else ''
    )


