from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

import crud_functions as crud

with open("API", "r", encoding="utf-8") as f:
    api = f.read()
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
start_menu = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")
button2 = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
start_menu.add(button, button2)

main_menu1 = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text="Рассчитать")
button_2 = KeyboardButton(text="Информация")
button_3 = KeyboardButton(text="Купить")
main_menu1.add(button_1, button_2)
main_menu1.add(button_3)
main_menu1.add(KeyboardButton(text="Регистрация"))
products = [InlineKeyboardButton(text=i[1], callback_data="product_buying") for i in
            crud.get_all_products("not_telegram.db")]
products_menu = InlineKeyboardMarkup(inline_keyboard=[
    products,
],
    resize_keyboard=True)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for i in crud.get_all_products("not_telegram.db"):
        await message.answer(f"Название: {i[1]} | Описание: {i[2]} | Цена: {i[3]}")
        with open("urban.jpg", "rb") as img:
            await message.answer_photo(img)
    await message.answer(f"Выберите продукты для покупки", reply_markup=products_menu)


@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer(f"Вы успешно приобрели товар")
    await call.answer()


@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=start_menu)


@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer()


@dp.callback_query_handler(text="calories")
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    await state.finish()
    await message.answer(
        f"Ваша норма калорий: {10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5}")


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью", reply_markup=main_menu1)


@dp.message_handler(text="Информация")
async def inform(message):
    await message.answer("Информация о боте")


@dp.message_handler(text="Регистрация")
async def sign_up(message):
    await message.answer("Введите имя пользователя (Только латинский алфавит)")
    await RegistrationState.username.set()


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение")


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    async with state.proxy() as data:
        username = message.text.strip()
        if crud.is_included("not_telegram.db", username):
            await message.answer("Пользователь с таким именем уже существует")
            await RegistrationState.username.set()
        else:
            data["username"] = username
            await message.answer("Введите свой email:")
            await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    async with state.proxy() as data:
        email = message.text.strip()
        data["email"] = email
        await message.answer("Введите свой возраст:")
        await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            age = int(message.text.strip())
            data['age'] = age
            data["balance"] = 1000

            crud.add_user("not_telegram.db", data["username"], data["email"], data["age"], data["balance"])

            await message.answer(f"Пользователь {data['username']} успешно зарегистрирован!")
            await state.finish()
        except ValueError:
            await message.answer("Возраст должен быть числом. Попробуйте снова:")
            await RegistrationState.age.set()


if __name__ == '__main__':
    executor.start_polling(dp)
