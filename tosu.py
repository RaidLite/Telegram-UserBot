from asyncio import sleep, iscoroutine, get_running_loop, run
from importlib.util import module_from_spec, spec_from_file_location
from os import listdir, makedirs, system, name
from pathlib import Path
from typing import Callable
from pystyle import Colorate, Colors
from qrcode import QRCode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from traceback import print_exc

API_HASH = 'bf654fd64259c65b85c8899ff081a437'
API_ID = 21341528
BANNER = """
    ███      ▄██████▄     ▄████████ ███    █▄  
▀█████████▄ ███    ███   ███    ███ ███    ███ 
   ▀███▀▀██ ███    ███   ███    █▀  ███    ███ 
    ███   ▀ ███    ███   ███        ███    ███ 
    ███     ███    ███ ▀███████████ ███    ███ 
    ███     ███    ███          ███ ███    ███ 
    ███     ███    ███    ▄█    ███ ███    ███ 
   ▄████▀    ▀██████▀   ▄████████▀  ████████▀  
                                               
                                                                                                                   
1. Запустить            
2. Зарегать акк                      
0. Выйти                  
"""

colored = lambda prompt: Colorate.Vertical(Colors.blue_to_cyan, prompt)
print_colored = lambda text: print(colored(text) + " ")
clear = lambda: system('cls' if name == 'nt' else 'clear')

async def create_client(session_name: str):
    makedirs("sessions", exist_ok=True)
    session_file = Path("sessions") / session_name
    client = TelegramClient(str(session_file), API_ID, API_HASH)
    await client.connect()
    return client


async def async_input(prompt: str = "") -> str:
    colored_prompt = colored(prompt)
    loop = get_running_loop()
    return await loop.run_in_executor(None, input, colored_prompt + " ")


async def call_maybe_async(func: Callable, *args):
    result = func(*args)
    if iscoroutine(result): await result

async def userbot():
    while True:
        clear()
        makedirs("sessions", exist_ok=True)
        print_colored(BANNER)
        print()
        match await async_input("Введи выбор --> "):
            case "1": await use_registered_account()
            case "2": await register_account()
            case "0": break
            case _: print_colored("Неверный ввод. Введи 1, 2 или 3.")


async def use_registered_account():
    sessions = [f for f in listdir("sessions") if f.endswith(".session")]
    if not sessions:
        print_colored("Нет доступных аккаунтов")
        return

    for i, s in enumerate(sessions, 1): print_colored(f"{i}. {s}")

    try:
        idx = int(await async_input("Выбери аккаунт: ")) - 1
        if not (0 <= idx < len(sessions)): raise ValueError
    except ValueError:
        print_colored("Некорректный номер аккаунта")
        return

    module_path = Path("modules")
    session_name = Path(sessions[idx]).stem
    client = await create_client(session_name)

    if not await client.is_user_authorized():
        print_colored(f"Сессия {session_name} невалидна или удалена!")
        await client.disconnect()
        return

    try: await load_modules(client, module_path)
    except KeyboardInterrupt: print_colored("\nОстановка...")
    finally: await client.disconnect()


async def register_account():
    clear()
    print_colored('РЕГИСТРАЦИЯ НОВОГО АККАУНТА')
    sid = await async_input('Введите название для сессии: ')
    client = await create_client(sid)

    try:
        if not await client.is_user_authorized():
            print_colored("\nВыберите способ входа:")
            print_colored("1. QR-код")
            print_colored("2. Номер телефона (иногда бывают проблемы)")

            choice = await async_input("\nВаш выбор: ")

            if choice == "1":
                qr = await client.qr_login()
                print_colored("\nОтсканируйте этот QR-код в приложении:")
                qr_gen = QRCode()
                qr_gen.add_data(qr.url)
                qr_gen.make(fit=True)
                qr_gen.print_ascii(invert=True)

                try:
                    await qr.wait()
                except SessionPasswordNeededError:
                    pw = await async_input('\n[!] Введите облачный пароль: ')
                    await client.sign_in(password=pw)

            elif choice == "2":
                phone = await async_input("Введите номер телефона (с +): ")
                await client.send_code_request(phone)
                code = await async_input("Введите код подтверждения: ")
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    pw = await async_input('\n[!] Введите облачный пароль: ')
                    await client.sign_in(password=pw)
            else:
                print_colored("Неверный выбор.")
                return

        print_colored('\nАккаунт успешно сохранен!')
        await async_input('Нажмите Enter чтобы вернуться в меню...')

    except Exception as e:
        print_colored(f'Произошла ошибка: {e}')
        await async_input('Нажмите Enter...')
    finally:
        await client.disconnect()

async def load_modules(client: TelegramClient, path: Path):
    if not path.is_dir():
        print_colored(f"Папка модулей не найдена: {path}")
        return

    print_colored(f"Аккаунт {client.session.filename} запущен")
    modules = list(path.glob("*.py"))
    active = 0

    for file in modules:
        try:
            spec = spec_from_file_location(file.stem, file)
            if spec is None or spec.loader is None: raise ImportError("Не удалось создать spec")
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            if not hasattr(module, "init"):
                print_colored(f"{file.name}: нет функции init(client)")
                continue
            await call_maybe_async(module.init, client)
            active += 1
        except Exception as e:
            print_exc()
            print(f"Ошибка загрузки модуля {file.name}: {e}")

    print_colored(f"Загружено модулей: {active}/{len(modules)}")
    print_colored("Бот работает. Ctrl+C для остановки.")

    try:
        while True: await sleep(1)
    finally: print_colored("Остановка модулей...")

if __name__ == "__main__": run(userbot())