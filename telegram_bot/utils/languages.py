from utils.database import User

database = User()


lang = {
    'en': {
        'send_welcome': lambda
            call: f'Hello {call.from_user.first_name}, my name is Olivia 🪄\nI know how to guess, '
                  f'let\'s try? 👇 ',
        'author': 'Author\'s cards 🎴',
        'author_cards': 'Author\'s cards 🎴',
        'standard': 'standard cards 🃏',
        'standard_cards': 'standard cards 🃏',
        'switch': 'switch language 🇺🇸🇷🇺',
        'fortune?': lambda m: f'tell fortunes? 🔮👁\nOlivia Energy: {database.get_energy(m)}/100',
        'fortune': 'Let\'s try!',
        'back': 'back',
        'repeat': lambda m: f'Do you want to repeat?🔮\nOlivia Energy: {database.get_energy(m)}/100',
        'repeat_again': 'Again!',
        'no_energy': 'Sorry, but Olivia is tired, she needs to recover!',
    },
    'ru': {
        'send_welcome': lambda
            call: f'Привет {call.from_user.first_name}, меня зовут Оливия 🪄\nЯ умею гадать, '
                  f'давай попробуем? 👇 ',
        'author': 'Авторские карты 🎴',
        'author_cards': 'Авторские карты 🎴',
        'standard': 'Стандартные карты 🃏',
        'standard_cards': 'Стандартные карты 🃏',
        'switch': 'сменить язык 🇺🇸🇷🇺',
        'fortune?': lambda m: f'Погадаем? 🔮👁\nЭнергия Оливии: {database.get_energy(m)}/100',
        'fortune': 'Давай попробуем!',
        'back': 'Назад',
        'repeat': lambda m: f'Хотите повторить?🔮\nЭнергия Оливии: {database.get_energy(m)}/100',
        'repeat_again': 'Еще раз!',
        'no_energy': 'Простите, но Оливия устала, ей нужно восстановится!',

    }
}


