from .all_modules import *

ShopStates = ShopStatesTelegram

async def shop_telegram_ton_pay(callback: types.CallbackQuery, state: FSMContext):
    _, confirm = await check_time(callback.message)
    if confirm:
        msg = await callback.message.edit_caption(
            caption="""💎 Выберите способ получения:\n\n❗️ При покупке на внутренний кошелёк монеты будут отправлены на ваш аккаунт, этот способ нужен, если вы покупаете рекламу или подарки на маркете Telegram.""",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Покупка на внутренний кошелёк Telegram",
                            callback_data="shop_telegram_ton_wallet"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="Покупка на внешний кошелек",
                            callback_data="shop_telegram_ton_address"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="Назад",
                            callback_data="back_ton_start"
                        )
                    ],
                ]
            )
        )

        await state.update_data(ton_pay=msg)

async def choose_ton_wallet(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "shop_telegram_ton_wallet":
        t = "на свой внутренний кошелек Telegram!"
    else:
        t = "на внешний кошелек!"
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_ton_confirm")
    kb.adjust(1)
    m = await callback.message.edit_caption(
        caption=f"Введите количество TON, которое хотите купить {t}",
        reply_markup=kb.as_markup()
    )

    await callback.answer()
    await state.update_data(msg_count_ton=m, wallet=t) # сообщение, которое надо поменять; кошелёк
    await state.set_state(ShopStates.start_ton_buy)

async def process_ton_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_count_ton = data.get("msg_count_ton") # введите количество ton...
    wallet = data.get("wallet") # на свой...
    try:
        if message.content_type == types.ContentType.TEXT and message.text.isdigit():
            quantity = float(message.text)
            await message.delete()
            price_data = await system_base.get_value('price_ton')
            if not price_data:
                await message.answer("Стоимость TON не найдена.")
                return
            price_per_ton = price_data[0]['price']
            total_price = math.floor(price_per_ton * quantity)
            await state.update_data(quantity=quantity, total_price=total_price)

            kb = InlineKeyboardBuilder()
            kb.button(text="Подтвердить", callback_data="confirm_ton")
            kb.button(text="Назад", callback_data="back_ton_confirm")
            kb.adjust(2)
            dest_text = f"{quantity} TON за {total_price} руб. {wallet}"
            msg_confirm_ton = await message.bot.edit_message_caption(
                chat_id=msg_count_ton.chat.id,
                message_id=msg_count_ton.message_id,
                caption=f"Вы собираетесь купить {dest_text}\n"
                f"Нажмите кнопку <b>Подтвердить</b>, чтобы завершить покупку.\n\n",
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )

            await state.update_data(msg_confirm_ton=msg_confirm_ton, msg_count_ton=msg_count_ton, dest_text=dest_text, )
            await state.set_state(ShopStates.confirm_ton_buy)
        else:
            await message.delete()
            m = await message.answer("Пожалуйста, введите число.")
            await asyncio.sleep(1)
            await message.bot.delete_message(
                chat_id=m.chat.id,
                message_id=m.message_id
            )
    except Exception as e:
        await message.answer(f"Ошибка при обработке: {e}")


async def confirm_ton_buy(callback: types.CallbackQuery, state: FSMContext):
    _, confirm = await check_time(callback)
    data = await state.get_data()
    dest_text = data.get("dest_text")
    print(data.items())

    if confirm:
        now_time = datetime.utcnow() + timedelta(hours=3)
        await send_to_admin(callback, dest_text, now_time)

        await system_base.update_last_msg_time(callback.from_user.id, now_time.strftime('%Y-%m-%d %H:%M:%S'))
    await callback.answer()
    await state.clear()

def register_telegram_handlers_ton(dp: Dispatcher):
    dp.callback_query.register(shop_telegram_ton_pay, F.data == "shop_telegram_ton_pay")
    dp.callback_query.register(choose_ton_wallet, F.data == "shop_telegram_ton_wallet")
    dp.callback_query.register(choose_ton_wallet, F.data == "shop_telegram_ton_address")
    dp.message.register(process_ton_payment, StateFilter(ShopStates.start_ton_buy))
    dp.callback_query.register(confirm_ton_buy, F.data == "confirm_ton")