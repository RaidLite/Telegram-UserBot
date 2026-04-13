from asyncio import sleep

from telethon import events

SEARCHING = "⚠️ Поиск по базам данных {}/50..."
DEANON_RESULT = (
    'Имя найдено, но не найдено крч\n'
    'Мама: не найдено\n'
    'Папа: чучут найдена\n'
    'Бабушка: найден прах\n'
    'Дед: похуй умер\n'
    'Размер хуя: карнишон\n'
    'Анальное отверстие: пробито\n'
    'Цвет простаты: березовый\n'
    'Цвет говна: красный\n'
    'Ебло: ахуевшее\n'
    'Страна: залупинск\n'
    'Оператор: пидор2\n'
    'Дом: там который\n'
    'Место проживание: земля\n'
    'Номер: +888888888\n'
    'Адрес: деаноновно 1/2\n'
    'Простата: масирована\n\n'
    'Жду извинений 😈😈😈'
)

def init(client):
    @client.on(events.NewMessage(pattern=r"\.deanon", outgoing=True))
    async def _(event):
        for i in range(1, 51):
            await event.edit(SEARCHING.format(i))
            await sleep(0.2)

        await event.edit(DEANON_RESULT)