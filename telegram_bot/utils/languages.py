from utils.database import User

database = User()


lang = {
    'en': {
        'send_welcome': lambda
            call: f'Hello {database.get_name(call)}, my name is Olivia 🪄\nI know how to guess, '
                  f'let\'s try? 👇 ',
        'author': 'Author\'s cards 🎴',
        'author_cards': 'Author\'s cards 🎴',
        'standard': 'Standard cards 🃏',
        'standard_cards': 'Standard cards 🃏',
        'switch': 'Switch language 🇺🇸🇷🇺',
        'fortune?': lambda m: f'tell fortunes? 🔮👁\nOlivia Energy: {database.get_energy(m)}/100',
        'fortune': 'Let\'s try!',
        'back': 'Back',
        'repeat': lambda m: f'Do you want to repeat?🔮\nOlivia Energy: {database.get_energy(m)}/100',
        'repeat_again': 'Again!',
        'no_energy': 'Sorry, but Olivia is tired, she needs to recover!',
        'question': 'What do you think about this? Have questions?\nReply to one post',
        'question2': 'Great question... I\'ll think about it and answer someday if I can find an answer',
        'session': 'The session ended, you did not answer the question for 10 minutes',
    },
    'ru': {
        'send_welcome': lambda
            call: f'Привет {database.get_name(call)}, меня зовут Оливия 🪄\nЯ умею гадать, '
                  f'давай попробуем? 👇 ',
        'author': 'Авторские карты 🎴',
        'author_cards': 'Авторские карты 🎴',
        'standard': 'Стандартные карты 🃏',
        'standard_cards': 'Стандартные карты 🃏',
        'switch': 'Сменить язык 🇺🇸🇷🇺',
        'fortune?': lambda m: f'Погадаем? 🔮👁\nЭнергия Оливии: {database.get_energy(m)}/100',
        'fortune': 'Давай попробуем!',
        'back': 'Назад',
        'repeat': lambda m: f'Хотите повторить?🔮\nЭнергия Оливии: {database.get_energy(m)}/100',
        'repeat_again': 'Еще раз!',
        'no_energy': 'Простите, но Оливия устала, ей нужно восстановится!',
        'question': 'Что думаете по этому поводу? Есть вопросы?\nДайте ответ одним сообщением',
        'question2': 'Отличный вопрос... Подумаю и отвечу когда-нибудь, если смогу найти ответ',
        'session': 'Сеанс завершен, вы не отвечали на вопрос в течении 10 минут',

    }
}
