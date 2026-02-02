from .tg.all_modules import *

ShopStates = ShopStatesTelegram

# Основная функция открытия магазина Telegram
async def shop_telegram(message: types.Message):
    admins = await system_base.get_admins()
    if message.from_user.id not in admins:
        keyboard = get_keyboard_tg()
        await message.delete()
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=types.FSInputFile("images/price_telegram_shop.JPG"),
            caption="Выберите интересующий вас товар снизу 👇\n💫 Любой товар можно отправить другу по юзернейму или кошельку!",
            reply_markup=keyboard,
        )


def get_keyboard_tg():
    return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Telegram Stars (Звёзды) ⭐️",
                        callback_data="shop_telegram_trade"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Telegram Premium 💎",
                        callback_data="shop_telegram_premium"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="TON 💎",
                        callback_data="shop_telegram_ton_pay"
                    )
                ],
            ]
        )

async def back(attr: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(attr, types.Message):
        message: types.Message = attr
        pass
    elif isinstance(attr, types.CallbackQuery):
        callback: types.CallbackQuery = attr
        msg = callback.message
        if callback.data == "back_stars" or callback.data == "back_prem_start" or callback.data == "back_ton_start":
            await callback.bot.edit_message_caption(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                caption="Выберите интересующий вас товар снизу 👇\n💫 Любой товар можно отправить другу по юзернейму или кошельку!",
                reply_markup=get_keyboard_tg()
            )
        elif callback.data == "back_prem_confirm":
            await shop_telegram_tg_prem(callback, state)
        elif callback.data == "back_ton_confirm":
            await shop_telegram_ton_pay(callback, state)

    await state.clear()

# Регистрация хендлеров
"""
back_stars READY
back_prem_start READY
back_prem_confirm READY
back_ton_start READY
back_ton_confirm
"""
def register_telegram_handlers(dp: Dispatcher):
    dp.message.register(shop_telegram, F.text.lower() == "магазин telegram 🌟")
    dp.callback_query.register(back, F.data == "back_stars")
    dp.callback_query.register(back, F.data == "back_prem_start")
    dp.callback_query.register(back, F.data == "back_prem_confirm")
    dp.callback_query.register(back, F.data == "back_ton_start")
    dp.callback_query.register(back, F.data == "back_ton_confirm")

    register_telegram_handlers_stars(dp)
    register_telegram_handlers_premium(dp)
    register_telegram_handlers_ton(dp)
