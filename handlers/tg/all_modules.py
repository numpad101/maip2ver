import asyncio, math, system_base

from aiogram import Dispatcher, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.core_funcs import check_time, send_to_admin, ShopStatesTelegram

from .ton import register_telegram_handlers_ton, shop_telegram_ton_pay
from .stars import register_telegram_handlers_stars
from .premium import register_telegram_handlers_premium, shop_telegram_tg_prem