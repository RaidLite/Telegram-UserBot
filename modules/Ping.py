from time import perf_counter

from telethon import events


def a(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_command_handler(event):
        start = perf_counter()
        await event.edit("Понг!")
        end = perf_counter()
        ping_time = round((end - start) * 1000, 2)
        await event.edit(f"Пинг: {ping_time} мс")
