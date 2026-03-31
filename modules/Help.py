from telethon import events


def a(client):
    @client.on(events.NewMessage(pattern=r"\.help", outgoing=True))
    async def _(event):
        if event.fwd_from:
            return
        help_message = """
 
<b>🌈  Список доступных команд:</b>

▪ <code>.love</code> - показать анимацию Красного сердца
▪ <code>.type [текст]</code> - показать анимацию «type»  
▪ <code>.tpback [текст]</code> - показать анимацию «tpback»  
▪ <code>.tp [текст]</code> - показать анимацию «tp»  
▪ <code>.line [текст]</code> - показать анимацию «line»  
▪ <code>.bold on|off</code> - режим жирного текста  
▪ <code>.shrift on|off</code> - режим шрифта  
▪ <code>.afk</code> - Режим АФК  
▪ <code>.gen male|female ru|ua</code> - генерация инфы
▪ <code>.ping</code> - показать пинг
▪ <code>.write [текст]</code> — рукописное изображение  
▪ <code>.getid</code> — ID чата и пользователя
▪ <code>.tagall</code> — тег всех участников чата
▪ <code>.iter</code> - дамп чата в csv файл
▪ <code>.info</code> - информация о чате / пользователе
▪ <code>.spam [количество] [текст]</code> — если есть текст спамит им, если нет и есть реплай на медиа, спамит медиа
▪ <code>.swat [номер] [ФИО]</code> - сгенерировать сват текст
▪ <code>.tralka [1-50]</code> - обозвать текстом
▪ <code>.ls [к.слов] [1-5] [к.строк] [1-3]</code> - лесенка оскорблений
▪ <code>.tr [1-1000]</code> - спамить оскорблениями
▪ <code>.deanon</code> - фейково задеанонить
▪ <code>.cb [количество]</code> - отправить фейковый чек
▪ <code>.nerv on|off [id]</code> - включить режим "нервов", кошмарит собеседника
▪ <code>.ad on|off (1-999) текст</code> - начать авто рассылку рекламы в чат
▪ <code>.zaeb [off]</code> - заебать типа
▪ <code>.onl on|off</code> - вечный онлайн
▪ <code>.report [количество] [комментарий]</code> - массовые жалобы

        """
        await event.edit(help_message, parse_mode='html')
