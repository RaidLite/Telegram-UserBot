from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest, UpdateStatusRequest

bold_mode = False
BOLD_ON_CMD = ".bold on"
BOLD_OFF_CMD = ".bold off"
BOLD_TAG = "\u200B"
shift_mode = False
SHIFT_ON_CMD = ".shrift on"
SHIFT_OFF_CMD = ".shrift off"
MAP = {
    "а": "ᴀ", "б": "ʙ", "в": "ᴠ", "г": "ɢ", "д": "ᴅ", "е": "ᴇ", "ё": "ё", "ж": "ᴢʜ",
    "з": "ᴢ", "и": "ɪ", "й": "ᴊ", "к": "ᴋ", "л": "ʟ", "м": "ᴍ", "н": "ɴ", "о": "ᴏ",
    "п": "ᴘ", "р": "ʀ", "с": "s", "т": "ᴛ", "у": "ᴜ", "ф": "ғ", "х": "ʜ", "ц": "ᴛs",
    "ч": "ᴄʜ", "ш": "sʜ", "щ": "sᴄʜ", "ъ": "ъ", "ы": "ʏ", "ь": "ь", "э": "ᴇ",
    "ю": "ʏᴜ", "я": "ʏᴀ"
}


def a(client):
    global bold_mode

    @client.on(events.NewMessage(outgoing=True, pattern='.afk'))
    async def afk(event):
        if event.fwd_from:
            return
        await event.delete()
        me = await event.client.get_me()
        first_name = me.first_name
        second_name = me.last_name
        if 'AFK ' not in first_name:
            first_name = f'AFK {first_name}'
            await client(UpdateProfileRequest(
                first_name=first_name,
                last_name=second_name
            ))
            await client(UpdateStatusRequest(offline=True))
        else:
            first_name = first_name.replace('AFK ', '')
            await client(UpdateProfileRequest(
                first_name=first_name,
                last_name=second_name
            ))
            await client(UpdateStatusRequest(offline=False))

    @client.on(events.NewMessage(outgoing=True))
    async def bold_toggle_and_auto(event):
        global bold_mode
        message = event.raw_text.strip()

        if message in (BOLD_ON_CMD, BOLD_OFF_CMD):
            bold_mode = message == BOLD_ON_CMD
            await event.delete()
            return

        if message.startswith('.'):
            return

        if bold_mode and BOLD_TAG not in message:
            await event.delete()
            await event.respond(
                f"**{message}**{BOLD_TAG}",
                parse_mode='markdown',
                reply_to=event.reply_to_msg_id
            )

    @client.on(events.NewMessage(outgoing=True))
    async def shrift_toggle_and_auto(event):
        global shift_mode
        text = event.raw_text.strip()

        if text in (SHIFT_ON_CMD, SHIFT_OFF_CMD):
            shift_mode = text == SHIFT_ON_CMD
            await event.delete()
            return

        if not shift_mode or text.startswith(".") or BOLD_TAG in text:
            return

        result = []
        for ch in text:
            low = ch.lower()
            if low in MAP:
                repl = MAP[low]
                if ch.isupper():
                    repl = repl.upper()
                result.append(repl)
            else:
                result.append(ch)

        new_text = "".join(result)

        if new_text != text:
            await event.delete()
            await event.respond(new_text, reply_to=event.reply_to_msg_id)
