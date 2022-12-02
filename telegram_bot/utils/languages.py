from utils.database import User, Fortune

database = User()
database_fortune = Fortune()


lang = {
    'en': {
        'send_welcome': lambda
            call: f'Hello {database.get_name(call)}, my name is Olivia 🪄\nI know how to guess, '
                  f'let\'s try? 👇 ',
        'start': f'Always glad to have a new guest. You are welcome here. How can I call you, guest?🦄',
        'clarify': 'Clarify a situation 🌟',
        'day_card': 'Сard of the day 🃏',
        'switch': 'Switch language 🇺🇸🇷🇺',
        'back': 'Back',
        'repeat_again': 'Again!',
        'no_energy': 'I need to rest, I\'ll tell fortunes for you a little later..',
        'question': 'What do you think about this? Have questions?\nReply to one post',
        'question2': 'Great question... I\'ll think about it and answer someday if I can find an answer',
        'session': 'The session ended, you did not answer the question for 10 minutes',
        'fortune_menu': 'Where can I guess this time? 🤔',
        'add_wisdom_text': 'Please teach me something new! \
        (what should I add or improve? I will take into account all useful comments and links) \
        Let\'s make magic together ✨',
        'answer_wisdom': 'Thank you for your wisdom!\nI will listen to you',
        'question_again': lambda m: f'What other question haunts you, {database.get_name(m)}?',
        'choose_language': 'Choose language 🧙‍♂️',
        'thanks': lambda m: f'I was glad to help, {database.get_name(m)}',
        'what_say': 'Let\'s see what the cards say?',
        'empty_history': 'Your history is empty',
        'get_card': 'Concentrate your mind on your question and draw a card...',
        'thx': 'Thanks',
        'know_more': 'Dive deeper',
        'fortune': 'Draw card',
        'fortune_again': 'Guess again',
    },
    'ru': {
        'send_welcome': lambda
            call: f'Привет {database.get_name(call)}, меня зовут Оливия 🪄\nЯ умею гадать, '
                  f'давай попробуем? 👇 ',
        'start': f'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, гость?🦄',
        'clarify': 'Прояснить ситуацию 🌟',
        'author_cards': 'Авторские карты 🎴',
        'day_card': 'Карта дня 🃏',
        'switch': 'Сменить язык 🇺🇸🇷🇺',
        'back': 'Назад',
        'repeat_again': 'Еще раз!',
        'no_energy': 'Мне надо отдохнуть, я погадаю для вас чуть позже..',
        'question': 'Что думаете по этому поводу? Есть вопросы?\nДайте ответ одним сообщением',
        'question2': 'Отличный вопрос... Подумаю и отвечу когда-нибудь, если смогу найти ответ',
        'session': 'Сеанс завершен, вы не отвечали на вопрос в течении 10 минут',
        'fortune_menu': 'Где же мне погадать в этот раз? 🤔',
        'add_wisdom_text': 'Пожалуйста, научи меня чему-то новому! \
(что мне добавить или улучшить? Учту все полезные комментарии и ссылки) \
Давай творить магию вместе ✨',
        'answer_wisdom': 'Спасибо за вашу мудрость!\nЯ прислушаюсь к вам',
        'question_again': lambda m: f'Какой ещё вопрос не даёт вам покоя, {database.get_name(m)}?',
        'question_start': lambda m: f'Какой вопрос не даёт вам покоя, {m.text}?',
        'choose_language': 'Выберите язык 🧙‍♂️',
        'thanks': lambda m: f'Рада была помочь, {database.get_name(m)}',
        'what_say': 'Давайте посмотрим, что скажут карты?',
        'empty_history': 'Ваша история пуста',
        'get_card': 'Сконцентрируйте сознание на своем вопросе и вытяните карту...',
        'thx': 'Спасибо',
        'know_more': 'Узнать больше',
        'fortune': 'Вытянуть карту',
        'fortune_again': 'Погадать ещё раз',

    }
}

all_lang = {
    'thx': ['Thanks', 'Спасибо'],
    'know_more': ['Dive deeper', 'Узнать больше'],
    'get_card': ['Draw card', 'Вытянуть карту'],
    'get_card_again': ['Guess again', 'Погадать ещё раз'],
}