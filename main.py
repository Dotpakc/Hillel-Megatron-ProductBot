#Завдання:
#Телеграм бот, інтернет магазин ІТ курсів.
#1. /start - виводить привітання та меню магазину.
#Кнопки Reply: "Курси", "Контакти", "Корзина".
#КУРСИ:
#Сберігаються в папці courses.
#Кожен курс - окремий папка з файлом course.txt та з фотографію.
#Кнопки Inline: "Купити", "Повернутися".
#КОНТАКТИ:
#Виводиться інформація про магазин.
#Кнопки Inline: "Повернутися".
#КОРЗИНА:
#Виводиться список куплених курсів.
#Кнопки Inline: "Оплатити", "Повернутися".
#ОПЛАТА:
#Виводиться інформація про оплату.


#КУРСИ:
    # Виводиться список курсів з папки courses та кнопками 1 - 5. де 1 - перший курс, 2 - другий курс і т.д.
    # Коли користувач нажав на Іnline Кнопку "1" - виводиться інформація про курс.
    #ИНФОРМАЦИЯ ПРО КУРС:
        #Фото курсу
        #Назва курсу
        #Опис курсу
        #Ціна курсу
        #кількість уроків на тиждень
        #кількість уроків в курсі
        #Кнопки Inline: Детальніше(url на сайт), Купити, Повернутися.


import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from decouple import config

from utils import get_courses, get_photo

API_TOKEN = config('API_TELEGRAM')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Reply buttons main menu
main_menu_rep = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_rep.add(types.KeyboardButton('🌟Курси'))
main_menu_rep.add(types.KeyboardButton('📱Контакти')) 
main_menu_rep.add(types.KeyboardButton('🛒Корзина'))

# Inline buttons КУРСИ
inline_kb_courses = types.InlineKeyboardMarkup()
inline_kb_courses.add(types.InlineKeyboardButton('🛒Купити', callback_data='buy'))
inline_kb_courses.add(types.InlineKeyboardButton('◀Повернутися', callback_data='back'))

# Inline buttons КОНТАКТИ
inline_kb_contacts = types.InlineKeyboardMarkup()
inline_kb_contacts.add(types.InlineKeyboardButton('◀Повернутися', callback_data='back'))

# Inline buttons КОРЗИНА
inline_kb_basket = types.InlineKeyboardMarkup()
inline_kb_basket.add(types.InlineKeyboardButton('💳Оплатити', callback_data='pay'))
inline_kb_basket.add(types.InlineKeyboardButton('◀Повернутися', callback_data='back'))

# Inline buttons ОПЛАТА
inline_kb_pay = types.InlineKeyboardMarkup()
inline_kb_pay.add(types.InlineKeyboardButton('◀Повернутися', callback_data='back'))

#Cчитуємо курси з папки courses
courses = get_courses()
 
 
# States
class CoursesState(StatesGroup):
    course = State()
    course_info = State()

@dp.message_handler(commands=['start'], state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    await message.reply("Привіт! Я бот магазину курсів. Обирай один із варіантів меню.", reply_markup=main_menu_rep)
    await state.finish()
    
@dp.message_handler(lambda message: message.text == '🌟Курси', state='*')
async def process_courses_command(message: types.Message, state: FSMContext):
    
    muckup = types.InlineKeyboardMarkup(row_width=5)
    text = 'Оберіть курс:\n'
    buttons = []
    for i, course in enumerate(courses):
        print(course)
        name_course = courses.get(course).get('name')
        text += f'{i+1}. {name_course}\n'
        buttons.append(types.InlineKeyboardButton(f'{i+1}', callback_data=course))
    muckup.add(*buttons)
        
    await message.reply(text, reply_markup=muckup)
    await CoursesState.course.set()
    
@dp.callback_query_handler(lambda c: c.data in courses, state=CoursesState.course)
async def process_callback_course(callback_query: types.CallbackQuery, state: FSMContext):
    course = courses.get(callback_query.data)
    
    photo = get_photo(callback_query.data)
    
    name = course.get('name')
    description = course.get('description')
    price = course.get('price')
    lessons_week = course.get('duration')
    lessons = course.get('lessons')
    level = course.get('level')
    url = course.get('url')
    
    buttons = []
    #url
    buttons.append(types.InlineKeyboardButton('🔗Посилання', url=url))
    buttons.append(types.InlineKeyboardButton('🛒Купити', callback_data='buy'))
    buttons.append(types.InlineKeyboardButton('◀Повернутися', callback_data='back'))
    inline_kb_courses = types.InlineKeyboardMarkup()
    inline_kb_courses.add(*buttons)
    
    text = f'<b>Назва курсу:</b> {name}\n\n<b>Опис курсу:</b> {description}\n\n<b>Ціна курсу:</b> {price} грн.\n<b>Кількість уроків на тиждень:</b> {lessons_week}\n<b>Кількість уроків в курсі:</b> {lessons}'
    await bot.send_photo(callback_query.from_user.id, photo, caption=text, reply_markup=inline_kb_courses , parse_mode='HTML')
    await CoursesState.course_info.set()

@dp.callback_query_handler(lambda c: c.data == 'buy', state=CoursesState.course_info)
async def process_callback_buy(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Курс додано до корзини', reply_markup=inline_kb_basket)
    await state.finish()

    
# Обробка кнопки НАЗАД
@dp.callback_query_handler(lambda c: c.data == 'back', state=CoursesState.course_info)
async def process_callback_back(callback_query: types.CallbackQuery, state: FSMContext):
    await process_courses_command(callback_query.message, state)

#Контакти
@dp.message_handler(lambda message: message.text == '📞Контакти', state='*')
async def process_contacts_command(message: types.Message, state: FSMContext):
    await message.reply('Зв\'яжіться з нами за телефоном: 0800 20 8020\n Або на сайті: https://dnipro.ithillel.ua/contact', reply_markup=main_menu_rep)
  

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)