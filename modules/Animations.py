from random import choices
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


def init(client):
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
            rand = choices(arr, k=34)
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
    async def watcher_love(event):
        message = event
        if message.sender_id == (await message.client.get_me()).id:
            colors = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛️"]
            white = "⬜️"
            first = ""
            for i in "".join(
                    [
                     white * 9, "\n", white * 2,
                        colors[0] * 2, white,
                        colors[0] * 2, white * 2, "\n", white,
                        colors[0] * 7, white, "\n", white,
                        colors[0] * 7,
                     white, "\n",
                        white, colors[0] * 7,
                        white, "\n",
                        white * 2, colors[0] * 5,
                        white * 2, "\n",
                        white * 3, colors[0] * 3,
                        white * 3, "\n",
                     white * 4, colors[0],
                        white * 4
                    ]
            ).split("\n"):
                first += i + "\n"
                await message.edit(first)
                await sleep(0.2)
            await edit_pattern(message, colors, white)
            await random_pattern(message, colors, white)
            await final_pattern(message, colors, white, "❤️")