import csv
from io import BytesIO, StringIO
from time import time

from phonenumbers import geocoder, parse
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import DocumentAttributeFilename, ChannelParticipantsAdmins

COMMAND_PATTERN = r"\.iter"

class UserExporter:
    HEADER = [
        'ID', 'Имя', 'Фамилия', 'Username', 'Телефон', 'Страна/Регион',
        'Бот', 'Скам', 'Премиум', 'Админ', 'Статус', 'О себе'
    ]

    @staticmethod
    def get_location(phone):
        if not phone or phone == '-': return '-'
        try:
            phone_norm = phone if phone.startswith('+') else f'+{phone}'
            num = parse(phone_norm)
            country = geocoder.country_name_for_number(num, 'ru')
            location = geocoder.description_for_number(num, 'ru')
            return f"{country} ({location})" if location else country
        except:
            return '-'

    @classmethod
    async def format_user_data(cls, client, user, is_admin, fetch_full=False):
        about = '-'
        if fetch_full:
            try:
                full = await client(GetFullUserRequest(user.id))
                about = full.full_user.about or '-'
            except: pass

        return [
            user.id,
            user.first_name or '-',
            user.last_name or '-',
            user.username or '-',
            user.phone or '-',
            cls.get_location(user.phone),
            '+' if user.bot else '-',
            '+' if user.scam else '-',
            '+' if user.premium else '-',
            '+' if is_admin else '-',
            user.status.__class__.__name__.replace('UserStatus', '') if user.status else 'Hidden',
            about
        ]

def init(client):
    @client.on(events.NewMessage(pattern=COMMAND_PATTERN, outgoing=True))
    async def handle_iter_command(event):
        args = event.text.split()
        await event.delete()

        chat = await event.get_chat()
        fetch_full = "-f" in args
        only_phones = "-n" in args

        admins = []
        try:
            admins = [u.id for u in await client.get_participants(chat, filter=ChannelParticipantsAdmins)]
        except: pass

        output = StringIO()
        writer = csv.writer(output, delimiter='|')
        writer.writerow(UserExporter.HEADER)

        async for user in client.iter_participants(chat):
            if only_phones and not user.phone:
                continue
            try:
                row = await UserExporter.format_user_data(client, user, user.id in admins, fetch_full)
                writer.writerow(row)
            except:
                continue

        filename = f'export_{chat.id}_{int(time())}.csv'
        file_buffer = BytesIO(output.getvalue().encode('utf-8'))
        
        await client.send_file(
            'me', 
            file_buffer, 
            attributes=[DocumentAttributeFilename(filename)]
        )