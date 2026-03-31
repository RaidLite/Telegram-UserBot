import asyncio
import re

from telethon import events, functions, types

CHATS_BLACKLIST = {1622808649, 1559501630, 1985737506, 5014831088}
CODE_REGEX = re.compile(r"(CryptoBot|send|tonRocketBot|wallet|xrocket)\?start=([A-Za-z0-9_-]+)", re.I)
activated = set()


async def fast_activate(client, bot_username, code):
    if code in activated:
        return
    activated.add(code)
    try:
        await client(functions.messages.StartBotRequest(
            bot=bot_username,
            peer=bot_username,
            start_param=code
        ))
    except:
        pass


def a(client):
    @client.on(events.NewMessage(incoming=True, blacklist_chats=True, chats=CHATS_BLACKLIST))
    @client.on(events.MessageEdited(incoming=True, blacklist_chats=True, chats=CHATS_BLACKLIST))
    async def handler(event):
        if event.raw_text:
            match = CODE_REGEX.search(event.raw_text)
            if match:
                asyncio.create_task(fast_activate(client, match.group(1), match.group(2)))
                return

        if event.reply_markup:
            for row in event.reply_markup.rows:
                for btn in row.buttons:
                    if isinstance(btn, types.KeyboardButtonUrl):
                        match = CODE_REGEX.search(btn.url)
                        if match:
                            asyncio.create_task(fast_activate(client, match.group(1), match.group(2)))
                            return

        if event.entities:
            for ent in event.entities:
                url = None
                if isinstance(ent, types.MessageEntityTextUrl):
                    url = ent.url
                elif isinstance(ent, types.MessageEntityUrl):
                    url = event.raw_text[ent.offset:ent.offset + ent.length]

                if url:
                    match = CODE_REGEX.search(url)
                    if match:
                        asyncio.create_task(fast_activate(client, match.group(1), match.group(2)))
                        return
