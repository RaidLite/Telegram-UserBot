import asyncio

from telethon import events

active_ads = {}


def a(client):
    @client.on(events.NewMessage(pattern=r'\.ad on (\d+) (.+)', outgoing=True))
    async def ad_on(event):
        await event.delete()

        chat_id = event.chat_id
        delay = int(event.pattern_match.group(1))
        text = event.pattern_match.group(2)
        media = event.message.media

        if chat_id in active_ads:
            return

        async def spammer():
            while chat_id in active_ads:
                if media:
                    await client.send_file(chat_id, media, caption=text)
                else:
                    await client.send_message(chat_id, text)
                await asyncio.sleep(delay)

        task = asyncio.create_task(spammer())
        active_ads[chat_id] = task

    @client.on(events.NewMessage(pattern=r'\.ad off', outgoing=True))
    async def ad_off(event):
        await event.delete()

        chat_id = event.chat_id
        if chat_id in active_ads:
            active_ads[chat_id].cancel()
            del active_ads[chat_id]
