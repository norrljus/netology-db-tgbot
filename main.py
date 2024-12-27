import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from db_models import UsersId, Dictionary, LearnWords
from db_connect import make_session


print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = '7712595422:AAF6133SqxMGnIBwWsF8bZMfhCwG07i32rw'
bot = TeleBot(token_bot, state_storage=state_storage)

session = make_session()

known_users = []
aux = session.query(UsersId).all()
for i in aux:
    known_users.append(i.usertgid)
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def addstarterwords(cid):
    tabuserid = session.query(UsersId).where(UsersId.usertgid == cid).all()[0].id
    for y in range(10):
        session.add(LearnWords(user_id=tabuserid, dict_id=(y+1)))
    session.commit()


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        userStep[cid] = 0
        session.add(UsersId(usertgid=cid))
        session.commit()
        bot.send_message(cid, "Hello, stranger, let study English...")
        addstarterwords(cid)
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    #words = session.query(LearnWords).join(Dictionary.wordid).join(UsersId.userid).where(UsersId == cid).limit(4).all()
    words = (session.query(Dictionary)
             .join(LearnWords, LearnWords.dict_id == Dictionary.id)
             .join(UsersId, UsersId.id == LearnWords.user_id)
             .filter(UsersId.usertgid == cid)
             .all())
    target_word = words[0].engword   # взято из БД
    translate = words[0].rusword     # взято из БД
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = [words[1].engword, words[2].engword, words[3].engword]  # брать из БД
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        session.query(Dictionary).join(LearnWords.dict_id).filter(Dictionary.rusword == message).delete()  # удалить
        session.commit()


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    hint = 'Введите слово в формате:\n english-русский'
    bot.send_message(message.chat.id, hint)
    if '-' not in message.text:
        hint = 'обратите внимание на формат english-русский. Через дефис'
        bot.send_message(message.chat.id, hint)
    english, russian = message.text.split('-')
    if not session.query(Dictionary).filter(Dictionary.engword == english):
        Dictionary.addword(cid, english, russian)
        dictionaryenru = Dictionary.selectwordsbyuser(cid)
        hint = f'Слово 🇬🇧 {english} добавлено в базу.\nВсего {len(dictionaryenru)} слов'
        bot.send_message(message.chat.id, hint)
    create_cards(message)
    userStep[cid] = 0


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
