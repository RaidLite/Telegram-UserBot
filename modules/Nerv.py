import asyncio
import random

from telethon import functions, types, events

nerv_tasks = {}


def a(client):
    @client.on(events.NewMessage(pattern=r"\.nerv (on|off)(?: (\d+))?", outgoing=True))
    async def nerv_handler(event):
        status = event.pattern_match.group(1).lower()
        custom_id = event.pattern_match.group(2)
        target_chat = int(custom_id) if custom_id else event.chat_id

        await event.delete()

        if status == "on":
            if target_chat not in nerv_tasks:
                nerv_tasks[target_chat] = asyncio.create_task(
                    nerv_logic(client, target_chat)
                )

        elif status == "off":
            task = nerv_tasks.pop(target_chat, None)
            if task:
                task.cancel()


async def nerv_online_status(client):
    await client(functions.account.UpdateStatusRequest(offline=False))
    await asyncio.sleep(0.1)
    await client(functions.account.UpdateStatusRequest(offline=True))
    await asyncio.sleep(0.1)


async def nerv_task(client, chat_id, act):
    await nerv_online_status(client)
    await nerv_online_status(client)
    await nerv_online_status(client)
    await client(functions.messages.SetTypingRequest(
        peer=chat_id,
        action=act
    ))
    await asyncio.sleep(1.5)
    await client(functions.messages.SetTypingRequest(
        peer=chat_id,
        action=types.SendMessageCancelAction()
    ))


async def nerv_logic(client, chat_id):
    actions = [
        types.SendMessageTypingAction(),
        types.SendMessageRecordAudioAction(),
        types.SendMessageRecordVideoAction(),
        types.SendMessageChooseStickerAction(),
        types.SendMessageUploadPhotoAction(progress=1)
    ]

    try:
        while True:
            act = random.choice(actions)
            await nerv_task(client, chat_id, act)
    except asyncio.CancelledError:
        raise
    except Exception:
        return
