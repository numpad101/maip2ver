from .all_modules import *

ShopStates = ShopStatesTelegram


async def start_trade_stars_buy(callback: types.CallbackQuery, state: FSMContext):
    await check_time(callback.message)
    await state.set_state(ShopStates.start_trade_stars_buy)
    msg = callback.message
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_stars")
    kb.adjust(1)
    msg = await msg.edit_caption(
        caption="🔢 Введите количество звёзд, которое хотите купить!",
        reply_markup=kb.as_markup()
    )
    await state.update_data(message_start_trade_stars=msg)

async def shop_telegram_trade_stars_buy(message: types.Message, state: FSMContext):
    try:
        _, confirm = await check_time(message)
        if not confirm:
            await state.clear()
            return

        if message.content_type == types.ContentType.TEXT and message.text.isdigit():
            quantity = int(message.text)
            if quantity < 50:
                m = await message.answer("Минимальное количество звёзд для покупки: 50! Введите повторно.")
                await message.delete()
                await asyncio.sleep(1)
                await message.bot.delete_message(
                    chat_id=m.chat.id,
                    message_id=m.message_id
                )
                return

            price_data = (await system_base.get_value('products_tg_trade'))[0]
            price_per_star = price_data["price_default"]
            if quantity >= 500:
                price_per_star = price_data["price_500plus"]
            total_price = math.floor(price_per_star * quantity)

            # Обновляем данные состояния
            await state.update_data(quantity=quantity, total_price=total_price)

            # Строим обновлённое сообщение
            new_text = (
                f"Вы собираетесь купить {quantity} ⭐️ за {total_price} руб.\n"
                f"Нажмите кнопку <b>Подтвердить</b>, чтобы завершить покупку.\n\n"
                f"❗️ После подтверждения покупки администратор получит уведомление о том, что вы готовы сделать заказ"
            )
            # Редактируем исходное сообщение
            message_start_trade_stars = (await state.get_data()).get("message_start_trade_stars")  # введите количество звёзд...
            await message.delete()

            kb = InlineKeyboardBuilder()
            kb.button(text="Подтвердить", callback_data="confirm_trade")
            kb.button(text="Отменить", callback_data="back_stars")
            kb.adjust(2)
            msg_confirm_stars = await message_start_trade_stars.edit_caption(
                caption=new_text,
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )
            await state.update_data(msg_confirm_stars=msg_confirm_stars, message_start_trade_stars=message_start_trade_stars)
        else:
            await message.delete()
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def confirm_trade_stars_buy(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get("quantity")
    total_price = data.get("total_price")
    text = f"{quantity} ⭐️ за {total_price} руб."
    if not all([quantity, total_price]):
        await callback.answer("Нет данных по покупке. Попробуйте заново.", show_alert=True)
        await state.clear()
        return

    now_time = datetime.utcnow() + timedelta(hours=3)
    await send_to_admin(callback, text, now_time)
    await system_base.update_last_msg_time(callback.from_user.id, now_time.strftime('%Y-%m-%d %H:%M:%S'))

    await callback.answer()
    await state.clear()

def register_telegram_handlers_stars(dp: Dispatcher):
    dp.callback_query.register(start_trade_stars_buy, F.data == "shop_telegram_trade")
    dp.message.register(shop_telegram_trade_stars_buy, StateFilter(ShopStates.start_trade_stars_buy))
    dp.callback_query.register(confirm_trade_stars_buy, F.data == "confirm_trade")