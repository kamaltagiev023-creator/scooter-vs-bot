
import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")

SCOOTERS = {
    "xiaomi": {
        "name": "Xiaomi Electric Scooter 4 Pro",
        "power": 700,
        "speed": 25,
        "range": 55,
        "pros": "Хороший запас хода, удобный городской формат",
        "cons": "Тяжёлый, реальный пробег зависит от условий",
    },
    "ninebot": {
        "name": "Segway Ninebot MAX G2",
        "power": 450,
        "speed": 25,
        "range": 70,
        "pros": "Комфортная подвеска, большой заявленный запас хода",
        "cons": "Тяжёлый и обычно дорогой",
    },
    "kugoo": {
        "name": "Kugoo Kirin G2 Pro",
        "power": 600,
        "speed": 45,
        "range": 55,
        "pros": "Мощный мотор, динамичный разгон",
        "cons": "Тяжёлый; характеристики зависят от версии и рынка",
    },
    "inokim": {
        "name": "Inokim OXO",
        "power": 2600,
        "speed": 65,
        "range": 110,
        "pros": "Высокая мощность, подвеска, большой запас хода",
        "cons": "Высокая цена, большой вес",
    },
}


def bar(value, maximum, width=12):
    filled = max(0, min(width, round(value / maximum * width)))
    return "█" * filled + "░" * (width - filled)


def card(s):
    return (
        f"🛴 <b>{s['name']}</b>\n\n"
        f"⚡ Мощность: <b>{s['power']} Вт</b>\n"
        f"{bar(s['power'], 2600)}\n"
        f"💨 Скорость: <b>{s['speed']} км/ч</b>\n"
        f"{bar(s['speed'], 65)}\n"
        f"🔋 Заявленный запас хода: <b>{s['range']} км</b>\n"
        f"{bar(s['range'], 110)}\n\n"
        f"✅ Плюсы: {s['pros']}\n"
        f"⚠️ Минусы: {s['cons']}\n"
    )


def menu():
    kb = InlineKeyboardBuilder()
    for key, s in SCOOTERS.items():
        kb.button(text=s["name"], callback_data=f"info:{key}")
    kb.button(text="⚔️ Сравнить два самоката", callback_data="compare_menu")
    kb.adjust(1)
    return kb.as_markup()


def compare_menu():
    kb = InlineKeyboardBuilder()
    keys = list(SCOOTERS.keys())
    for a in keys:
        for b in keys:
            if a < b:
                kb.button(
                    text=f"{SCOOTERS[a]['name'].split()[0]} vs "
                         f"{SCOOTERS[b]['name'].split()[0]}",
                    callback_data=f"compare:{a}:{b}",
                )
    kb.adjust(1)
    return kb.as_markup()


async def main():
    if not TOKEN:
        raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

    bot = Bot(TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message):
        await message.answer(
            "🏁 <b>Scooter VS</b>\n"
            "Сравнивай электросамокаты по мощности, скорости "
            "и запасу хода.\n\n"
            "Команды:\n"
            "/list — каталог\n"
            "/compare — сравнение моделей\n\n"
            "Выбери самокат:",
            reply_markup=menu(),
        )

    @dp.message(Command("list"))
    async def list_scooters(message: Message):
        await message.answer("🛴 <b>Каталог самокатов</b>", reply_markup=menu())

    @dp.message(Command("compare"))
    async def compare(message: Message):
        await message.answer(
            "Выбери пару для сравнения:",
            reply_markup=compare_menu(),
        )

    @dp.callback_query(F.data == "compare_menu")
    async def show_compare_menu(call: CallbackQuery):
        await call.message.answer(
            "⚔️ Выбери пару для сравнения:",
            reply_markup=compare_menu(),
        )
        await call.answer()

    @dp.callback_query(F.data.startswith("info:"))
    async def show_info(call: CallbackQuery):
        key = call.data.split(":")[1]
        await call.message.answer(card(SCOOTERS[key]), parse_mode="HTML")
        await call.answer()

    @dp.callback_query(F.data.startswith("compare:"))
    async def show_comparison(call: CallbackQuery):
        _, a, b = call.data.split(":")
        first, second = SCOOTERS[a], SCOOTERS[b]

        def winner(x, y, field):
            if x[field] == y[field]:
                return "Ничья"
            return x["name"] if x[field] > y[field] else y["name"]

        text = (
            "⚔️ <b>СРАВНЕНИЕ САМОКАТОВ</b>\n\n"
            f"🛴 <b>{first['name']}</b>\n"
            f"⚡ {first['power']} Вт  {bar(first['power'], 2600)}\n"
            f"💨 {first['speed']} км/ч  {bar(first['speed'], 65)}\n"
            f"🔋 {first['range']} км  {bar(first['range'], 110)}\n\n"
            f"🛴 <b>{second['name']}</b>\n"
            f"⚡ {second['power']} Вт  {bar(second['power'], 2600)}\n"
            f"💨 {second['speed']} км/ч  {bar(second['speed'], 65)}\n"
            f"🔋 {second['range']} км  {bar(second['range'], 110)}\n\n"
            "🏆 <b>По характеристикам:</b>\n"
            f"Мощность: {winner(first, second, 'power')}\n"
            f"Скорость: {winner(first, second, 'speed')}\n"
            f"Запас хода: {winner(first, second, 'range')}\n\n"
            f"✅ Плюсы {first['name']}: {first['pros']}\n"
            f"⚠️ Минусы: {first['cons']}\n\n"
            f"✅ Плюсы {second['name']}: {second['pros']}\n"
            f"⚠️ Минусы: {second['cons']}\n\n"
            "ℹ️ Данные ориентировочные: характеристики зависят от версии, "
            "рынка и условий. Победа по цифрам не означает, что модель лучше "
            "для каждого человека."
        )
        await call.message.answer(text, parse_mode="HTML")
        await call.answer()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
