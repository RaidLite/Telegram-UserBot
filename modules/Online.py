from asyncio import sleep

from telethon import events, functions


def a(client):
    @client.on(events.NewMessage(pattern=r"\.onl", outgoing=True))
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
                await event.client(functions.account.UpdateStatusRequest(offline=False))
                await sleep(10)
        elif paytext == 'off':
            await event.edit("Вечный онлайн выключен.")
            await event.client(functions.account.UpdateStatusRequest(offline=True))
