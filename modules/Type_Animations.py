import asyncio
from collections import deque

from telethon import events
from telethon.errors import MessageNotModifiedError, MessageTooLongError

MSG_TOO_LONG = "Сообщение слишком длинное! Пожалуйста, сократите его до 4096 символов."
MSG_ANIM_TOO_LONG = "Сообщение слишком длинное для анимации!"
ERROR_PREFIX = "Ошибка во время анимации строки:"
TYPING_SYMBOL = "|"
DELAY_BETWEEN_EDITS = 0.1
TYPING_SYMBOL_2 = ">"
typing_symbol = "<"


async def putback_event_handler(event):
    if event.fwd_from:
        return

    input_str = event.pattern_match.group(1)
    result_text = ""

    await event.edit(TYPING_SYMBOL_2)
    await asyncio.sleep(DELAY_BETWEEN_EDITS)

    for character in reversed(input_str):
        result_text = character + result_text
        typing_text = TYPING_SYMBOL_2 + result_text
        await event.edit(f'<b>{typing_text}</b>', parse_mode='html')
        await asyncio.sleep(DELAY_BETWEEN_EDITS)


def a(client):
    client.on(events.NewMessage(pattern=r"\.tpback (.*)", outgoing=True))(putback_event_handler)

    @client.on(events.NewMessage(pattern=r"\.tp (.*)", outgoing=True))
    async def _(event):
        if event.fwd_from:
            return
        input_str = event.pattern_match.group(1)
        previous_text = ""
        await event.edit(typing_symbol)
        await asyncio.sleep(DELAY_BETWEEN_EDITS)
        for character in input_str:
            previous_text = previous_text + "" + character
            typing_text = previous_text + "" + typing_symbol
            await event.edit(f'<b>{typing_text}</b>', parse_mode='html')
            await asyncio.sleep(DELAY_BETWEEN_EDITS)

    @client.on(events.NewMessage(pattern=r"\.type (.*)", outgoing=True))
    async def _(event):
        if event.fwd_from:
            return

        input_str = event.pattern_match.group(1)
        previous_text = ""

        await event.edit(TYPING_SYMBOL)
        await asyncio.sleep(DELAY_BETWEEN_EDITS)

        for character in input_str:
            previous_text += character
            typing_text = previous_text + TYPING_SYMBOL
            await event.edit(typing_text)
            await asyncio.sleep(DELAY_BETWEEN_EDITS)
            await event.edit(previous_text)
            await asyncio.sleep(DELAY_BETWEEN_EDITS)

    @client.on(events.NewMessage(pattern=r"\.line", outgoing=True))
    async def _(event):
        if event.fwd_from:
            return

        try:
            message_text = event.message.message
        except AttributeError:
            message_text = event.original_update.message.message

        content = ' '.join(message_text.split()[1:])
        if not content:
            return

        if len(content) > 4096:
            await event.edit(MSG_TOO_LONG)
            return

        chars = deque(content)
        animation_delay = 0.1
        result = ""

        for _ in range(len(chars)):
            result += chars.popleft()
            await asyncio.sleep(animation_delay)
            try:
                await event.edit(result)
            except MessageNotModifiedError:
                pass
            except MessageTooLongError:
                await event.edit(MSG_ANIM_TOO_LONG)
                return
            except Exception as e:
                print(f"{ERROR_PREFIX} {e}")
                return
