from asyncio import sleep
from json import dumps, loads
from os import path, remove
from re import findall
from httpx import AsyncClient
from telethon import events
from telethon.tl.functions.payments import GetStarGiftsRequest, GetPaymentFormRequest, SendStarsFormRequest
from telethon.tl.types import InputInvoiceStarGift, TextWithEntities

SITE_URL = 'https://cdn.changes.tg/gifts/originals/'
HELP = (
    "💠 Market - Меню\n"
    "┣ .gifts parse all — пропарсить подарки\n"
    "┗ .gifts send <id> <@user|id> <кол-во>"
)

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

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts help$"))
    async def cmd_help(event): await _send(event, HELP)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts parse all$"))
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
                ("available_gifts.json", avail_bytes, f"📄 Доступные ({len(available_ids)} шт.)")
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
                    await client(SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
                    ok += 1
                    if i < count - 1: await sleep(1)
                except Exception as e:
                    await _send(event, f"❌ Шаг {i + 1}: `{e}`")
                    break
            await _send(event, f"✅ Отправлено `{ok}/{count}` → `{target}`")
        except Exception as e:
            await _send(event, f"❌ `{e}`")