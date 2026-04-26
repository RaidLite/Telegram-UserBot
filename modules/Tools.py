from asyncio import sleep
from telethon import events
from asyncio import sleep, create_task, CancelledError
from time import perf_counter
from telethon import events
from telethon.tl.functions.account import UpdateStatusRequest
from asyncio import gather
from telethon import events, types, functions

reasons = [
    types.InputReportReasonChildAbuse(),
    types.InputReportReasonCopyright(),
    types.InputReportReasonFake(),
    types.InputReportReasonPornography(),
    types.InputReportReasonSpam(),
    types.InputReportReasonViolence(),
    types.InputReportReasonOther(),
    types.InputReportReasonCopyright(),
    types.InputReportReasonIllegalDrugs(),
    types.InputReportReasonGeoIrrelevant()
]

IMG_URL = "https://i.ibb.co/rKDqVdfp/image.png"
CHUNK_SIZE = 50

nerv_tasks = {}
active_ads = {}
stop_flags = {}

SEARCHING = "⚠️ Поиск по базам данных {}/50..."
DEANON_RESULT = (
    'Имя найдено, но не найдено крч\n'
    'Мама: не найдено\n'
    'Папа: чучут найдена\n'
    'Бабушка: найден прах\n'
    'Дед: похуй умер\n'
    'Размер хуя: карнишон\n'
    'Анальное отверстие: пробито\n'
    'Цвет простаты: березовый\n'
    'Цвет говна: красный\n'
    'Ебло: ахуевшее\n'
    'Страна: залупинск\n'
    'Оператор: пидор2\n'
    'Дом: там который\n'
    'Место проживание: земля\n'
    'Номер: +888888888\n'
    'Адрес: деаноновно 1/2\n'
    'Простата: масирована\n\n'
    'Жду извинений 😈😈😈'
)

ERROR_MESSAGE = (
    "Ошибка!\n"
    "Использование:\n"
    "<code>.spam <количество> <текст сообщения></code>\n"
    "или\n"
    "<code>.spam <количество></code> с реплаем на медиа"
)

COMMAND_MENU = (
    "💠 Tools - Меню\n\n"
    "┣ <code>.tools ad on [delay] [text]</code> - Включить спам\n"
    "┣ <code>.tools ad off</code> - Выключить спам\n"
    "┣ <code>.tools ping</code> - Проверить пинг\n"
    "┣ <code>.tools onl on/off</code> - Включить/выключить вечный онлайн\n"
    "┣ <code>.tools nerv on/off</code> - Включить/выключить вечный онлайн\n"
    "┣ <code>.tools zaeb [off] [count]</code> - Заебать пользователя\n"
    "┣ <code>.tools spam [количество] [текст]</code> - Спам текстом\n"
    "┣ <code>.tools report</code> - Пожаловаться на пользователя\n"
    "┣ <code>.tools tagall</code> - Отметить всех участников в группе\n"
    "┣ <code>.tools cb [кол-во]</code> - Фейковый чек\n"
    "┣ <code>.tools help</code> - Показать это меню\n"
    "┗ <code>.tools deanon</code> - Фейковый деанон\n"
)

async def nerv_online_status(client):
    await client(UpdateStatusRequest(False))
    await client(UpdateStatusRequest(True))

async def nerv_logic(client):
    try:
        while True: await nerv_online_status(client)
    except CancelledError: raise
    except Exception:return

def init(client):
    @client.on(events.NewMessage(pattern=r"\.tools$", outgoing=True))
    async def tools_main(event): await event.edit("ℹ️ Чтобы узнать команды, напишите <code>.tools help</code>", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.tools help", outgoing=True))
    async def tools_help(event): await event.edit(COMMAND_MENU, parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.tools deanon", outgoing=True))
    async def _(event):
        for i in range(1, 51):
            await event.edit(SEARCHING.format(i))
            await sleep(0.2)

        await event.edit(DEANON_RESULT)

    @client.on(events.NewMessage(pattern=r"\.tools cb(?:\s+(\d+))?", outgoing=True))
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

    @client.on(events.NewMessage(outgoing=True, pattern=".tools tagall"))
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

    @client.on(events.NewMessage(pattern=r"\.tools report", outgoing=True))
    async def _(event):
        reported_actions = set()

        chat_id = event.chat_id
        if chat_id in reported_actions:
            return await event.edit("<b>Действие уже было выполнено ранее.</b>", parse_mode='html')

        args = event.message.text.split(' ')
        times = 1

        if len(args) > 1 and args[1].isdigit():
            times = int(args[1])

        for _ in range(times):
            for reason in reasons:
                try:
                    await client(
                        functions.account.ReportPeerRequest(
                            peer=event.peer_id,
                            reason=reason,
                            message=''
                        )
                    )

                    reason_text = str(reason).replace('InputReportReason', '').replace('()', '')
                    await event.edit(f'Жалоба {reason_text} отправлена!')
                except Exception as e:
                    print(e)

        reported_actions.add(chat_id)
        await event.edit(f'<b>Жалобы ({times * len(reasons)}) успешно отправлены!</b>', parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.tools spam", outgoing=True))
    async def spam_handler(event):
        command_text = event.message.message if hasattr(event.message, 'message') else event.original_update.message.message
        parts = command_text.split(maxsplit=2)

        if len(parts) < 2 or not parts[1].isdigit():
            await event.edit(ERROR_MESSAGE, parse_mode='html')
            return

        count = int(parts[1])
        message_text = parts[2] if len(parts) > 2 else None
        reply = await event.get_reply_message()

        if message_text:
            await event.delete()
            for _ in range(count): await client.send_message(event.chat_id, message_text)
        elif reply and reply.media:
            await event.delete()
            await gather(*(client.send_file(event.chat_id, reply.media) for _ in range(count)))
        else:
            await event.edit(ERROR_MESSAGE, parse_mode='html')

    @client.on(events.NewMessage(pattern=r'\.tools ad on (\d+) (.+)', outgoing=True))
    async def ad_on(event):
        await event.delete()

        chat_id = event.chat_id
        delay = int(event.pattern_match.group(1))
        text = event.pattern_match.group(2)
        media = event.message.media

        if chat_id in active_ads: return

        async def spammer():
            while chat_id in active_ads:
                if media: await client.send_file(chat_id, media, caption=text)
                else: await client.send_message(chat_id, text)
                await sleep(delay)

        task = create_task(spammer())
        active_ads[chat_id] = task

    @client.on(events.NewMessage(pattern=r'\.tools ad off', outgoing=True))
    async def ad_off(event):
        await event.delete()

        chat_id = event.chat_id
        if chat_id in active_ads:
            active_ads[chat_id].cancel()
            del active_ads[chat_id]

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tools ping$"))
    async def ping_command_handler(event):
        start = perf_counter()
        await event.edit("Понг!")
        end = perf_counter()
        ping_time = round((end - start) * 1000, 2)
        await event.edit(f"Пинг: {ping_time} мс")

    @client.on(events.NewMessage(pattern=r"\.tools onl", outgoing=True))
    async def online(event):
        try:
            txt1 = event.message.message
        except:
            txt1 = event.original_update.message.message
        paytext = ''.join(txt1.split(' ')[1:])
        if not paytext:
            paytext = '0'
            await event.edit(
                '<b>Ошибка!</b> \n<code>.onl on</code> для включения\n<code>.onl off</code> для выключения\n',
                parse_mode='html')
        if paytext == 'on':
            await event.edit("Вечный онлайн включен.")
            while 1 == 1:
                await event.client(UpdateStatusRequest(offline=False))
                await sleep(10)
        elif paytext == 'off':
            await event.edit("Вечный онлайн выключен.")
            await event.client(UpdateStatusRequest(offline=True))

    @client.on(events.NewMessage(pattern=r"\.tools nerv (on|off)(?: (\d+))?", outgoing=True))
    async def nerv_handler(event):
        status = event.pattern_match.group(1).lower()
        custom_id = event.pattern_match.group(2)
        target_chat = int(custom_id) if custom_id else event.chat_id

        await event.delete()

        if status == "on":
            if target_chat not in nerv_tasks:
                nerv_tasks[target_chat] = create_task(
                    nerv_logic(client)
                )

        elif status == "off":
            task = nerv_tasks.pop(target_chat, None)
            if task:
                task.cancel()
    
    @client.on(events.NewMessage(pattern=r"\.tools zaeb", outgoing=True))
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
                await sleep(0.1)
                await msg.delete()
                await sleep(0.1)
            except:
                break

        stop_flags[chat_id] = False
