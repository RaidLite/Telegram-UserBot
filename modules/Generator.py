import random

from telethon import events

DATA = {
    "ru": {
        "male": ["Иван", "Дмитрий", "Алексей", "Сергей", "Николай", "Павел", "Юрий", "Олег", "Артур", "Борис",
                 "Вадим", "Роман", "Григорий", "Виктор", "Константин", "Михаил", "Тимофей", "Егор", "Фёдор",
                 "Степан", "Максим"],
        "female": ["Анна", "Мария", "Елена", "Ольга", "Татьяна", "Ирина", "Светлана", "Наталья", "Виктория",
                   "Алина", "Людмила", "Зинаида", "Дарина", "Ксения", "Юлия", "Алёна", "Лариса", "Галина", "Римма",
                   "Вероника"],
        "surnames": ["Петров", "Иванов", "Смирнов", "Кузнецов", "Попов", "Сидоров", "Васильев", "Григорьев", "Орлов",
                     "Морозов", "Волков", "Киселёв", "Захаров", "Андреев", "Фролов", "Данилов", "Мельников", "Чернов",
                     "Тимофеев"],
        "cities": ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород", "Челябинск",
                   "Ростов-на-Дону", "Уфа", "Пермь", "Самара", "Красноярск"],
        "streets": ["Ленина", "Советская", "Гагарина", "Победы", "Мира", "Центральная", "Первомайская", "Комсомольская",
                    "Октябрьская", "Солнечная", "Тимирязева", "Чапаева", "Дзержинского", "Космонавтов", "Лермонтова",
                    "Пушкина", "Школьная", "Юбилейная", "Молодежная", "Строителей", "Зеленая", "Калинина",
                    "Партизанская",
                    "Кузнецова", "Победы", "Фрунзе"],
        "card_types": ['Visa', 'MasterCard', 'Мир']
    },
    "ua": {
        "male": ["Олександр", "Іван", "Микола", "Андрій", "Юрій", "Володимир", "Тарас", "Сергій", "Дмитро",
                 "Леонід", "Петро", "Василь", "Ярослав", "Богдан", "Роман", "Анатолій", "Ігор", "Олег", "Роман",
                 "Євген"],
        "female": ["Ольга", "Наталія", "Ірина", "Світлана", "Тетяна", "Людмила", "Катерина", "Марія", "Алла", "Яна",
                   "Вікторія", "Анна", "Олена", "Люба", "Юлія", "Ніна", "Ганна", "Ксенія", "Орися", "Марина"],
        "surnames": ["Шевченко", "Коваленко", "Бондар", "Ткаченко", "Мельник", "Коваль", "Петренко", "Сидоренко",
                     "Захарченко", "Гончаренко", "Дьяків", "Сердюк", "Кравченко", "Нечипорук", "Литвин", "Пасічник",
                     "Яценко", "Чорний", "Гречаник"],
        "cities": ["Київ", "Харків", "Одеса", "Дніпро", "Львів", "Запоріжжя", "Вінниця", "Чернігів", "Полтава", "Суми",
                   "Тернопіль", "Хмельницький", "Херсон"],
        "streets": ["Шевченка", "Грушевського", "Бандери", "Хрещатик", "Лесі Українки", "Соборна", "Гагаріна",
                    "Козацька",
                    "Незалежності", "Визволителів", "Тараса Шевченка", "Мазепи", "Лермонтова", "Дніпровська",
                    "Київська",
                    "Тимошенка", "Чорновола", "Січових Стрільців", "Політехнічна", "Суворова", "Перемоги",
                    "Старообрядницька",
                    "Пушкіна", "Молодіжна"],
        "card_types": ['Visa', 'MasterCard']
    }
}

domains = ['gmail.com', 'mail.ru', 'yandex.ru', 'rambler.ru', 'outlook.com', 'ukr.net', 'meta.ua', 'hotmail.com',
           'aol.com', 'yahoo.com', 'zoho.com', 'protonmail.com', 'tutanota.com', 'icloud.com', 'live.com', 'inbox.ru',
           'bk.ru', 'list.ru', 'fastmail.com', 'mail.com', 'gmx.com', 'me.com', 'seznam.cz', 'orange.fr', 'wanadoo.fr',
           'sfr.fr', 'laposte.net', 'verizon.net', 'comcast.net', 'att.net', 'earthlink.net', 'bellsouth.net',
           'talktalk.net', 'blueyonder.co.uk', 'ntlworld.com', 'sky.com', 'btinternet.com', 'virginmedia.com',
           'mailchimp.com', 'sendgrid.net', 'posteo.de', 'runbox.com', 'hushmail.com', 'mailfence.com']

brands = ["Lada", "Kia", "Hyundai", "Toyota", "Volkswagen", "Renault", "Nissan", "Ford", "Mazda", "Skoda", "BMW",
          "Mercedes-Benz", "Audi", "Chevrolet", "Peugeot", "Honda", "Mitsubishi", "Subaru", "Opel", "Land Rover",
          "Jeep", "Volvo", "Fiat", "Chery", "GAC", "BYD", "Great Wall", "Jaguar", "Porsche", "Lexus", "Ferrari",
          "Tesla"]

models = ["Vesta", "Rio", "Solaris", "Camry", "Polo", "Logan", "Qashqai", "Focus", "CX-5", "Octavia", "X5", "A6",
          "C-Class", "Q7", "Captiva", "Partner", "Civic", "Outlander", "Forester", "Astra", "Wrangler", "Volvo XC90",
          "500", "Tiggo", "G3", "Tucson", "B-Class", "Model 3", "458 Italia", "911"]


def a(client):
    @client.on(events.NewMessage(pattern=r"\.gen(?:\s+(.+))?$", outgoing=True))
    async def handler(event):
        args = event.pattern_match.group(1)

        if args:
            parts = args.split()
            gender = parts[0] if parts[0] in ['male', 'female'] else random.choice(['male', 'female'])
            country = parts[1] if len(parts) > 1 and parts[1] in ['ru', 'ua'] else random.choice(['ru', 'ua'])
        else:
            gender = random.choice(['male', 'female'])
            country = random.choice(['ru', 'ua'])

        await event.respond(await generate_identity(gender, country))
        await event.delete()


async def generate_all():
    return await generate_identity(random.choice(['male', 'female']), random.choice(['ru', 'ua']))


def random_choice(country, gender, key):
    return random.choice(DATA[country][key if key in DATA[country] else f"{gender}" if key == 'names' else key])


def random_digits(length):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def random_mac():
    return ':'.join(f"{random.randint(0, 255):02x}" for _ in range(6))


def random_date(start=2010, end=2023):
    return f"{random.randint(1, 31):02d}.{random.randint(1, 12):02d}.{random.randint(start, end)}"


async def generate_identity(gender='male', country='ru'):
    first = random_choice(country, gender, gender)
    last = random_choice(country, gender, 'surnames')
    name = f"{first} {last}"
    age = random.randint(18, 65)
    location = f"{random_choice(country, gender, 'cities')}, {country.upper()}"
    phone = f"+7{random_digits(10)}" if country == 'ru' else f"+380{random_digits(9)}"
    email = f"{name.lower().replace(' ', '.')}{random.randint(100, 999)}@{random.choice(domains)}"
    passport = f"Серия {random.randint(10, 99)} {random.randint(10, 99)} Номер {random_digits(6)} | Выдан {random_date()}" if country == 'ru' else f"ID{random_digits(8)}"
    address = f"{random_choice(country, gender, 'streets')} ул., д. {random.randint(1, 200)}, кв. {random.randint(1, 200)}"
    card_type = random.choice(DATA[country]['card_types'])
    prefix = '4' if card_type == 'Visa' else '5' if card_type == 'MasterCard' else '2'
    card_number = f"{prefix}{random_digits(15)}"
    card = f"{card_type} {card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]} | CVV: {random_digits(3)} | Exp: {random.randint(1, 12):02d}/{random.randint(24, 30)}"
    car = f"{random.choice(brands)} {random.choice(models)} ({random.randint(2005, 2023)}) | Номер: {random.randint(100, 999)}{random.choice('ABEKMHOPCTYX')}{random.choice('ABEKMHOPCTYX')}{random.randint(77, 199)}"
    ip = random_ip()
    mac = random_mac()
    bic = random_digits(9)
    inn = random_digits(12)
    snils = f"{random_digits(3)}-{random_digits(3)}-{random_digits(3)} {random_digits(2)}"
    driver = f"{random.randint(10, 99)} {random_digits(6)}"
    return f"""👤 ФИО: {name}
⌛ Возраст: {age}
🌍 Локация: {location}
📞 Номер телефона: {phone}
📧 Email: {email}
📇 Паспорт: {passport}
🏠 Адрес: {address}
💳 Банковская карта: {card}
🚗 Автомобиль: {car}
🌐 IP адрес: {ip}
🔌 MAC адрес: {mac}
🏦 БИК: {bic}
📄 ИНН: {inn}
📋 СНИЛС: {snils}
🚘 Водительские права: {driver}
"""
