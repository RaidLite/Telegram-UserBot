from asyncio import sleep
from json import dumps, loads
from os import path, remove
from re import findall
from httpx import AsyncClient
from telethon import events
from telethon.tl.functions.payments import GetStarGiftsRequest, GetPaymentFormRequest, SendStarsFormRequest
from telethon.tl.types import InputInvoiceStarGift, TextWithEntities
from random import choice

SITE_URL = 'https://cdn.changes.tg/gifts/originals/'

HELP = (
    "💠 Market - Меню\n\n"
    "┣ `.gifts about <айди|random>`\n"
    "┣ `.gifts unique` - показать уникальные подарки\n"
    "┣ `.gifts parse` — пропарсить подарки\n"
    "┗ `.gifts send` <айди> <@юз|айди> <кол-во>"
)

UNIQUE = {
    "5801108895304779062": "I LOVE YOU",
    "5893356958802511476": "Leprechaun Bear",
    "5935895822435615975": "Clown Bear",
    "5800655655995968830": "Winter Bear",
    "5969796561943660080": "Easter Bear",
    "5866352046986232958": "8 March Bear",
    "5922558454332916696": "Christmas Tree",
    "5956217000635139069": "Christmas Bear"
}

parser_state = {"running": False}
get_all_gifts = lambda client: client(GetStarGiftsRequest(hash=0))
get_payment_form = lambda client, invoice: client(GetPaymentFormRequest(invoice=invoice, theme_params=None))
make_invoice = lambda peer, gid: InputInvoiceStarGift(hide_name=False, include_upgrade=False, peer=peer, gift_id=gid, message=TextWithEntities(text="", entities=[]))
encode_json = lambda obj: dumps(obj, indent=2).encode()
parse_entity = lambda t: int(t) if t.lstrip("-").isdigit() else t
cleanup = lambda *fps: [remove(f) for f in fps if path.exists(f)]

def _format_gift(g) -> dict:
    ga = lambda k, d=None: getattr(g, k, d)
    return {
        "id": g.id, "title": ga("title"), "stars": ga("stars", 0),
        "convert_stars": ga("convert_stars", 0), "limited": ga("limited", False),
        "sold_out": ga("sold_out", False), "availability_remains": ga("availability_remains"),
        "availability_total": ga("availability_total"),
        "upgrade_stars": ga("upgrade_stars")
    }

async def _fetch_site_ids() -> list[str]:
    async with AsyncClient() as http:
        r = await http.get(SITE_URL)
        if r.status_code != 200: return []
        return [i.strip().rstrip("/") for i in findall(r'<span class="name">([^<]+)</span>', r.text)]

async def _do_runly(client) -> tuple[bytes, bytes]:
    result = await get_all_gifts(client)
    site_ids = await _fetch_site_ids()
    return encode_json([_format_gift(g) for g in result.gifts]), encode_json({"ids": site_ids})

def init(client):
    async def _send(event, text):
        try: await event.edit(text, parse_mode="md")
        except Exception: await client.send_message(event.chat_id, text, parse_mode="md")

    async def save_and_send(cid, fp, data, label):
        with open(fp, "wb") as f:
            f.write(data)
        return await client.send_file(cid, fp, caption=label)
    
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts unique$"))
    async def cmd_unique(event):
        lines = [f"┣ {id}: {name}" for id, name in UNIQUE.items()]
        if lines:
            lines[-1] = lines[-1].replace("┣ ", "┗ ", 1)
        await _send(
            event,
            "ℹ️ Уникальные подарки:\n" + "\n".join(lines)
        )

    def format_gift_about(g):
        return (
            f"🎁 Тайтл: <b>{g['title']}</b> (ID: <code>{g['id']}</code>)\n"
            f"⭐ Звёзд: {g['stars']}\n"
            f"🔄 Конвертация: {g['convert_stars']} звёзд\n"
            f"⏳ Ограниченный: {'Да' if g['limited'] else 'Нет'}\n"
            f"❌ Распродан: {'Да' if g['sold_out'] else 'Нет'}\n"
            f"📉 Осталось: {g['availability_remains']} из {g['availability_total']}\n"
            f"⬆️ Апгрейд: {g['upgrade_stars']} звёзд\n"
        )
    
    def get_gift_png_url(gid): return f"https://cdn.changes.tg/gifts/originals/{gid}/Original.png"

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts about (\d+|random)$"))
    async def cmd_about(event):
        gift_id = event.pattern_match.group(1)
        try: 
            await event.delete()
        except Exception: 
            pass
        if gift_id == "random":
            try:
                result = await get_all_gifts(client)
                if not result.gifts:
                    await _send(event, "❌ Нет доступных подарков для отображения.")
                    return
                gift = choice(result.gifts)
                info_text = format_gift_about(_format_gift(gift))
                png_url = get_gift_png_url(gift.id)
                await client.send_file(event.chat_id, png_url, caption=info_text, parse_mode="html")
                return
            except Exception as e:
                await _send(event, f"❌ Ошибка при получении случайного подарка: `{e}`")
                return
        else:
            gift_id = int(gift_id)
        try:
            result = await get_all_gifts(client)
            gift = next((g for g in result.gifts if g.id == gift_id), None)
            if gift:
                info_text = format_gift_about(_format_gift(gift))
                png_url = get_gift_png_url(gift_id)
                await client.send_file(event.chat_id, png_url, caption=info_text, parse_mode="html")
                return
            
            try:
                peer = await client.get_input_entity(event.sender_id)
                invoice = make_invoice(peer, gift_id)
                await get_payment_form(client, invoice)
                can_send = True
            except Exception:
                can_send = False
            
            png_url = get_gift_png_url(gift_id)
            try:
                if can_send:
                    caption = f"ℹ️ Информация о подарке с ID {gift_id} не найдена в API, но подарок доступен для отправки."
                else:
                    caption = f"ℹ️ Информация о подарке с ID {gift_id} не найдена в API и подарок недоступен для отправки, но фото найдено."
                await client.send_file(event.chat_id, png_url, caption=caption, parse_mode="html")
            except Exception:
                await _send(event, f"❌ Подарок с ID {gift_id} не найден, и фото недоступно.")
        except Exception as e:
            await _send(event, f"❌ Ошибка: `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts$"))
    async def cmd_root(event):
        await _send(event, "ℹ️ Чтобы узнать команды, напишите `.gifts help`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts help$"))
    async def cmd_help(event): 
        await _send(event, HELP)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts parse$"))
    async def cmd_parse(event):
        if parser_state["running"]:
            await _send(event, "⚠️ Парсер уже работает")
            return

        parser_state["running"] = True
        await _send(event, "⏳ Сбор данных...")

        try:
            api_bytes, site_ids_bytes = await _do_runly(client)
            api_data = loads(api_bytes.decode())
            api_ids = {g["id"] for g in api_data}
            site_ids = set(loads(site_ids_bytes.decode())["ids"])
            
            available_ids = [int(idx) for idx in site_ids if int(idx) not in api_ids]
            avail_bytes = encode_json(available_ids)

            files = [
                ("api_gifts.json", api_bytes, "📄 Данные API"),
                ("all_gifts.json", site_ids_bytes, "📄 Все ID с сайта"),
                ("available_gifts.json", avail_bytes, f"📄 Доступные уникальные подарки")
            ]

            for path_file, data, label in files:
                await save_and_send(event.chat_id, path_file, data, label)
                cleanup(path_file)

            await _send(event, "✅ Готово. Отправлено 3 файла.")
        except Exception as e:
            await _send(event, f"❌ Ошибка: `{e}`")
        finally:
            parser_state["running"] = False

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts send (\d+) (\S+) (\d+)$"))
    async def cmd_send(event):
        _, _, gift_id_val, target, count_str = event.raw_text.split()
        gift_id_val, count = int(gift_id_val), int(count_str)
        await _send(event, f"📦 `{gift_id_val}` → `{target}` × `{count}`...")
        try:
            peer = await client.get_input_entity(parse_entity(target))
            invoice = make_invoice(peer, gift_id_val)
            ok = 0
            for i in range(count):
                try:
                    form = await get_payment_form(client, invoice)
                    await client(SendStarsFormRequest(
                        form_id=form.form_id, 
                        invoice=invoice)
                    )
                    ok += 1
                    if i < count - 1: await sleep(1)
                except Exception as e:
                    await _send(event, f"❌ Шаг {i + 1}: `{e}`")
                    break
            await _send(event, f"✅ Отправлено `{ok}/{count}` → `{target}`")
        except Exception as e:
            await _send(event, f"❌ `{e}`")