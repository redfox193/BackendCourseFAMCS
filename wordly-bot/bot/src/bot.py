import logging
import asyncio
from aiogram import Bot, Router, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from db import Database
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

db = Database()


class AddWord(StatesGroup):
    word = State()
    translation = State()


def get_word_inline_keyboard_markup(word_id: int, username: str, front_side: bool = True) -> InlineKeyboardMarkup:
    flip_button = (
        InlineKeyboardButton(text="Перевернуть", callback_data=f"flip_back_{word_id}_{username}") if front_side
        else InlineKeyboardButton(text="Перевернуть", callback_data=f"flip_front_{word_id}_{username}")
    )

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data=f"correct_{word_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"wrong_{word_id}")
        ],
        [flip_button],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{word_id}")]
    ])


@router.message(Command('start'))
async def start(message: types.Message):
    await db.add_user(message.from_user.username)
    await message.answer("Привет! Я помогу тебе учить слова. Используй /add, /word.")


@router.message(Command('word'))
async def get_word(message: types.Message, state: FSMContext):
    await state.clear()

    username = message.from_user.username
    word_data = await db.get_random_word(message.from_user.username)

    if word_data:
        word_id, word = word_data['id'], word_data['word']

        keyboard = get_word_inline_keyboard_markup(word_id, username)
        await message.answer(word, reply_markup=keyboard)
    else:
        await message.answer("В вашем словаре пока нет слов.")


@router.callback_query(lambda c: c.data.startswith("flip_"))
async def flip_word(callback: types.CallbackQuery):
    is_front_side = callback.data.split("_")[1] == "front"
    word_id = int(callback.data.split("_")[2])
    username = callback.data.split("_")[3]

    if word_id:
        message = await (db.get_word(word_id) if is_front_side else db.get_translation(word_id))
        if message:
            keyboard = get_word_inline_keyboard_markup(word_id, username, is_front_side)
            await callback.message.edit_text(message, reply_markup=keyboard)
        else:
            await callback.message.edit_text("Ошибка: слово не найдено.")
    else:
        await callback.message.edit_text("Сначала запросите слово командой /word.")


@router.callback_query(lambda c: c.data.startswith("correct_") or c.data.startswith("wrong_"))
async def check_answer(callback: types.CallbackQuery):
    correct = callback.data.startswith("correct_")
    word_id = int(callback.data.split("_")[1])

    await db.update_priority(word_id, correct)
    await callback.message.edit_text("Принято👍")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_word(callback: types.CallbackQuery):
    word_id = int(callback.data.split("_")[1])

    await db.delete_word(word_id)
    await callback.message.edit_text("Слово удалено ✅")


@router.message(Command('add'))
async def add_word_start(message: types.Message, state: FSMContext):
    await state.set_state(AddWord.word)
    await message.answer("Введите слово:")


@router.message(AddWord.word)
async def add_word_step_1(message: types.Message, state: FSMContext):
    await state.update_data(word=message.text)
    await state.set_state(AddWord.translation)
    await message.answer("Введите перевод:")


@router.message(AddWord.translation)
async def add_word_step_2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    word, translation = data['word'], message.text
    success = await db.add_word(message.from_user.username, word, translation)

    if success:
        await message.answer("Слово добавлено!")
    else:
        await message.answer("Ошибка добавления слова.")

    await state.clear()


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="word", description="Получить слово"),
        BotCommand(command="add", description="Добавить слово"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await db.connect()
    await db.create_tables()

    await set_bot_commands(bot)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
