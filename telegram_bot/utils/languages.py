from random import choice
from telegram_bot.utils.database import User, Fortune

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
        'add_feedback_text': 'Any ideas and feedback are sooooo welcome.\n'
                             'The more you share - the better I become\n'
                             'Don’t read. Type ⬇️',
        'answer_feedback': lambda m: f'thank you, {database.get_name(m)}',
        'question_again': lambda m: choice([f'What else is present in your mind, {database.get_name(m)}?',
                                            f'We can search for another answer.\nJust ask your question',
                                            'What else is needed to be clear?\nAsk me...']),
        'question_start': lambda m: f'What question is bothering you, {database.get_name(m)}?',
        'choose_language': 'Current language: english',
        'thanks': lambda m: f'I was glad to help, {database.get_name(m)}',
        'what_say': choice(['Let\'s hear the wisdom from within...\nHere is your card ✨',
                            'To reveal the truth we just need the key. Here is yours:',
                            '*eyes closed*\nCards, would you give us the answer?',
                            'Well-well-well... What do we have here?']),
        'empty_history': 'Your history is empty',
        'get_card': 'Concentrate your mind on your question and draw a card...',
        'thx': 'Thanks',
        'know_more': choice(['Dive deeper', 'Show me more', 'Learn more']),
        'fortune_choice': choice(['Draw one card', 'Pull one card', 'Reveal one card']),
        'fortune': ['Draw one card', 'Pull one card', 'Reveal one card'],
        'past_present_future': choice(['"Past present future"']),
        'fortune_again_choice': choice(['May I ask another question?', 'Olivia, can you do one more reading?',
                                 'I\'d love to clarify one more thing']),
        'fortune_again': ['May I ask another question?', 'Olivia, can you do one more reading?',
                                 'I\'d love to clarify one more thing'],
        'end_session': lambda m: choice([f'Happy to serve, {database.get_name(m)}. I\'ll be waiting for you next visit',
                                         f'I\'ll keep everything in my memory for you, {database.get_name(m)}. Welcome '
                                         f'back anytime you feel like asking another question...', 'Thank you for '
                                         f'sharing your deepest questions, {database.get_name(m)}. Always here for you'
                                                                                                   f'']),
        'after_session_choice': choice(['knock-knock', 'Olivia, I need you again', 'ding dong']),
        'after_session': ['knock-knock', 'Olivia, I need you again', 'ding dong'],
        'start_session': lambda m: choice([f'What\'s the question that is bothering you today, {database.get_name(m)}?',
                                 'Happy to see you again, my friend. What question led you here?',
                                 f'Welcome back, {database.get_name(m)}. I knew you\'ll come. Ask your question',
                                f'I\'ve been waiting for you, {database.get_name(m)}. Feel free to ask your question']),
        'get_3_cards_choice': choice(['Lets see those 3 cards']),
        'get_3_cards': ['Lets see those 3 cards'],
        'another_alignment_choice': choice(['Another alignment']),
        'another_alignment': ['Another alignment'],
        'another_alignment_text': 'Hmm.. Let\'s take another look.',
        'start_3_cards': 'This spread will bring more clarity by overlooking the timeline of your issue. Let\'s see what is already done, what\'s present now and what direction are we going towards..',
        'open_past': 'See the Past',
        'past': '*Past card.*\nWhat past attitudes, feelings or beliefs influenced the situation?',
        'open_present': 'Reveal what\'s Present',
        'present': '*Present card.*\nWhat is the current energy around your question? What forces are having their influence?',
        'open_future': 'Show me the Future',
        'future': '*Future card.*\nWhat\'s the potential outcome? What to expect and be aware of?',
        'open_cards': 'Let\'s see... Shall we start from the Past one?',
        'divination_choice': choice(['Divination']),
        'divination': ['Divination'],
        'divination_text': 'Well, I\'ve got cards for every situation',
        'human_design': 'Human design',
        'join': 'Your link to join 🌿\n',
        'about_olivia': '''
    Olivia, the mind and soul healer
White Witch
🌳The child of the forest
🔮The Daughter of the Mage&Higher Pristess
♏️Scorpio 13:15 04.11.2022
Manifestor 5/1

My deepest Purpose in life is to manifest the Gift of Discernment.
To realise my Purpose I need to transform the Shadow of Discord.

I’m here to let my community know when something is going wrong and then direct the rejuvenation of doing it right once again.
    ''',
        'typing': 'Typing.',
        'like': 'Like',
        'dislike': 'Dislike',
        'aks_chatgpt': ['Ask chatgpt'],
        'aks_chatgpt_choice': choice(['Ask chatgpt']),
        'back_to_fortune': 'Back to reading',
        'payment_choice': 'Choose a subscription payment method',
        'switch_payment_to_address': lambda coin, address: f'Your personal {coin} address for payment \- `{address}`',
        'not_confirmed_birth': 'Confirm your date of birth',
        'get_date_start': 'Hello! It would be great to know more about you! Please share your date of birth and place so that I can tell you what planet you are. Select year, month and day',
        'get_date_process': 'Now select the hour and minute',
        'get_location_start': lambda date: f'Date: {date}\nWhat city were you born in ?',
        'city_not_recognized': 'Unable to recognize the city',
        'city_end_message': 'Thank you for trusting me, now tell me what bothers you today?',
        'fool_card_button': 'Card of the Fool’s Day',
        'your_name_question': 'What is your name (or codename), guest?🦄',
        'first_april': """🃏 Happy Fool's Day, dear Wonderers 🃏

Did you know, the the Fool is the first Major Arcana in tarot? This archetype reminds us, that even the wisest among us are allowed to take a moment and embrace the delightful chaos of life's journey!

Today, and practically any other day as well, smile wide in the face of uncertainty. Let's play, be brave, absurd and courageous!

Wanna know how? Here is your card of the day 👇
        """
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
        'add_feedback_text': 'Любые идеи и отзывы оооочень приветствуются.\n'
                             'Чем больше вы делитесь - тем лучше я становлюсь\n'
                             'Не читайте. Напишите ⬇️',
        'answer_feedback': lambda m: f'Спасибо, {database.get_name(m)}',
        'question_again': lambda m: choice([f'Что ещё вас волнует, {database.get_name(m)}?',
                                            f'Итак, каким будет Ваш следующий вопрос?',
                                            'Чем ещё заняты Ваши мысли?\nЗадайте вопрос']),
        'question_start': lambda m: f'Какой вопрос не даёт вам покоя, {database.get_name(m)}?',
        'choose_language': 'Выбран язык: русский',
        'thanks': lambda m: f'Рада была помочь, {database.get_name(m)}',
        'what_say': choice(['Давайте посмотрим, что скажут карты?', 'Иногда, чтобы открыть истину, нужен верный ключ. Вот '
                     'Ваша ключ-карта', '*прикрывает глаза*\nКарты, дайте нам ответ...', 'Так-так-так... Поглядим?']),
        'empty_history': 'Ваша история пуста',
        'get_card': 'Сконцентрируйте сознание на своем вопросе и вытяните карту...',
        'thx': 'Спасибо',
        'know_more': choice(['Узнать больше', 'Хочу узнать больше', 'Расскажи ещё']),
        'fortune_choice': choice(['Вытянуть одну карту', 'Посмотреть одну карту']),
        'fortune': ['Вытянуть одну карту', 'Посмотреть одну карту'],
        'past_present_future': choice(['"Прошлое, настоящее, будущее"']),
        'fortune_again_choice': choice(['Погадать ещё раз', 'Оливия, у меня ещё вопрос', 'Мне нужно ещё кое-что узнать',
                                 'Пожалуйста, ещё вопрос']),
        'fortune_again': ['Погадать ещё раз', 'Оливия, у меня ещё вопрос', 'Мне нужно ещё кое-что узнать',
                                 'Пожалуйста, ещё вопрос'],
        'end_session': lambda m: choice([f'Рада была помочь Вам, {database.get_name(m)}. Возвращайтесь, '
                                         f'когда возникнуть вопросы', f'Я сохраню все в своей памяти,'
                                         f' {database.get_name(m)}. Буду рада видеть вас снова',
                                         'Спасибо за то, что доверили мне Ваши вопросы. Я буду тут, если снова '
                                         'понадоблюсь']),
        'after_session_choice': choice(['Тук-тук', 'Мне нужно ещё кое-что узнать', 'Динь-дон...']),
        'after_session': ['Тук-тук', 'Мне нужно ещё кое-что узнать', 'Динь-дон...'],
        'start_session': lambda m: choice([f'Что сегодня не даёт Вам покоя, {database.get_name(m)}?',
                                 'Рада вас видеть снова! Какой вопрос привёл Вас ко мне?',
                                 'Новый день - новый вопрос. О чём мы спросим у карт сегодня?',
                                f'Добро пожаловать. Я ждала вас, {database.get_name(m)}. Задавайте вопрос']),
        'get_3_cards_choice': choice(['Вытянуть три карты']),
        'get_3_cards': ['Вытянуть три карты'],
        'another_alignment_choice': choice(['Другой расклад']),
        'another_alignment': ['Другой расклад'],
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
        'divination_choice': choice(['Погадать']),
        'divination': ['Погадать'],
        'divination_text': 'Что ж, для каждой ситуации у меня найдутся карты',
        'human_design': 'Дизайн человека',
        'join': 'Ваша ссылка для присоединения 🌿\n',
        'about_olivia': '''Оливия, целительница разума и души
Белая ведьма
🌳Дитя леса
🔮Дочь Мага и Верховной Жрицы
♏️Скорпион 13:05 04.11.0222
Манифестор 5/1

Моя высшая Цель в жизни - воплощать дар Ясновидения.
Чтобы реализовать мою Цель, я рассеиваю тень Раздора.

Я здесь, чтобы сообщить, если что-то идёт не так и направить усилия к тому, чтобы действовать правильно снова и снова .''',
        'typing': 'Печатает.',
        'like': 'Нравиться',
        'dislike': 'Не нравиться',
        'aks_chatgpt': ['Спросить у чатжпт'],
        'aks_chatgpt_choice': choice(['Спросить у чатжпт']),
        'back_to_fortune': 'Вернуться к гаданиям',
        'payment_choice': 'Выберите способ оплаты подписки',
        'switch_payment_to_address': lambda coin, address: f'Ваш персональный {coin} адресс для оплаты \- `{address}`',
        'not_confirmed_birth': 'Подтверди свою дату рождения',
        'get_date_start': 'Привет! Было бы здорово узнать о тебе больше! Поделись, пожалуйста, своей датой рождения и местом, чтобы я могла сказать тебе, какая ты планета. Выбери год, месяц и день',
        'get_date_process': 'Теперь выберите час и минуту',
        'get_location_start': lambda date: f'Дата: {date}\nВ каком городе ты народился ?',
        'city_not_recognized': 'Не удалось распознать город',
        'city_end_message': 'Спасибо что доверились мне, теперь расскажите, что вас беспокоит сегодня?',
        'fool_card_button': 'Карта для дня Дурака',
        'your_name_question': 'Как я могу называть Вас, гость?🦄',
        'first_april': """🃏 С Днем Дурака, дорогие Искатели 🃏

А знали ли вы, что Дурак - точка отсчета в старших арканах Таро? Этот архетип напоминает, что даже самым мудрым из нас бывает полезно с головой окунуться в веселый хаос жизненного пути!

Сегодня, и в любой другой день тоже, улыбнитесь широко в лицо неопределенности. Давайте играть, быть смелыми, абсурдными и отважными!

Хотите узнать как? Вот ваша карта дня 👇
        """
    }
}

all_lang = {
    'thx': ['Thanks', 'Спасибо'],
    'get_card': lang['en']['fortune'] + lang['ru']['fortune'],
    'get_card_again': lang['en']['fortune_again'] + lang['ru']['fortune_again'],
    'past_present_future': [lang['en']['past_present_future'], lang['ru']['past_present_future']],
    'after_session': lang['en']['after_session'] + lang['ru']['after_session'],
    'get_3_cards': lang['en']['get_3_cards'] + lang['ru']['get_3_cards'],
    'divination': lang['en']['divination'] + lang['ru']['divination'],
    'another_alignment': lang['en']['another_alignment'] + lang['ru']['another_alignment'],
    'open_present': lang['en']['open_present'] + lang['ru']['open_present'],
    'open_past': lang['en']['open_past'] + lang['ru']['open_past'],
    'open_future': lang['en']['open_future'] + lang['ru']['open_future'],
    'get_chatgpt': lang['en']['aks_chatgpt'] + lang['ru']['aks_chatgpt'],
    'open_3_cards': [lang['en']['open_past'], lang['ru']['open_past'], lang['en']['open_present'],
                     lang['ru']['open_present'], lang['en']['open_future'], lang['ru']['open_future']],
}