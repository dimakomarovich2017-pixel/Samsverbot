# -*- coding: utf-8 -*-

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

# 🔑 Вставь сюда токен от @BotFather
BOT_TOKEN = "8935066906:AAEebbUeQ-tAoqzriQVHHik3mvbTtm3z3ck"

RATE_HOUR = 108
RATE_SLA15 = 36
RATE_SLA30 = 49.5

logging.basicConfig(level=logging.INFO)


def fmt(num: float) -> str:
    if num == int(num):
        return f"{int(num):,}".replace(",", " ")
    else:
        return f"{num:,.1f}".replace(",", " ").replace(".", ",")


def parse_number(raw: str):
    raw = raw.strip().replace(",", ".")
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class Form(StatesGroup):
    hours = State()
    sla15 = State()
    sla30 = State()
    bonus = State()


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я считаю сверку итогов.\n\n"
        "Отправь значение часов (например: 57)."
    )
    await state.set_state(Form.hours)


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменил. Напиши /start, чтобы начать заново.")


@dp.message(Form.hours, F.text)
async def get_hours(message: Message, state: FSMContext):
    val = parse_number(message.text)
    if val is None:
        await message.answer("⚠️ Введи число, например: 57")
        return
    await state.update_data(hours=val)
    await message.answer("✅ Часы приняты.\n\nТеперь значение SLA 15:")
    await state.set_state(Form.sla15)


@dp.message(Form.sla15, F.text)
async def get_sla15(message: Message, state: FSMContext):
    val = parse_number(message.text)
    if val is None:
        await message.answer("⚠️ Введи число, например: 144")
        return
    await state.update_data(sla15=val)
    await message.answer("✅ SLA 15 принят.\n\nТеперь значение SLA 30:")
    await state.set_state(Form.sla30)


@dp.message(Form.sla30, F.text)
async def get_sla30(message: Message, state: FSMContext):
    val = parse_number(message.text)
    if val is None:
        await message.answer("⚠️ Введи число, например: 5")
        return
    await state.update_data(sla30=val)
    await message.answer("✅ SLA 30 принят.\n\nТеперь сумма надбавок в ₽ (если нет — отправь 0):")
    await state.set_state(Form.bonus)


@dp.message(Form.bonus, F.text)
async def get_bonus(message: Message, state: FSMContext):
    val = parse_number(message.text)
    if val is None:
        await message.answer("⚠️ Введи число, например: 8050")
        return

    data = await state.get_data()
    hours = data["hours"]
    sla15 = data["sla15"]
    sla30 = data["sla30"]
    bonus = val

    hours_sum = hours * RATE_HOUR
    sla15_sum = sla15 * RATE_SLA15
    sla30_sum = sla30 * RATE_SLA30
    total = hours_sum + sla15_sum + sla30_sum + bonus

    text = (
        "📋 СВЕРКА ИТОГОВ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🕒 Часы: {fmt(hours)}\n"
        f"✅ SLA 15: {fmt(sla15)}\n"
        f"✅ SLA 30: {fmt(sla30)}\n"
        f"💰 Надбавки: {fmt(bonus)}₽\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💵 ИТОГО: {fmt(total)}₽\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📌 Расценки:\n"
        f"• 1 час = {fmt(RATE_HOUR)}₽\n"
        f"• 1 SLA 15 = {fmt(RATE_SLA15)}₽\n"
        f"• 1 SLA 30 = {fmt(RATE_SLA30)}₽\n"
        "🧮 Подсчёты:\n"
        f"• {fmt(hours)} × {fmt(RATE_HOUR)}₽ = {fmt(hours_sum)}₽\n"
        f"• {fmt(sla15)} × {fmt(RATE_SLA15)}₽ = {fmt(sla15_sum)}₽\n"
        f"• {fmt(sla30)} × {fmt(RATE_SLA30)}₽ = {fmt(sla30_sum)}₽\n"
        f"• Надбавки = {fmt(bonus)}₽\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Итого: {fmt(hours_sum)} + {fmt(sla15_sum)} + {fmt(sla30_sum)} + {fmt(bonus)} = {fmt(total)}₽\n\n"
        "Чтобы посчитать ещё раз — /start"
    )

    await message.answer(text)
    await state.clear()


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
