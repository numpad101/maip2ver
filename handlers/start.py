from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

import config
import system_base
from aiogram import Dispatcher

async def cmd_start(message: Message, state: FSMContext):
    await system_base.create_tables()
    await system_base.add_admin(config.ADMIN_ID) # добавляем главного админа

    await system_base.add_user(message.from_user.id, message.from_user.username)

    admins = await system_base.get_admins()  # получить всех админов
    if message.from_user.id in admins:
        kb = [
            [KeyboardButton(text="Рассылка")],
            [KeyboardButton(text="Изменение товаров")],
            [KeyboardButton(text="Добавить админа"), KeyboardButton(text="Удалить админа")]
        ]

    else:
        kb = [
            [KeyboardButton(text="Магазин Supercell 🎮")],
            [KeyboardButton(text="Магазин Telegram 🌟")],
        ]


    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите нужный раздел"
    )

    await message.bot.send_photo(
        chat_id=message.from_user.id,
        photo=FSInputFile("images/navigation.png"),
        caption="""🐰 <b>Добро пожаловать в Магазин Майпа!</b>
        
Отзывы — @MaipShop
Техническая поддержка — @MaipMaip
Основной канал — @maipbsded
            
🗂️ Выберите интересующий вас раздел снизу.""",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

def register_start_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))