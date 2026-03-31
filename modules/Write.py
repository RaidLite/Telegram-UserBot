from io import BytesIO
from urllib.parse import quote

import httpx
from telethon import events

WRITE_TEXT = "Введите текст."
TEXTING = "Печатает..."
LOADING = "Загрузка..."
ERROR = "Не удалось получить изображение."


def a(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.write\s+(.+)'))
    async def write_command_handler(event):
        args = event.pattern_match.group(1).strip()
        if not args:
            await event.edit(WRITE_TEXT)
            return

        await event.edit(TEXTING)

        try:
            api_url = f"https://apis.xditya.me/write?text={quote(args)}"

            async with httpx.AsyncClient(timeout=30.0) as http_client:
                await event.edit(LOADING)
                response = await http_client.get(api_url)

                if response.status_code == 200:
                    file_bytes = BytesIO(response.content)
                    file_bytes.name = "image.jpg"

                    await client.send_file(
                        event.chat_id,
                        file=file_bytes,
                        force_document=False
                    )
                    await event.delete()
                else:
                    await event.edit(f"{ERROR} (Status: {response.status_code})")
        except Exception as e:
            print(f"Ошибка: {e}")
            await event.delete()
