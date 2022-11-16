from utils.database import User, Fortune

database = User()
database_fortune = Fortune()


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
        'fortune?': lambda m: f'tell fortunes? 🔮👁\nOlivia Energy: {database.get_energy(m)}/100'
        if not database_fortune.is_first_try(m) else f'Nice to see you again, {database.get_name(m)} 😁'
                                                     f'\nOlivia Energy: {database.get_energy(m)}/100',
        'fortune': 'Let\'s try!',
        'back': 'Back',
        'repeat': lambda m: f'Do you want to repeat?🔮\nOlivia Energy: {database.get_energy(m)}/100',
        'repeat_again': 'Again!',
        'no_energy': 'Sorry, but Olivia is tired, she needs to recover!',
        'question': 'What do you think about this? Have questions?\nReply to one post',
        'question2': 'Great question... I\'ll think about it and answer someday if I can find an answer',
        'session': 'The session ended, you did not answer the question for 10 minutes',
        'fortune_menu': 'Where can I guess this time? 🤔',
        '1-d': 'Once a day',
        '7-d': 'Once a week',
        '30-d': 'Once a month',
        '1-d_fail': 'You already guessed today',
        '7-d_fail': 'You already guessed this week',
        '30-d_fail': 'You already guessed this month',
        'common': 'Ordinary divination(-50 energy)',
        'add_wisdom': 'Add wisdom 🌈',
        'add_wisdom_text': 'Please teach me something new! \
        (what should I add or improve? I will take into account all useful comments and links) \
        Let\'s make magic together ✨',
        'answer_wisdom': 'Thank you for your wisdom!\nI will listen to you',
        'history': 'History of divination',
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
        'fortune?': lambda m: f'Погадаем? 🔮👁\nЭнергия Оливии: {database.get_energy(m)}/100'
        if not database_fortune.is_first_try(m) else f'Приятно снова видеть тебя, {database.get_name(m)} 😁\n\n'
                                                     f'Энергия Оливии: {database.get_energy(m)}/100',
        'fortune': 'Давай попробуем!',
        'back': 'Назад',
        'repeat': lambda m: f'Хотите повторить?🔮\nЭнергия Оливии: {database.get_energy(m)}/100',
        'repeat_again': 'Еще раз!',
        'no_energy': 'Простите, но Оливия устала, ей нужно восстановится!',
        'question': 'Что думаете по этому поводу? Есть вопросы?\nДайте ответ одним сообщением',
        'question2': 'Отличный вопрос... Подумаю и отвечу когда-нибудь, если смогу найти ответ',
        'session': 'Сеанс завершен, вы не отвечали на вопрос в течении 10 минут',
        'fortune_menu': 'Где же мне погадать в этот раз? 🤔',
        '1-d': 'Раз в день',
        '7-d': 'Раз в неделю',
        '30-d': 'Раз в месяц',
        '1-d_fail': 'Вы уже гадали сегодня',
        '7-d_fail': 'Вы уже гадали на этой неделе',
        '30-d_fail': 'Вы уже гадали в этом месяце',
        'common': 'Обычное гадание(-50 энергии)',
        'add_wisdom': 'Добавить мудрости 🌈',
        'add_wisdom_text': 'Пожалуйста, научи меня чему-то новому! \
(что мне добавить или улучшить? Учту все полезные комментарии и ссылки) \
Давай творить магию вместе ✨',
        'answer_wisdom': 'Спасибо за вашу мудрость!\nЯ прислушаюсь к вам',
        'history': 'История гаданий',

    }
}
