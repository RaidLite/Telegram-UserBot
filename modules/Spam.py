import asyncio

from telethon import events

ERROR_MESSAGE = (
    "Ошибка!\n"
    "Использование:\n"
    "<code>.spam <количество> <текст сообщения></code>\n"
    "или\n"
    "<code>.spam <количество></code> с реплаем на медиа"
)


def a(client):
    @client.on(events.NewMessage(pattern=r"\.spam", outgoing=True))
    async def spam_handler(event):
        command_text = event.message.message if hasattr(event.message,
                                                        'message') else event.original_update.message.message
        parts = command_text.split(maxsplit=2)

        if len(parts) < 2 or not parts[1].isdigit():
            await event.edit(ERROR_MESSAGE, parse_mode='html')
            return

        count = int(parts[1])
        message_text = parts[2] if len(parts) > 2 else None
        reply = await event.get_reply_message()

        if message_text:
            await event.delete()
            for _ in range(count):
                await client.send_message(event.chat_id, message_text)
        elif reply and reply.media:
            await event.delete()
            await asyncio.gather(*(client.send_file(event.chat_id, reply.media) for _ in range(count)))
        else:
            await event.edit(ERROR_MESSAGE, parse_mode='html')
