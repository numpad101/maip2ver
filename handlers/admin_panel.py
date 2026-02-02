from aiogram import Dispatcher, F
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
import system_base, logging


class BroadcastForm(StatesGroup):
    waiting_for_message = State()
    waiting_for_new_admin_id = State()
    waiting_for_delete_admin_id = State()

    waiting_for_new_product_brawl = State()
    waiting_for_vary_product_brawl = State()
    waiting_for_new_product_clash = State()
    waiting_for_vary_product_clash = State()
    waiting_for_new_product_clans = State()
    waiting_for_vary_product_clans = State()

    waiting_for_vary_price_trade = State()

    waiting_for_new_product_prem = State()
    waiting_for_vary_product_prem = State()

    waiting_for_vary_price_ton = State()



def escape_markdown_v2(text):
    # список зарезервированных символов в MarkdownV2
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return ''.join(f'\\{c}' if c in special_chars else c for c in text)


async def handler_msg(attr: Message | CallbackQuery, state: FSMContext):
    if isinstance(attr, Message):
        msg: Message = attr.text.lower()
        message = attr
        if msg == "рассылка" or msg == "добавить админа" or msg == "удалить админа":
            admins = await system_base.get_admins()
            if message.from_user.id not in admins:
                return
            if msg == "рассылка":
                await message.answer("Введите содержимое сообщения для рассылки:")
                await state.set_state(BroadcastForm.waiting_for_message)
    
            elif msg == "добавить админа":
                await message.answer("Введите ID аккаунта тг (можно узнать в @userinfobot)")
                await state.set_state(BroadcastForm.waiting_for_new_admin_id)

            elif msg == "удалить админа":
                mess = "Список админов:\n"
                i = 1
                for id in admins:
                    adm_info = await message.bot.get_chat(id)
                    mess += f"ID `{id}` @{adm_info.username}\n"
                    i += 1
                await message.answer("Введите ID админа, чтобы удалить его")
                await message.answer(escape_markdown_v2(mess), parse_mode="Markdown")
                await state.set_state(BroadcastForm.waiting_for_delete_admin_id)

async def start_add_product_supercell(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите продукт и его цену в рублях (просто число)."
                         "\n\nФормат:\n[30 гемов, 60]")
    print(callback.data)
    if callback.data == "products_supercell_brawl_add_product":
        await state.set_state(BroadcastForm.waiting_for_new_product_brawl)
    elif callback.data == "products_supercell_clash_add_product":
        await state.set_state(BroadcastForm.waiting_for_new_product_clash)
    elif callback.data == "products_supercell_clans_add_product":
        await state.set_state(BroadcastForm.waiting_for_new_product_clans)

async def start_vary_product_supercell(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новые данные.")
    if callback.data == "start_vary_product_brawl":
        await state.set_state(BroadcastForm.waiting_for_vary_product_brawl)
    elif callback.data == "start_vary_product_clash":
        await state.set_state(BroadcastForm.waiting_for_vary_product_clash)
    elif callback.data == "products_supercell_clans_add_product":
        await state.set_state(BroadcastForm.waiting_for_vary_product_clans)


async def start_vary_price_ton(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите цену в рублях за 1 TON (просто число)")
    await state.set_state(BroadcastForm.waiting_for_vary_price_ton)



async def start_add_product_prem(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите срок и стоимость в рублях (просто число)"
                         "\n\nФормат:\n[3 месяца, 600]")
    await state.set_state(BroadcastForm.waiting_for_new_product_prem)

async def start_vary_product_prem(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите срок и стоимость в рублях (просто число)"
                                     "\n\nФормат:\n[3 месяца, 600]")
    await state.set_state(BroadcastForm.waiting_for_vary_product_prem)


# Обработчик текстового сообщения в состоянии рассылки
async def process_broadcast_message(message: Message, state: FSMContext):
    users = await system_base.get_value('users')
    if not users:
        await message.answer("Нет пользователей для рассылки.")
        await state.clear()
        return

    success_count = 0
    fail_count = 0
    admins = await system_base.get_admins()
    for user in users:
        user_id = user['id']
        try:
            if user_id not in admins:
                if message.content_type == ContentType.TEXT:
                    await message.bot.send_message(chat_id=user_id, text=message.text)
                elif message.content_type == ContentType.PHOTO:
                    # Выбираем самое большое фото из доступных
                    photo = message.photo[-1]
                    caption = message.caption if message.caption else ''
                    await message.bot.send_photo(chat_id=user_id, photo=photo.file_id, caption=caption)
                elif message.content_type == ContentType.DOCUMENT:
                    caption = message.caption if message.caption else ''
                    await message.bot.send_document(chat_id=user_id, document=message.document.file_id, caption=caption)
                elif message.content_type == ContentType.VIDEO:
                    caption = message.caption if message.caption else ''
                    await message.bot.send_video(chat_id=user_id, video=message.video.file_id, caption=caption)
                elif message.content_type == ContentType.AUDIO:
                    caption = message.caption if message.caption else ''
                    await message.bot.send_audio(chat_id=user_id, audio=message.audio.file_id, caption=caption)
                elif message.content_type == ContentType.VOICE:
                    await message.bot.send_voice(chat_id=user_id, voice=message.voice.file_id)
                elif message.content_type == ContentType.ANIMATION:
                    caption = message.caption if message.caption else ''
                    await message.bot.send_animation(chat_id=user_id, animation=message.animation.file_id, caption=caption)
                elif message.content_type == ContentType.VIDEO_NOTE:
                    await message.bot.send_video_note(chat_id=user_id, video_note=message.video_note.file_id)
                elif message.content_type == ContentType.STICKER:
                    await message.bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)

                else:
                    fail_count += 1
                    continue

                success_count += 1
        except Exception as e:
            logging.error(f"Ошибка при отправке пользователю {user_id}: {e}")
            fail_count += 1
    if success_count == 0:
        await message.answer(f"Ошибка: Бот не способен сделать рассылку такого формата")
        return

    await message.answer(
        f"Рассылка завершена!\n{success_count}/{success_count + fail_count} пользователей получили сообщение")
    await state.clear()


async def process_add_admin(message: Message, state: FSMContext):
    try:
        id = int(message.text)
        print(await system_base.get_value('admins', {'id':id}))
        if len(await system_base.get_value('admins', {'id':id})) == 0:
            await message.bot.send_message(id, "Теперь Вы - админ!\nПерезапустите бота (/start)")
            text = f"***ВЫ ДОБАВИЛИ НОВОГО АДМИНА!***\nID: {id}\n"
            await message.answer(text)
            await system_base.add_admin(id)
            await state.clear()
        else: await message.answer("Этот админ уже есть в базе.")
    except Exception as e:
        await message.answer("Некорректные данные!")

        logging.error(f"Ошибка: {e}")


async def process_delete_admin(message: Message, state: FSMContext):
    try:
        id = int(message.text)
        id = await system_base.get_value('admins', {'id':id})
        print(id, id[0], id[0].get('id'), sep=" _=_ ")
        print(len(id) != 0)
        print(config.ADMIN_ID != id[0].get('id'))
        if len(id) != 0 and config.ADMIN_ID != id[0].get('id'):
            await message.bot.send_message(id[0].get('id'), "Вы больше не админ.\nПерезапустите бота (/start)")
            text = f"***ВЫ УДАЛИЛИ АДМИНА!***\nID: {id}\n"
            await message.answer(text)
            await system_base.delete_admin(id)
            await state.clear()
        elif config.ADMIN_ID == id[0].get('id'):
            await message.answer("Главного админа нельзя удалить!")
        else:
            await message.answer("Нет такого админа.")
    except Exception as e:
        await message.answer("Некорректные данные!")
        logging.error(f"Ошибка: {e}")


async def process_change_products(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменение: Магазин Supercell", callback_data="supercell")],
        [InlineKeyboardButton(text="Изменение: Магазин Telegram", callback_data="telegram")],

    ])


    await message.answer(
        "🛍️ Выберите магазин для редактирования:",
        reply_markup=kb,
    )

async def process_change_products_supercell(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Brawl Stars", callback_data="supercell_brawl")],
        [InlineKeyboardButton(text="Clash Royale", callback_data="supercell_clash")],
        [InlineKeyboardButton(text="Clash of Clans", callback_data="supercell_clans")]
    ])

    await callback.message.edit_text(
        "🎮 Редактирование товаров для:",
        reply_markup=kb,
    )

async def process_change_products_supercell_games(callback: CallbackQuery, state: FSMContext):
    if callback.data == "supercell_brawl":
        game = 'brawl'
    elif callback.data == "supercell_clash":
        game = 'clash'
    elif callback.data == "supercell_clans":
        game = "clans"
    table = await system_base.get_value(f'products_supercell_{game}')
    kb = []
    if len(table) != 0:
        for item in table:
            btn = InlineKeyboardButton(
                text=f"{item['label']} = {item['price']}, руб.",
                callback_data=f"admin_shop_supercell_{game}_gems_{item['id']}"
            )
            kb.append([btn])
            print(btn.callback_data)
    kb.append([InlineKeyboardButton(text="+ Добавить продукт", callback_data=f"products_supercell_{game}_add_product")])

    await state.update_data(game=game)
    await callback.message.edit_text(
        "Список продуктов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )

async def process_change_products_supercell_games_add_product(message: Message, state: FSMContext):
    game = (await state.get_data()).get("game")
    try:
        content = message.text.split(',')
        label = content[0].strip()
        price = int(content[1].strip())
        print(label, price)
        await system_base.add_product(f'products_supercell_{game}', label, price)
        await message.answer(f"Вы добавили новый продукт:\n---------------\nНаименование: {label}\nЦена: {price}")
        await state.clear()
    except Exception as e:
        await message.answer("Некорректные данные! Попробуйте ввести ещё раз, соблюдая правила ввода.")
        logging.error(f"Ошибка: {e}")


async def process_change_products_supercell_games_click_product(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("admin_shop_supercell_brawl_gems_"):
        game = "brawl"
    elif callback.data.startswith("admin_shop_supercell_clash_gems_"):
        game = "clash"
    else:
        game = "clans"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить данные продукта", callback_data='vary_' + callback.data)],
        [InlineKeyboardButton(text="Удалить продукт", callback_data=f'delete_' + game + '_' + callback.data)],
    ])
    await state.update_data(game=game)
    await callback.message.edit_text("Выберите действие:", reply_markup=kb)


async def process_change_products_supercell_vary_product(callback: CallbackQuery, state: FSMContext):
    game = (await state.get_data()).get("game")
    data_parts = callback.data.split('_')
    product_id = data_parts[-1]
    await callback.message.edit_text("Введите новую информацию о продукте и его цену в рублях (просто число)"
                                     "\n\nФормат:\n[500 гемов, 1000]")

    if game == "brawl":
        await state.set_state(BroadcastForm.waiting_for_vary_product_brawl)
    elif game == "clash":
        await state.set_state(BroadcastForm.waiting_for_vary_product_clash)
    else:
        await state.set_state(BroadcastForm.waiting_for_vary_product_clans)

    await state.update_data(product_id=product_id, game=game)

async def process_new_product_data_supercell(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    game = data.get('game')

    if not product_id:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.clear()
        return

    try:
        content = message.text.split(',')
        new_label = content[0].strip()
        new_price = content[1].strip()

        await system_base.update_product(f'products_supercell_{game}', product_id, new_label, new_price)

        await message.answer(f"Продукт обновлён:\nНазвание: {new_label}\nЦена: {new_price}")
        await state.clear()
    except Exception as e:
        await message.answer("Некорректный формат. Попробуйте снова: 'Название, Цена'.")
        logging.error(f"Ошибка при обновлении продукта: {e}")


async def process_delete_confirmation_supercell(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data.startswith('delete_brawl_admin_shop_supercell_clash_gems_'):
        delete_game = "delete_brawl"
    elif data.startswith('delete_clash_admin_shop_supercell_clash_gems_'):
        delete_game = "delete_clash"
    elif data.startswith('back_to'):
        # Переход назад к списку продуктов без удаления
        await process_change_products_supercell_games(callback, state)
        await callback.answer("Отмена удаления.")
        return
    else:
        delete_game = "delete_clans"
    product_data = data[len(f'{delete_game}_'):]  # admin_shop_supercell_brawl_gems_123
    parts = product_data.split('_')
    product_id = parts[-1]

    try:
        print()
        # Удаляем продукт из базы данных
        await system_base.delete_product(f'products_supercell_{delete_game.split("_")[1]}', product_id)

        # Обновляем список продуктов после удаления
        table = await system_base.get_value(f'products_supercell_{delete_game.split("_")[1]}')
        kb = []
        if len(table) != 0:
            for item in table:
                text = f"{item['label']} = {item['price']}, руб."
                btn = InlineKeyboardButton(
                    text=text,
                    callback_data=f"admin_shop_supercell_{delete_game.split("_")[1]}_gems_{item['id']}"
                )
                kb.append([btn])
        kb.append([InlineKeyboardButton(text="+ Добавить продукт", callback_data=f"products_supercell_{delete_game.split("_")[1]}_add_product")])

        await callback.message.edit_text(
            "Продукт удалён.\n\nОбновлённый список продуктов:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        )
        await callback.answer("Продукт успешно удалён.")
    except Exception as e:
        logging.error(f"Ошибка при удалении продукта: {e}")
        await callback.answer("Ошибка при удалении продукта.", show_alert=True)
    await state.clear()


async def process_change_products_tg(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обменник звёзд", callback_data="telegram_trade")],
        [InlineKeyboardButton(text="Телеграм Премиум", callback_data="telegram_prem")],
        [InlineKeyboardButton(text="TON", callback_data="telegram_ton")],
    ])

    await callback.message.edit_text(
        "🔄 Выберите раздел",
        reply_markup=kb,
    )



async def process_change_products_tg_prem(callback: CallbackQuery):
    table_trade = await system_base.get_value('products_tg_prem')
    print(callback.data)
    kb = []
    if len(table_trade) != 0:
        for item in table_trade:
            btn = InlineKeyboardButton(
                text=f"{item['label']} = {item['price']}, руб.",
                callback_data=f"admin_shop_products_tg_prem_{item['id']}"
            )
            kb.append([btn])
            print(btn.callback_data)
    kb.append([InlineKeyboardButton(text="+ Добавить продукт", callback_data=f"products_tg_prem_add_product")])

    await callback.message.edit_text(
        "Список продуктов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


async def process_change_products_tg_prem_add_product(message: Message, state: FSMContext):
    try:
        content = message.text.split(',')
        label = content[0].strip()
        price = int(content[1].strip())
        print(label, price)
        await system_base.add_product('products_tg_prem', label, price)
        await message.answer(f"Вы добавили новый продукт:\n---------------\nНаименование: {label}\nЦена: {price}")
        await state.clear()
    except Exception as e:
        await message.answer("Некорректные данные! Попробуйте ввести ещё раз, соблюдая правила ввода.")
        logging.error(f"Ошибка: {e}")

async def process_change_products_tg_prem_click_product(callback: CallbackQuery):
    print(callback.data)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить данные продукта", callback_data='vary_' + callback.data)],
        [InlineKeyboardButton(text="Удалить продукт", callback_data='delete_prem_' + callback.data)],
    ])
    await callback.message.edit_text("Выберите действие:", reply_markup=kb)

async def process_change_products_tg_prem_vary_product(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split('_')
    if len(data_parts) < 5:
        await callback.answer("Некорректные данные для изменения.")
        return

    product_id = data_parts[-1]

    await callback.message.edit_text("Введите новый срок и его цену в рублях через запятую (просто число)"
                         "\n\nФормат:\n[3 месяца, 646]")

    # Запомнить выбранный продукт
    await state.update_data(product_id=product_id)
    await state.set_state(BroadcastForm.waiting_for_vary_product_prem)


async def process_new_product_data_prem(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    print(product_id)
    if not product_id:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.clear()
        return

    try:
        content = message.text.split(',')
        new_label = content[0].strip()
        new_price = content[1].strip()

        await system_base.update_product('products_tg_prem', product_id, new_label, new_price)

        await message.answer(f"Продукт обновлён:\nНазвание: {new_label}\nЦена: {new_price}")
        await state.clear()
    except Exception as e:
        await message.answer("Некорректный формат. Попробуйте снова: 'Название, Цена'.")
        logging.error(f"Ошибка при обновлении продукта: {e}")


async def process_delete_confirmation_prem(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    print(data)
    if data.startswith('delete_prem_'):
        product_data = data[len('delete_prem_'):]
        parts = product_data.split('_')
        product_id = parts[-1]

        try:
            # Удаляем продукт из базы данных
            await system_base.delete_product('products_tg_prem', product_id)

            # Обновляем список продуктов после удаления
            table_prem = await system_base.get_value('products_tg_prem')
            kb = []
            if len(table_prem) != 0:
                for item in table_prem:
                    text = f"{item['label']} = {item['price']}, руб."
                    btn = InlineKeyboardButton(
                        text=text,
                        callback_data=f"admin_shop_telegram_prem_{item['id']}"
                    )
                    kb.append([btn])
            kb.append([InlineKeyboardButton(text="+ Добавить продукт", callback_data="products_telegram_prem_add_product")])

            await callback.answer("Продукт успешно удалён.")
        except Exception as e:
            logging.error(f"Ошибка при удалении продукта: {e}")
            await callback.answer("Ошибка при удалении продукта.", show_alert=True)
        await state.clear()

    elif data.startswith('back_to_prem'):
        # Переход назад к списку продуктов без удаления
        await process_change_products_tg_prem(callback)
        await callback.answer("Отмена удаления.")


async def start_vary_price_trade(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отлично! Теперь введите цены за одну звезду до и после 500 ⭐️ в формате:\n"
                                     "цена_до, цена_после\n"
                                     "например: 1.4, 1.35\n\n"
                                     "Обратите внимание:\n"
                                     "Размер звезд — до и после — разделены запятой")
    await state.set_state(BroadcastForm.waiting_for_vary_price_trade)

async def change_price_stars(message: Message, state: FSMContext):
    try:
        data = message.text.split(',')
        price_default = float(data[0])
        price_500plus = float(data[1])
        await system_base.update_price_trade(price_default, price_500plus)
        await message.answer(f"Успешно!\n\nЦена до 500 звёзд: {price_default}\nЦена после 500 звёзд: {price_500plus}")
        await state.clear()
    except Exception as e:
        logging.error(e)
        await message.answer("Некорректные данные. Введите заново, соблюдая все правила ввода!")
        await state.clear()


async def change_price_ton(message: Message, state: FSMContext):
    try:
        data = float(message.text)
        await system_base.update_price_ton(data)
        await message.answer(f"Успешно!\n\nЦена за 1 TON: {data}")
        await state.clear()
    except Exception as e:
        logging.error(e)
        await message.answer("Некорректные данные. Введите заново, соблюдая все правила ввода!")
        await state.clear()

def register_admin_handler(dp: Dispatcher):
    dp.callback_query.register(start_vary_price_trade, F.data == "telegram_trade")
    dp.callback_query.register(start_vary_price_ton, F.data == "telegram_ton")

    dp.message.register(change_price_stars, StateFilter(BroadcastForm.waiting_for_vary_price_trade))
    dp.message.register(handler_msg, F.text.lower() == "рассылка")
    dp.message.register(handler_msg, F.text.lower() == "добавить админа")
    dp.message.register(handler_msg, F.text.lower() == "удалить админа")
    dp.message.register(process_change_products, F.text.lower() == "изменение товаров")

    dp.callback_query.register(process_change_products_supercell, F.data == "supercell")

    dp.callback_query.register(process_change_products_supercell_games, F.data == "supercell_brawl")
    dp.callback_query.register(process_change_products_supercell_games, F.data == "supercell_clash")
    dp.callback_query.register(process_change_products_supercell_games, F.data == "supercell_clans")

    dp.callback_query.register(start_add_product_supercell, F.data == "products_supercell_brawl_add_product")
    dp.callback_query.register(start_add_product_supercell, F.data == "products_supercell_clash_add_product")
    dp.callback_query.register(start_add_product_supercell, F.data == "products_supercell_clans_add_product")
    dp.callback_query.register(
        process_change_products_supercell_games_click_product,
        F.data.startswith("admin_shop_supercell_brawl_gems_")
    )
    dp.callback_query.register(
        process_change_products_supercell_games_click_product,
        F.data.startswith("admin_shop_supercell_clash_gems_")
    )
    dp.callback_query.register(
        process_change_products_supercell_vary_product,
        F.data.startswith('vary_admin_shop_supercell_brawl_gems_')
    )
    dp.callback_query.register(
        process_change_products_supercell_vary_product,
        F.data.startswith('vary_admin_shop_supercell_clash_gems_')
    )
    dp.callback_query.register(process_delete_confirmation_supercell, F.data.startswith('delete_brawl_'))
    dp.callback_query.register(process_delete_confirmation_supercell, F.data.startswith('back_to'))
    dp.callback_query.register(process_delete_confirmation_supercell, F.data.startswith('delete_clash_'))



    dp.message.register(process_broadcast_message, StateFilter(BroadcastForm.waiting_for_message))
    dp.message.register(process_add_admin, StateFilter(BroadcastForm.waiting_for_new_admin_id))
    dp.message.register(process_delete_admin, StateFilter(BroadcastForm.waiting_for_delete_admin_id))

    dp.message.register(process_change_products_supercell_games_add_product, StateFilter(BroadcastForm.waiting_for_new_product_brawl))
    dp.message.register(process_change_products_supercell_games_add_product, StateFilter(BroadcastForm.waiting_for_new_product_clash))
    dp.message.register(process_change_products_supercell_games_add_product, StateFilter(BroadcastForm.waiting_for_new_product_clans))

    dp.message.register(process_new_product_data_supercell, StateFilter(BroadcastForm.waiting_for_vary_product_brawl))
    dp.message.register(process_new_product_data_supercell, StateFilter(BroadcastForm.waiting_for_vary_product_clash))
    dp.message.register(process_new_product_data_supercell, StateFilter(BroadcastForm.waiting_for_vary_product_clans))

    dp.callback_query.register(
        process_change_products_tg_prem_click_product,
        F.data.startswith("admin_shop_products_tg_prem_")
    )
    dp.callback_query.register(
        process_change_products_tg_prem_vary_product,
        F.data.startswith("vary_admin_shop_products_tg_prem_")
    )

    dp.message.register(process_new_product_data_prem, StateFilter(BroadcastForm.waiting_for_vary_product_prem))
    dp.message.register(process_change_products_tg_prem_add_product, StateFilter(BroadcastForm.waiting_for_new_product_prem))
    dp.message.register(change_price_ton, StateFilter(BroadcastForm.waiting_for_vary_price_ton))

    dp.callback_query.register(process_change_products_tg, F.data == "telegram")

    dp.callback_query.register(process_change_products_tg_prem, F.data == "telegram_prem")
    dp.callback_query.register(start_add_product_prem, F.data == "products_tg_prem_add_product")
    dp.callback_query.register(process_delete_confirmation_prem, F.data.startswith('delete_prem_'))
    dp.callback_query.register(process_delete_confirmation_prem, F.data.startswith('back_to_tg'))

