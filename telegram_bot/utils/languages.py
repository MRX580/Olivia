from random import choice
from utils.database import User, Fortune

database = User()
database_fortune = Fortune()


lang = {
    'en': {
        'send_welcome': lambda
            call: f'Hello {database.get_name(call)}, my name is Olivia 🪄\nLet\'s open up your unconscious..',
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
        'question_again': lambda m: choice([f'What else is present in your mind, {database.get_name(m)}?',
                                            f'We can search for another answer.\nJust ask your question',
                                            'What else is needed to be clear?\nAsk me...']),
        'question_start': lambda m: f'What question is bothering you, {database.get_name(m)}?',
        'choose_language': 'Choose language 🧙‍♂️',
        'thanks': lambda m: f'I was glad to help, {database.get_name(m)}',
        'what_say': choice(['Let\'s hear the wisdom from within...\nHere is your card ✨',
                            'To reveal the truth we just need the key. Here is yours:',
                            '*eyes closed*\nCards, would you give us the answer?',
                            'Well-well-well... What do we have here?']),
        'empty_history': 'Your history is empty',
        'get_card': 'Concentrate your mind on your question and draw a card...',
        'thx': 'Thanks',
        'know_more': choice(['Dive deeper', 'Show me more', 'Learn more']),
        'fortune': choice(['Draw one card', 'Pull one card', 'Reveal one card']),
        'past_present_future': choice(['"Past present future"']),
        'fortune_again': choice(['May I ask another question?', 'Olivia, can you do one ore reading?',
                                 'I\'d love to clarify one more thing']),
        'end_session': lambda m: choice([f'Happy to serve, {database.get_name(m)}. I\'ll be waiting for you next visit',
                                         f'I\'ll keep everything in my memory for you, {database.get_name(m)}. Welcome '
                                         f'back anytime you feel like asking another question...', 'Thank you for '
                                         f'sharing your deepest questions, {database.get_name(m)}. Always here for you'
                                                                                                   f'']),
        'after_session': choice(['knock-knock', 'Olivia, I need you again', 'ding dong']),
        'start_session': lambda m: choice([f'What\'s the question that is bothering you today, {database.get_name(m)}?',
                                 'Happy to see you again, my friend. What question led you here?',
                                 f'Welcome back, {database.get_name(m)}. I knew you\'ll come. Ask your question',
                                f'I\'ve been waiting for you, {database.get_name(m)}. Feel free to ask your question']),
        'get_3_cards': 'Lets see those 3 cards',
        'another_alignment': 'Another alignment',
        'another_alignment_text': 'Hmm.. Let\'s take another look.',
        'start_3_cards': 'This spread will bring more clarity by overlooking the timeline of your issue. Let\'s see what is already done, what\'s present now and what direction are we going towards..',
        'open_past': 'See the Past',
        'past': '*Map of the past*\nWhat past attitudes, feelings or beliefs influenced the situation?',
        'open_present': 'Reveal what\'s Present',
        'present': '*Map of the present*\nWhat is the current energy around your question? What forces are having their influence?',
        'open_future': 'Show me the Future',
        'future': '*Map of the future*\nWhat\'s the potential outcome? What to expect and be aware of?',
        'open_cards': 'Let\'s see... Shall we start from the Past one?',
        'divination': 'Divination',
        'divination_text': 'Well, I\'ve got cards for every situation',
        'human_design': 'Human design',
    },




    'ru': {
        'send_welcome': lambda
            call: f'Привет {database.get_name(call)}, меня зовут Оливия 🪄\nДавай раскроем твое бессознательное..',
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
        'question_again': lambda m: choice([f'Что ещё вас волнует, {database.get_name(m)}?',
                                            f'Итак, каким будет Ваш следующий вопрос?',
                                            'Чем ещё заняты Ваши мысли?\nЗадайте вопрос']),
        'question_start': lambda m: f'Какой вопрос не даёт вам покоя, {database.get_name(m)}?',
        'choose_language': 'Выберите язык 🧙‍♂️',
        'thanks': lambda m: f'Рада была помочь, {database.get_name(m)}',
        'what_say': choice(['Давайте посмотрим, что скажут карты?', 'Иногда, чтобы открыть истину, нужен верный ключ. Вот '
                     'Ваша ключ-карта', '*прикрывает глаза*\nКарты, дайте нам ответ...', 'Так-так-так... Поглядим?']),
        'empty_history': 'Ваша история пуста',
        'get_card': 'Сконцентрируйте сознание на своем вопросе и вытяните карту...',
        'thx': 'Спасибо',
        'know_more': choice(['Узнать больше', 'Хочу узнать больше', 'Расскажи ещё']),
        'fortune': choice(['Вытянуть одну карту', 'Посмотреть одну карту']),
        'past_present_future': choice(['"Прошлое, настоящее, будущее"']),
        'fortune_again': choice(['Погадать ещё раз', 'Оливия, у меня ещё вопрос', 'Мне нужно ещё кое-что узнать',
                                 'Пожалуйста, ещё вопрос']),
        'end_session': lambda m: choice([f'Рада была помочь Вам, {database.get_name(m)}. Возвращайтесь, '
                                         f'когда возникнуть вопросы', f'Я сохраню все в своей памяти,'
                                         f' {database.get_name(m)}. Буду рада видеть вас снова',
                                         'Спасибо за то, что доверили мне Ваши вопросы. Я буду тут, если снова '
                                         'понадоблюсь']),
        'after_session': choice(['Тук-тук', 'Мне нужно ещё кое-что узнать', 'Динь-дон...']),
        'start_session': lambda m: choice([f'Что сегодня не даёт Вам покоя, {database.get_name(m)}?',
                                 'Рада вас видеть снова! Какой вопрос привёл Вас ко мне?',
                                 'Новый день - новый вопрос. О чём мы спросим у карт сегодня?',
                                f'Добро пожаловать. Я ждала вас, {database.get_name(m)}. Задавайте вопрос']),
        'get_3_cards': 'Вытянуть три карты',
        'another_alignment': 'Другой расклад',
        'another_alignment_text': 'Хм.. Взглянем-ка еще раз',
        'start_3_cards': 'Этот расклад даст общее понимание о сложившейся ситуации по вашему вопросу.\n'
                                            'Вытяните три карты, чтобы начать.',
        'open_past': 'Открыть карту прошлого',
        'past': '*Карта прошлого*\nКакие установки, чувства или убеждения прошлого повлияли на вопрос?',
        'open_present': 'Открыть карту настоящего',
        'present': '*Карта настоящего*\nКакие силы влияют на вопрос прямо сейчас?',
        'open_future': 'Открыть карту будущего',
        'future': '*Карта будущего*\nКак будет дальше развиваться эта ситуация?',
        'open_cards': 'Осталось только открыть карты..',
        'divination': 'Погадать',
        'divination_text': 'Что ж, для каждой ситуации у меня найдутся карты',
        'human_design': 'Дизайн человека',
    }
}

all_lang = {
    'thx': ['Thanks', 'Спасибо'],
    'get_card': [lang['en']['fortune'], lang['ru']['fortune']],
    'get_card_again': [lang['en']['fortune_again'], lang['ru']['fortune_again']],
    'past_present_future': [lang['en']['past_present_future'], lang['ru']['past_present_future']],
    'after_session': [lang['en']['after_session'], lang['ru']['after_session']],
    'get_3_cards': [lang['en']['get_3_cards'], lang['ru']['get_3_cards']],
    'divination': [lang['en']['divination'], lang['ru']['divination']],
    'another_alignment': [lang['en']['another_alignment'], lang['ru']['another_alignment']],
    'open_3_cards': [lang['en']['open_past'], lang['ru']['open_past'], lang['en']['open_present'],
                     lang['ru']['open_present'], lang['en']['open_future'], lang['ru']['open_future']],
}