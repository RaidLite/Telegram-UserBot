from telethon import events

IMG_URL = "https://i.ibb.co/rKDqVdfp/image.png"


def init(client):
    @client.on(events.NewMessage(pattern=r"\.cb(?:\s+(\d+))?", outgoing=True))
    async def _(event):
        if event.fwd_from: return
        amount = event.pattern_match.group(1) or "1488"
        caption = f"🦋 Чек на 🪙 {amount} USDT (${amount})."

        try:
            await event.delete()
            await client.send_file(
                event.chat_id,
                IMG_URL,
                caption=caption
            )
        except Exception as e:
            await event.respond(f"🔴 Ошибка: {e}")