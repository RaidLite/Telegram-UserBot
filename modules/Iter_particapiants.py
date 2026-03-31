import csv
import io
import time

import phonenumbers
from phonenumbers import geocoder
from telethon import events
from telethon.errors import RPCError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import DocumentAttributeFilename, ChannelParticipantsAdmins

ITER_COMMAND_PATTERN = r"\.iter"

header = [
    'ID', 'Access Hash', 'Имя', 'Фамилия', 'Username', 'Телефон',
    'Бот', 'Верифицирован', 'Скам', 'Фейк', 'Ограничен', 'Язык',
    'Статус (Online)', 'Последний вход', 'Удален', 'Премиум', 'В контактах',
    'Страна/Регион', 'О себе', 'Общих чатов', 'Есть фото', 'Причина ограничений',
    'Админ', 'Бот-админ право', 'Скрытый телефон'
]


def get_country_from_phone(phone):
    if not phone or phone == '-':
        return '-'
    try:
        phone_norm = phone if phone.startswith('+') else f'+{phone}'
        number = phonenumbers.parse(phone_norm)
        country = geocoder.country_name_for_number(number, 'ru')
        location = geocoder.description_for_number(number, 'ru')
        return f"{country} ({location})" if location else country
    except:
        return '-'


def a(client):
    @client.on(events.NewMessage(pattern=ITER_COMMAND_PATTERN, outgoing=True))
    async def handle_iter_command(event):
        args = event.text.split()
        await event.delete()

        chat = await event.get_chat()
        fetch_full = "-f" in args
        include_only_with_phone = "-n" in args

        timestamp = int(time.time())
        filename = f'export_{chat.id}_{timestamp}.csv'

        admins = []
        try:
            admins = [u.id for u in await client.get_participants(chat, filter=ChannelParticipantsAdmins)]
        except:
            pass

        sio = io.StringIO()
        writer = csv.writer(sio, delimiter='|')
        writer.writerow(header)

        async for user in client.iter_participants(chat.id):
            if include_only_with_phone and not user.phone:
                continue

            try:
                about = '-'
                if fetch_full:
                    try:
                        full_user = await client(GetFullUserRequest(user.id))
                        about = full_user.full_user.about or '-'
                        time.sleep(0.1)
                    except:
                        pass

                phone = user.phone or '-'

                data = [
                    user.id,
                    user.access_hash,
                    user.first_name or '-',
                    user.last_name or '-',
                    user.username or '-',
                    phone,
                    '+' if user.bot else '-',
                    '+' if user.verified else '-',
                    'SCAM' if user.scam else '-',
                    'FAKE' if user.fake else '-',
                    '+' if user.restricted else '-',
                    user.lang_code or '-',
                    user.status.__class__.__name__.replace('UserStatus', '') if user.status else 'Hidden',
                    getattr(user.status, 'was_online', '-') if hasattr(user.status, 'was_online') else '-',
                    '+' if user.deleted else '-',
                    '+' if user.premium else '-',
                    '+' if user.mutual_contact else '-',
                    get_country_from_phone(phone),
                    about,
                    getattr(user, 'common_chats_count', 0),
                    '+' if user.photo else '-',
                    ', '.join(
                        [f"{r.reason}" for r in user.restrictions]) if user.restricted and user.restrictions else '-',
                    '+' if user.id in admins else '-',
                    getattr(user, 'bot_chat_history', '-'),
                    '+' if not user.phone and not user.deleted and not user.bot else '-'
                ]
                writer.writerow(data)
            except Exception:
                continue

        csv_data = sio.getvalue()
        try:
            await client.send_file(
                'me',
                io.BytesIO(csv_data.encode('utf-8')),
                attributes=[DocumentAttributeFilename(filename)]
            )
        except RPCError:
            pass
