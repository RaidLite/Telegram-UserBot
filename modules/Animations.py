import random
from asyncio import sleep

from telethon import events

mask = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]


def a(client):
    async def create_heart_pattern(arr, h):
        a = arr[0]
        char_map = {0: h, 1: a}
        lines = ["".join(char_map[cell] for cell in row) for row in mask]

        return "\n".join(lines)

    async def edit_pattern(message, arr, h, sleep_time=0.3):
        for i in arr:
            char_map = {0: h, 1: i}
            lines = ["".join(char_map[cell] for cell in row) for row in mask]
            heart = "\n".join(lines)

            await message.edit(heart)
            await sleep(sleep_time)

    async def random_pattern(message, arr, h, sleep_time=0.3):
        for _ in range(8):
            rand = random.choices(arr, k=34)
            rand_iter = iter(rand)

            lines = []
            for row in mask:
                line = ""
                for cell in row:
                    if cell == 0:
                        line += h
                    else:
                        line += next(rand_iter)
                lines.append(line)

            await message.edit("\n".join(lines))
            await sleep(sleep_time)

    async def final_pattern(message, arr, h, heart_emoji, times=47, sleep_time=0.1):
        fourth = await create_heart_pattern(arr, h)
        await message.edit(fourth)
        for _ in range(times):
            fourth = fourth.replace("⬜️", arr[0], 1)
            await message.edit(fourth)
            await sleep(sleep_time)
        for i in range(8):
            await message.edit((arr[0] * (8 - i) + "\n") * (8 - i))
            await sleep(0.4)
        for i in [
            "I", f"I {heart_emoji} U",
            f"I {heart_emoji} U!",
            f"i {heart_emoji} U",
            f"I {heart_emoji} u",
            f"I {heart_emoji} U"
        ]:
            await message.edit(f"<b>{i}</b>", parse_mode='html')
            await sleep(0.5)

    @client.on(events.NewMessage(pattern=r"\.love", outgoing=True))
    async def watcher_lvR(event):
        message = event
        if message.sender_id == (await message.client.get_me()).id:
            arr = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛️"]
            h = "⬜️"
            first = ""
            for i in "".join(
                    [h * 9, "\n", h * 2, arr[0] * 2, h, arr[0] * 2, h * 2, "\n", h, arr[0] * 7, h, "\n", h, arr[0] * 7,
                     h, "\n", h, arr[0] * 7, h, "\n", h * 2, arr[0] * 5, h * 2, "\n", h * 3, arr[0] * 3, h * 3, "\n",
                     h * 4, arr[0], h * 4]).split("\n"):
                first += i + "\n"
                await message.edit(first)
                await sleep(0.2)
            await edit_pattern(message, arr, h)
            await random_pattern(message, arr, h)
            await final_pattern(message, arr, h, "❤️")
