from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

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
products_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Product1", callback_data="product_buying"),
     InlineKeyboardButton(text="Product2", callback_data="product_buying"),
     InlineKeyboardButton(text="Product3", callback_data="product_buying"),
     InlineKeyboardButton(text="Product4", callback_data="product_buying")],
],
    resize_keyboard=True)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for i in range(1, 5):
        await message.answer(f"Название: Product{i} | Описание: описание {i} | Цена: {i * 100}")
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


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение")


if __name__ == '__main__':
    executor.start_polling(dp)
