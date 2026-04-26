from telethon import events

help_message = """

<b>💎  Список доступных команд:</b>

┣ <code>.love</code> — анимация красного сердца
┣ <code>.type [текст]</code> — печатающий эффект
┣ <code>.tpback [текст]</code> — анимация tpback
┣ <code>.tp [текст]</code> — анимация tp
┣ <code>.line [текст]</code> — анимация линии
┣ <code>.write [текст]</code> — рукописное изображение
┣ <code>.getid</code> — ID чата / пользователя
┣ <code>.info</code> — информация о чате / пользователе
┣ <code>.iter</code> — дамп чата в CSV
┣ <code>.gen male|female ru|ua</code> — генерация данных
┣ <code>.tralka [1–50]</code> — случайное оскорбление
┣ <code>.ls [сл] [1–5] [стр] [1–3]</code> — лесенка оскорблений
┣ <code>.tr [1–1000]</code> — спам оскорблениями
┣ <code>.swat [номер] [ФИО]</code> — сват-текст
┣ <code>.tools help</code> — тулзы
┣ <code>.mods help</code> — моды
┗ <code>.gifts help</code> — маркет Telegram
"""

def init(client):
    @client.on(events.NewMessage(pattern=r"\.help", outgoing=True))
    async def _(event):
        if event.fwd_from: return
        await event.edit(
            help_message,
            parse_mode='html'
)