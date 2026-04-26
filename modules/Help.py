from telethon import events

help_message = """

<b>💎  Список доступных команд:</b>

┣ <code>.love</code> — анимация красного сердца
┣ <code>.type [текст]</code> — печатающий эффект
┣ <code>.tpback [текст]</code> — анимация tpback
┣ <code>.tp [текст]</code> — анимация tp
┣ <code>.line [текст]</code> — анимация линии
┣ <code>.bold on|off</code> — жирный текст
┣ <code>.shrift on|off</code> — смена шрифта
┣ <code>.write [текст]</code> — рукописное изображение
┣ <code>.ping</code> — задержка соединения
┣ <code>.getid</code> — ID чата / пользователя
┣ <code>.info</code> — информация о чате / пользователе
┣ <code>.iter</code> — дамп чата в CSV
┣ <code>.afk</code> — режим АФК
┣ <code>.gen male|female ru|ua</code> — генерация данных
┣ <code>.tagall</code> — тег всех участников
┣ <code>.spam [кол-во] [текст]</code> — спам текстом или медиа
┣ <code>.onl on|off</code> — постоянный онлайн
┣ <code>.tralka [1–50]</code> — случайное оскорбление
┣ <code>.ls [сл] [1–5] [стр] [1–3]</code> — лесенка оскорблений
┣ <code>.tr [1–1000]</code> — спам оскорблениями
┣ <code>.nerv on|off [id]</code> — режим «нервов»
┣ <code>.zaeb [off]</code> — режим заебать
┣ <code>.ad on|off (1–999) [текст]</code> — авторассылка
┣ <code>.swat [номер] [ФИО]</code> — сват-текст
┣ <code>.deanon</code> — фейковый деанон
┣ <code>.cb [кол-во]</code> — фейковый чек
┣ <code>.report [кол-во] [комм.]</code> — массовые жалобы
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