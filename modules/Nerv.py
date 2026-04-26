from asyncio import sleep, create_task, CancelledError

from telethon import functions, events

nerv_tasks = {}


def init(client):
    @client.on(events.NewMessage(pattern=r"\.nerv (on|off)(?: (\d+))?", outgoing=True))
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


async def nerv_online_status(client):
    await client(functions.account.UpdateStatusRequest(offline=False))
    await client(functions.account.UpdateStatusRequest(offline=True))

async def nerv_logic(client):
    try:
        while True: await nerv_online_status(client)
    except CancelledError: raise
    except Exception:return