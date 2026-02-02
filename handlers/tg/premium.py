from .all_modules import *

ShopStates = ShopStatesTelegram


async def shop_telegram_tg_prem(callback: types.CallbackQuery, state: FSMContext):
    table_prem = await system_base.get_value('products_tg_prem')
    if not table_prem:
        await callback.message.edit_text("Здесь пока пусто")
        return

    kb = [
        [
            types.InlineKeyboardButton(
                text=f"{item['label']} = {item['price']}, руб.",
                callback_data=f"shop_telegram_prem_buy_{item['id']}"
            )
        ] for item in table_prem
    ]
    back = types.InlineKeyboardButton(
        text="Назад",
        callback_data="back_prem_start"
    )
    kb.append([back])
    msg_prem = await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption="Выберите срок *Telegram Premium*",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )

    await state.update_data(msg_prem=msg_prem)


async def confirm_prem_buy(callback: types.CallbackQuery, state: FSMContext):
    context = await state.get_data()
    if context == {}:
        await callback.message.answer("Это подтверждение устарело. Выберите продукт заново")
        return
    text = context.get("text")
    now_time =context.get("now_time")
    await send_to_admin(callback, text, now_time)

async def shop_telegram_tg_prem_buy_click(callback: types.CallbackQuery, state: FSMContext):
    now_time, confirm = await check_time(callback)

    if confirm:
        kb = InlineKeyboardBuilder()
        kb.button(text="Подтвердить", callback_data="confirm_prem_buy")
        kb.button(text="Назад", callback_data="back_prem_confirm")
        kb.adjust(2)

        product_id = callback.data.split("_")[-1]
        product_data = (await system_base.get_value('products_tg_prem', {'id': product_id}))[0]
        text = f"Telegram Premium на {product_data['label']} = {product_data['price']}, руб."

        msg = await callback.message.edit_caption(
            caption=f"{product_data['label']} = {product_data['price']}, руб.\n\n"
            "Нажмите кнопку <b>Подтвердить</b>, чтобы завершить покупку.",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        await state.update_data(id_product=product_id, data_nah=product_data, text=text, now_time=now_time, confirm=confirm, msg_confirm_prem=msg)
        await system_base.update_last_msg_time(callback.from_user.id, now_time.strftime('%Y-%m-%d %H:%M:%S'))
        await state.set_state(ShopStates.confirm_prem_buy)

    await callback.answer()

def register_telegram_handlers_premium(dp: Dispatcher):
    dp.callback_query.register(shop_telegram_tg_prem, F.data == "shop_telegram_premium")
    dp.callback_query.register(shop_telegram_tg_prem_buy_click, F.data.startswith("shop_telegram_prem_buy_"))
    dp.callback_query.register(confirm_prem_buy, F.data == "confirm_prem_buy")