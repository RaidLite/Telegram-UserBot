from telethon import events

CHUNK_SIZE = 50


def a(client):
    @client.on(events.NewMessage(outgoing=True, pattern=".tagall"))
    async def _(event):
        if event.fwd_from or not event.is_group:
            return

        chat = await event.get_input_chat()
        mentions = []

        async for user in client.iter_participants(chat):
            mentions.append(f"[{user.username}](tg://user?id={user.id})")

        for i in range(0, len(mentions), CHUNK_SIZE):
            chunk = "\n".join(mentions[i:i + CHUNK_SIZE])
            await event.reply(f"Приветик всем)))\n\n{chunk}")

        await event.delete()
