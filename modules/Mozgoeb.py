from asyncio import sleep
from telethon import events

stop_flags = {}


def a(client):
    @client.on(events.NewMessage(pattern=r"\.zaeb", outgoing=True))
    async def _(event):
        chat_id = event.chat_id
        args = event.text.split()

        if len(args) > 1 and args[1] == "off":
            stop_flags[chat_id] = True
            await event.delete()
            return

        stop_flags[chat_id] = False

        reply = await event.get_reply_message()
        if not reply:
            await event.edit("<b>Использовать в ответ на сообщение!</b>", parse_mode='html')
            return

        user_id = reply.sender_id

        count = 50
        if len(args) > 1 and args[-1].isdigit():
            count = max(1, int(args[-1]))

        txt = f'<a href="tg://user?id={user_id}">_</a>'
        await event.delete()

        for _ in range(count):
            if stop_flags.get(chat_id):
                break

            try:
                msg = await event.client.send_message(event.to_id, txt, parse_mode='html')
                await sleep(0.3)
                await msg.delete()
                await sleep(0.3)
            except:
                break

        stop_flags[chat_id] = False