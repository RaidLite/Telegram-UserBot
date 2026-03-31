from telethon import events
from telethon.tl.functions.users import GetFullUserRequest


def a(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.getid"))
    async def id_commands(event):
        if event.is_group:
            name_group = await event.get_chat()
            user = await event.get_sender()
            await event.edit(
                f"🖌 Название чата: {name_group.title}\n"
                f"🆔 ID чата: -100{event.chat_id}\n\n"
                f"💻 Твой ID: {user.id}",
                parse_mode=None
            )
        else:
            await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.info$', outgoing=True))
    async def info_handler(event):
        output = ""

        def add(label, value, is_bot_field=False):
            nonlocal output
            if value is None or value is False or value == "" or value == [] or value == {}:
                if is_bot_field:
                    output += f"<b>{label}:</b> Неа (Не бот)\n"
                else:
                    output += f"<b>{label}:</b> Неа\n"
            else:
                output += f"<b>{label}:</b> {value}\n"

        if event.is_reply:
            reply = await event.get_reply_message()
            sender = await reply.get_sender()
            if not sender:
                await event.edit("❌ Не удалось получить данные отправителя.")
                return

            try:
                full_user_response = await client(GetFullUserRequest(sender.id))
                user = full_user_response.users[0]
                full_user = full_user_response.full_user

                output += "👤 <b>Информация о пользователе</b>\n\n"

                add("🆔 ID", user.id)
                add("👤 Имя", f"{user.first_name or ''} {user.last_name or ''}".strip())
                add("🔗 Юзернейм", f"@{user.username}" if user.username else None)
                add("📞 Телефон", user.phone)
                add("🤖 Бот", "Да" if user.bot else None)
                add("⭐ Премиум", "Да" if user.premium else None)
                add("✅ Верифицирован", "Да" if user.verified else None)
                add("⚠️ Скам", "Да" if user.scam else None)
                add("📇 Контакт", "Да" if user.contact else None)
                add("📌 Истории недоступны", "Да" if user.stories_unavailable else None)
                add("💼 Бизнес бот", getattr(user, "bot_business", None), True)
                add("🕒 Статус", type(user.status).__name__.replace('UserStatus', '') if user.status else None)
                if hasattr(user.status, "was_online") and user.status:
                    add("⏱ Был в сети", user.status.was_online.strftime("%d.%m.%Y %H:%M"))

                output += "\n📄 <b>Дополнительно</b>\n\n"
                add("ℹ️ О себе", full_user.about)
                add("👥 Общих чатов", full_user.common_chats_count)
                add("📊 Активных пользователей (бот)", getattr(user, "bot_active_users", None), True)
                add("📦 Версия бота", getattr(user, "bot_info_version", None), True)

            except Exception as e:
                output += f"❌ Ошибка (User): <code>{e}</code>"

        else:
            output += "ℹ️ <b>Информация о чате</b>\n\n"
            try:
                chat = await event.get_chat()
                if getattr(chat, "broadcast", False) or getattr(chat, "megagroup", False):
                    from telethon.tl.functions.channels import GetFullChannelRequest
                    full = await client(GetFullChannelRequest(chat))
                else:
                    from telethon.tl.functions.messages import GetFullChatRequest
                    full = await client(GetFullChatRequest(chat.id))

                chat_info = full.chats[0]
                full_chat = full.full_chat

                add("📛 Название", chat_info.title)
                add("🆔 ID", chat_info.id)
                add("📢 Канал", "Да" if getattr(chat_info, "broadcast", None) else None)
                add("👥 Супергруппа", "Да" if getattr(chat_info, "megagroup", None) else None)
                add("✅ Верифицирован", "Да" if getattr(chat_info, "verified", None) else None)
                add("⚠️ Скам", "Да" if getattr(chat_info, "scam", None) else None)
                add("📅 Создан", chat_info.date.strftime("%d.%m.%Y %H:%M") if hasattr(chat_info,
                                                                                     "date") and chat_info.date else None)
                add("👥 Участников", getattr(full_chat, "participants_count", None))

                if full_chat.about:
                    output += f"\nℹ️ <b>Описание:</b> {full_chat.about}"
                else:
                    add("ℹ️ Описание", None)

            except Exception as e:
                output += f"❌ Ошибка (Chat): <code>{e}</code>"

        await event.edit(output, parse_mode="html")
