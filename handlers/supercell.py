from aiogram import types
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import system_base
from handlers.core_funcs import check_time, send_to_admin

class ShopStates(StatesGroup):
    confirm_buy = State()

async def shop_supercell(message: types.Message, state: FSMContext):
    admins = await system_base.get_admins()
    if message.from_user.id not in admins:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text = "Brawl Stars",
                        callback_data="shop_supercell_brawl_gems",
                   )
                ],
                [
                    types.InlineKeyboardButton(
                        text = "Clash Royale",
                        callback_data="shop_supercell_clash_gems",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Clash of Clans",
                        callback_data="shop_supercell_clans_gems",
                    )
                ]
            ]
        )
        try:
            await message.edit_media(
                media=types.InputMediaPhoto(
                    media=FSInputFile(f"images/navigation.png"),
                    caption="Выберите игру с помощью клавиатуры снизу 👇"
                ),
                reply_markup=keyboard
            )
        except Exception as e:
            print(e)
            await message.delete()
            await message.answer(
                "Выберите игру с помощью клавиатуры снизу 👇",
                reply_markup=keyboard,
            )

async def shop_supercell_products_callback(callback: CallbackQuery):
    if callback.data == "shop_supercell_brawl_gems":
        game = "brawl"
    elif callback.data == "shop_supercell_clash_gems":
        game = "clash"
    else:
        game = "clans"
        print(f"{game=}")

    table = await system_base.get_value(f'products_supercell_{game}')
    kb = []
    txt = "Здесь пока пусто"
    if len(table) != 0:
        txt = "Выберите товар с помощью клавиатуры снизу  👇"
        for item in table:
            btn = InlineKeyboardButton(
                text=f"{item['label']} = {item['price']}, руб.",
                callback_data=f"shop_supercell_{game}_gems_{item['id']}"
            )
            kb.append([btn])
        # Добавляем кнопку "Назад" сюда
        back_btn = InlineKeyboardButton(
            text="Назад",
            callback_data="shop_back_supercell"
        )
        kb.append([back_btn])

    inline_markup = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=FSInputFile(f"images/price_{game}.png"),
            caption=txt,
            parse_mode="Markdown"
        ),
        reply_markup=inline_markup
    )

async def shop_supercell_back(callback: CallbackQuery, state: FSMContext):
    # Проверка прав не обязательна, так как это возврат
    await shop_supercell(callback.message, state)
    await callback.answer()

async def confirm(callback: CallbackQuery, state: FSMContext):
    context = await state.get_data()
    if context == {}:
        await callback.message.answer("Это подтверждение устарело. Выберите продукт заново")
        return
    text = context.get("text")
    now_time = context.get("now_time")
    print(context)
    await send_to_admin(callback, text, now_time)

async def shop_supercell_products_final_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("shop_supercell_brawl_gems_"):
        game = "brawl"
    elif callback.data.startswith("shop_supercell_clash_gems_"):
        game = "clash"
    else:
        game = "clans"

    now_time, confirma = await check_time(callback)
    if confirma:
        # Создаем клавиатуру подтверждения и "Назад"
        kb = InlineKeyboardBuilder()
        kb.button(text="Подтвердить", callback_data="confirm_buy")
        kb.button(text="Назад", callback_data="shop_back_supercell")
        kb.adjust(2)

        id_product = callback.data[len(f"shop_supercell_{game}_gems_"):]
        data_nah = (await system_base.get_value(f'products_supercell_{game}', {'id': id_product}))[0]
        text = f"{game} {data_nah['label']} = {data_nah['price']}, руб."
        await state.update_data(id_product=id_product, data_nah=data_nah, text=text, now_time=now_time, confirm=confirm)

        await callback.message.edit_caption(
            caption=f"{data_nah['label']} = {data_nah['price']}, руб.\n\n"
            "Нажмите кнопку <b>Подтвердить</b>, чтобы завершить покупку.",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ShopStates.confirm_buy)

        await system_base.update_last_msg_time(callback.from_user.id, now_time.strftime('%Y-%m-%d %H:%M:%S'))
    await callback.answer()

def register_supercell_handlers(dp: Dispatcher):
    dp.message.register(shop_supercell, F.text.lower() == "магазин supercell 🎮")
    dp.callback_query.register(shop_supercell_products_callback, F.data == "shop_supercell_brawl_gems")
    dp.callback_query.register(shop_supercell_products_callback, F.data == "shop_supercell_clash_gems")
    dp.callback_query.register(shop_supercell_products_callback, F.data == "shop_supercell_clans_gems")

    dp.callback_query.register(shop_supercell_products_final_callback, F.data.startswith("shop_supercell_brawl_gems_"))
    dp.callback_query.register(shop_supercell_products_final_callback, F.data.startswith("shop_supercell_clash_gems_"))
    dp.callback_query.register(shop_supercell_products_final_callback, F.data.startswith("shop_supercell_clans_gems_"))
    # Обработка кнопки "Назад"
    dp.callback_query.register(shop_supercell_back, F.data == "shop_back_supercell")
    dp.callback_query.register(confirm, F.data == "confirm_buy")