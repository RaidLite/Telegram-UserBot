import io

import httpx
from telethon import events

IMG_URL = "https://i.ibb.co/rKDqVdfp/image.png"


def a(client):
    @client.on(events.NewMessage(pattern=r"\.cb(?:\s+(\d+))?", outgoing=True))
    async def _(event):
        if event.fwd_from:
            return

        amount = event.pattern_match.group(1)
        if not amount:
            amount = "1488"

        caption_text = f"🦋 Чек на 🪙 {amount} USDT (${amount})."

        try:
            await event.delete()
            async with httpx.AsyncClient() as session:
                response = await session.get(IMG_URL)
                if response.status_code != 200:
                    await event.respond("🔴 Ошибка при скачивании изображения.")
                    return

                img_bytes = io.BytesIO(response.content)
                img_bytes.name = "image.png"

            await client.send_file(
                event.chat_id,
                file=img_bytes,
                caption=caption_text
            )

        except httpx.RequestError as error:
            await event.respond(f"🔴 Ошибка запроса: {str(error)}")
        except Exception as error:
            await event.respond(f"🔴 Произошла ошибка: {str(error)}")
