import logging
import random
from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import Command
from datetime import datetime, timedelta
import json
import os

# Вставьте ваш токен сюда
API_TOKEN = '7456520482:AAHo_2ktNS_FjaSBN-2ejS_IsKzgjLkk3WQ'

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STORAGE_FILE = 'sol_storage.json'


def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {"total_sol": 0.0, "max_sol": random.uniform(20, 27), "last_reset": datetime.now().strftime('%Y-%m-%d'),
            "daily_sol": 0.0, "users": [941825672]}


def save_storage(storage):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(storage, f)


async def reset_monthly_limit():
    while True:
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        next_year = now.year if now.month < 12 else now.year + 1
        reset_time = datetime(next_year, next_month, 1)
        wait_time = (reset_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        storage = load_storage()
        storage["total_sol"] = 0.0
        storage["max_sol"] = random.uniform(20, 27)
        storage["last_reset"] = datetime.now().strftime('%Y-%m-%d')
        save_storage(storage)


def generate_sol_list(S, N):
    # Генерируем начальные случайные числа
    sol_list = [random.random() for _ in range(N)]

    # Нормализуем их сумму до 1
    total_sum = sum(sol_list)
    sol_list = [x / total_sum for x in sol_list]

    # Пропорционально изменяем числа, чтобы их сумма была равна S
    sol_list = [x * S for x in sol_list]

    return sol_list


async def send_sol_messages():
    while True:
        num_messages = random.randint(8, 50)  # случайное количество сообщений в день
        daily_sol_limit = random.uniform(0.4, 1)  # случайная сумма SOL в день

        random_times = sorted(random.sample(range(86400), num_messages))  # случайные временные отметки в течение дня
        storage = load_storage()
        if storage["total_sol"] >= storage["max_sol"]:
            continue  # лимит за месяц исчерпан

        print(num_messages)
        total_sol = 0
        messages = []

        sol_list = generate_sol_list(daily_sol_limit, num_messages)
        for s in sol_list:
            sol_amount = s
            total_sol += sol_amount
            storage["total_sol"] += sol_amount
            storage["daily_sol"] += sol_amount
            messages.append(f'+{sol_amount:.5f} SOL\nToday: {storage["daily_sol"]:.5f} SOL')

        #
        # for _ in range(num_messages):
        #     if total_sol >= daily_sol_limit or storage["total_sol"] >= storage["max_sol"]:
        #         break
        #     sol_amount = round(random.uniform(0.00001, 0.1), 5)
        #     if total_sol + sol_amount > daily_sol_limit or storage["total_sol"] + sol_amount > storage["max_sol"]:
        #         break
        #     total_sol += sol_amount
        #     storage["total_sol"] += sol_amount
        #     storage["daily_sol"] += sol_amount
        #     messages.append(f'+{sol_amount:.5f} SOL\nToday: {storage["daily_sol"]:.5f} SOL')

        print(messages)
        print(len(messages))
        save_storage(storage)

        for i, msg in enumerate(messages):
            for user_id in storage["users"]:
                await asyncio.sleep(random_times[i] - (random_times[i - 1] if i > 0 else 0))
                await bot.send_message(chat_id=user_id, text=msg)

        now = datetime.now()
        new_day = False
        while new_day is False:
            if now.hour == 0 and now.minute == 0:
                storage["daily_sol"] = 0
                new_day = True


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    storage = load_storage()
    if message.from_user.id not in storage["users"]:
        storage["users"].append(message.from_user.id)
        save_storage(storage)
    await message.reply("Successfully access")


async def start_sending_messages():
    await asyncio.gather(send_sol_messages())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(reset_monthly_limit())
    loop.create_task(start_sending_messages())
    loop.run_until_complete(dp.start_polling(bot))
