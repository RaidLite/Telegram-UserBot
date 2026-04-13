from asyncio import create_task
from re import compile, I
from telethon import events, functions, types

CHATS_BLACKLIST = {
    1622808649, 1559501630,
    1985737506, 5014831088
}
CODE_REGEX = compile(r"(CryptoBot|send|tonRocketBot|wallet|xrocket)\?start=([A-Za-z0-9_-]+)", I)
activated = set()

async def fast_activate(client, bot, code):
    if code in activated: return
    activated.add(code)
    try: await client(functions.messages.StartBotRequest(
        bot=bot,
        peer=bot,
        start_param=code
    ))
    except Exception: pass

def init(client):
    opts = dict(incoming=True, blacklist_chats=True, chats=CHATS_BLACKLIST)

    @client.on(events.NewMessage(**opts))
    @client.on(events.MessageEdited(**opts))
    async def handler(event):
        def try_match(text: str | None) -> bool:
            if not text:
                return False
            m = CODE_REGEX.search(text)
            if m:
                create_task(fast_activate(client, m.group(1), m.group(2)))
                return True
            return False

        if try_match(event.raw_text):
            return

        if event.reply_markup:
            for row in event.reply_markup.rows:
                for btn in row.buttons:
                    if isinstance(btn, types.KeyboardButtonUrl) and try_match(btn.url):
                        return

        if event.entities:
            t = event.raw_text
            for ent in event.entities:
                url = ent.url if isinstance(ent, types.MessageEntityTextUrl) else \
                      t[ent.offset:ent.offset+ent.length] if isinstance(ent, types.MessageEntityUrl) else None
                if url and try_match(url):
                    return