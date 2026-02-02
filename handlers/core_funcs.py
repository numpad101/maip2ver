from datetime import timedelta, datetime


from aiogram.types import CallbackQuery, Message
import config
import system_base
from config import DEBUG
from aiogram.fsm.state import State, StatesGroup

class ShopStatesTelegram(StatesGroup):
    start_trade_stars_buy = State()
    start_ton_buy = State()
    confirm_ton_buy = State()
    confirm_prem_buy = State()


async def check_time(attr):
    # type(attr) = Message or CallbackQuery
    last_time_str = await system_base.get_last_msg_time(attr.from_user.id)
    if last_time_str:
        last_msg_time = datetime.strptime(last_time_str, '%Y-%m-%d %H:%M:%S')
    else:
        last_msg_time = None

    if isinstance(attr, CallbackQuery):
        now_time = datetime.strptime((attr.message.date + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                                     '%Y-%m-%d %H:%M:%S')
    elif isinstance(attr, Message):
        now_time = datetime.strptime((attr.date + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                                     '%Y-%m-%d %H:%M:%S')
    else:
        now_time = datetime.utcnow()

    confirm = True
    if not DEBUG:
        huy = datetime.now() + timedelta(hours=3)
    else: huy = datetime.now()

    if last_msg_time is None:
        delta = timedelta(seconds=config.COOLDOWN) - timedelta(seconds=config.COOLDOWN)
    else:
        delta = timedelta(seconds=config.COOLDOWN) - (huy - last_msg_time)
    total_seconds = int(delta.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    print(f"{delta=}; {total_seconds=}; {minutes=}; {seconds=}")

    if last_msg_time and (huy - last_msg_time) <= timedelta(seconds=config.COOLDOWN):
        if isinstance(attr, CallbackQuery):
            await attr.message.answer(f"Вы уже отправляли сообщение недавно. Осталось {minutes} мин. {seconds} сек.")
        elif isinstance(attr, Message):
            await attr.answer(f"Вы уже отправляли сообщение недавно. Осталось {minutes} мин. {seconds} сек.")
        confirm = False

    return now_time, confirm

async def send_to_admin(attr, text, now_time):
    # type(attr) = Message or CallbackQuery
    admins = await system_base.get_admins()
    for id in admins:
        await attr.bot.send_message(id, f"***УВЕДОМЛЕНИЕ***\n"
                                            f"ID: {attr.from_user.id}\n"
                                            f"Ник: @{attr.from_user.username}\n"
                                            f"Продукт: {text}\n"
                                            f"Время: {now_time}")
    if type(attr) is CallbackQuery:
        text: str = text.replace("clash", "").replace("brawl", "")
        try:
            await attr.message.edit_text(
                f"""
                Уведомление администраторам пришло! Напиши мне в лс, если готов сделать заказ — @MaipMaip\n
            <blockquote>Вы купили {text}</blockquote>
                """,
                parse_mode="HTML"
            )
        except Exception as e:
            print(e)
            print("ASD")
            await attr.message.edit_caption(
                caption=f"""
                Уведомление администраторам пришло! Напиши мне в лс, если готов сделать заказ — @MaipMaip\n
            <blockquote>Вы купили {text}</blockquote>
                """,
                parse_mode="HTML"
            )
    elif type(attr) is Message:
        await attr.answer("Вы уже отправляли сообщение недавно. Подождите немного.")