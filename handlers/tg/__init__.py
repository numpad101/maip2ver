import asyncio

from aiogram import Dispatcher, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import math

from aiogram.utils.keyboard import InlineKeyboardBuilder

import system_base
from handlers.core_funcs import check_time, send_to_admin