from asyncio import Semaphore, gather, sleep, ensure_future
from collections import deque
from datetime import datetime
from json import dumps
from json import loads
from os import path, remove
from pathlib import Path
from re import findall
from time import time
from httpx import AsyncClient
from pystyle import Colors, Colorate
from telethon import events
from telethon.tl.functions.payments import (
    GetResaleStarGiftsRequest,
    GetStarGiftsRequest,
    GetPaymentFormRequest
)
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import (
    InputInvoiceStarGift,
    TextWithEntities,
    StarsAmount
)

p_g = lambda text: print(Colorate.Horizontal(Colors.green_to_blue, text))
DB_FILE = "seen.txt"
SKIP_FILE = "expensive.txt"
gift_price = "price"
gift_slug = "slug"
gift_id = "id"
MAX_PRICE = 350
MIN_EXPENSIVE = 450
CONCURRENCY = 25
INSTANT_PRICE = 300
url = 'https://cdn.changes.tg/gifts/originals/'
HELP = (
    "🎁 **Market**\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "**〔 Монитор 〕**\n"
    "  `.gifts mon start` — запустить\n"
    "  `.gifts mon stop` — остановить\n"
    "  `.gifts mon status` — статус\n"
    "  `.gifts mon set max 500` — макс цена\n"
    "  `.gifts mon set instant 50` — мгновенная\n"
    "  `.gifts mon set expensive 5000` — порог дорогого\n"
    "  `.gifts mon set concurrency 5` — параллельность\n"
    "\n"
    "**〔 Парсер 〕**\n"
    "  `.gifts parse all` — полный\n"
    "  `.gifts parse info` — доступность\n"
    "\n"
    "**〔 Отправка 〕**\n"
    "  `.gifts send <id> <@user|id> <кол-во>`\n"
    "\n"
    "**〔 Лог 〕**\n"
    "  `.gifts log [N]` — последние N записей"
)

activity_log = deque(maxlen=200)
monitor_state = {
    "running": False,
    "total": 0,
    "active": 0,
    "ignored": 0,
    "sent": 0,
    "errors": 0,
    "last_tick": None,
    "max_price": MAX_PRICE,
    "instant_price": INSTANT_PRICE,
    "min_expensive": MIN_EXPENSIVE,
    "concurrency": CONCURRENCY,
}
parser_state = {
    "running": False,
    "step": None,
    "progress": 0,
    "total": 0,
    "nft_found": 0,
    "available_found": 0,
}


async def get_all_gifts_not_hidden(client): return await client(GetStarGiftsRequest(hash=0))
async def payment_request(invoice, client): return await client(GetPaymentFormRequest(invoice=invoice, theme_params=None))
def save(p, data): Path(p).write_text(dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
async def get_invoice(peer, gg_id): return InputInvoiceStarGift(hide_name=False, include_upgrade=False, peer=peer, gift_id=gg_id, message=TextWithEntities(text="", entities=[]))
def _log(tag: str, msg: str) -> None: activity_log.appendleft({"ts": time(), "tag": tag, "msg": msg})

async def get_price(client, gift_id):
    try:
        resale = await client(GetResaleStarGiftsRequest(gift_id=gift_id, offset="", limit=1, sort_by_price=True, sort_by_num=True))
        if resale.gifts:
            item = resale.gifts[0]
            p = next((e.amount for e in getattr(item, "resell_amount", []) if isinstance(e, StarsAmount)), None)

            return {
                "price": p,
                "slug": item.slug,
                "id": gift_id
            }

    except Exception as e: p_g(f"[!] Ошибка запроса ID {gift_id}: {e}")
    return None

def load_data(file_path: str) -> set:
    if path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file if line.strip())
    return set()


def save_data(file_path: str, item: str):
    with open(file_path, 'a', encoding='utf-8') as file: file.write(f"{item}\n")


def _format_gift(g: object) -> dict:
    return {
        "id": g.id,
        "title": getattr(g, "title", None),
        "stars": getattr(g, "stars", 0),
        "convert_stars": getattr(g, "convert_stars", 0),
        "limited": getattr(g, "limited", False),
        "sold_out": getattr(g, "sold_out", False),
        "availability_remains": getattr(g, "availability_remains", None),
        "availability_total": getattr(g, "availability_total", None),
        "first_sale_date": str(g.first_sale_date) if getattr(g, "first_sale_date", None) else None,
        "last_sale_date": str(g.last_sale_date) if getattr(g, "last_sale_date", None) else None,
        "upgrade_stars": getattr(g, "upgrade_stars", None),
        "birthday": getattr(g, "birthday", False),
        "require_premium": getattr(g, "require_premium", False),
        "per_user_remains": getattr(g, "per_user_remains", None),
    }


def _get_ids_from_bytes(data: bytes) -> list[int]:
    try: return [int(i) for i in loads(data.decode()).get("ids", [])]
    except (ValueError, KeyError): return []


async def _fetch_site_ids() -> list[str]:
    async with AsyncClient() as http:
        r = await http.get(url)
        if r.status_code != 200: return []
        ids = findall(r'<span class="name">([^<]+)</span>', r.text)
        return [i.strip().rstrip("/") for i in ids]


async def _do_runly(client: object) -> tuple[bytes, bytes]:
    result = await get_all_gifts_not_hidden(client)
    site_ids = await _fetch_site_ids()
    api_bytes = dumps([_format_gift(g) for g in result.gifts], indent=2).encode()
    all_bytes = dumps({"ids": site_ids}, indent=2).encode()
    _log("PARSER", f"Загружено {len(result.gifts)} гифтов, {len(site_ids)} ID с сайта")
    return api_bytes, all_bytes


async def _do_info_gifts(client: object, ids_bytes: bytes) -> list[int]:
    available_ids: list[int] = []
    peer = await client.get_input_entity("me")
    all_gifts = await get_all_gifts_not_hidden(client)
    gifts_dict = {g.id: g for g in all_gifts.gifts}
    ids = _get_ids_from_bytes(ids_bytes)
    parser_state["total"] = len(ids)
    for i, g_id in enumerate(ids):
        parser_state["progress"] = i + 1
        gift_obj = gifts_dict.get(g_id)
        if not gift_obj:
            try:
                await payment_request(await get_invoice(peer, g_id), client)
                available_ids.append(g_id)
            except Exception:
                pass
            finally:
                await sleep(0.1)
            continue
        stars = getattr(gift_obj, "stars", None)
        if stars is not None and int(stars) >= 0:
            continue
        if not getattr(gift_obj, "sold_out", False):
            available_ids.append(g_id)
        await sleep(0.1)
    parser_state["available_found"] = len(available_ids)
    _log("PARSER", f"Доступно гифтов: {len(available_ids)}")
    return available_ids


async def _do_nftparse(client: object, ids_bytes: bytes) -> list[int]:
    gifts = await get_all_gifts_not_hidden(client)
    gifts_dict = {g.id: g for g in gifts.gifts}
    found_nft_ids: list[int] = []
    ids = _get_ids_from_bytes(ids_bytes)
    parser_state["total"] = len(ids)
    for i, g_id in enumerate(ids):
        parser_state["progress"] = i + 1
        gift_obj = gifts_dict.get(g_id)
        if gift_obj and getattr(gift_obj, "title", None) and getattr(gift_obj, "limited", False):
            found_nft_ids.append(g_id)
    parser_state["nft_found"] = len(found_nft_ids)
    _log("PARSER", f"NFT гифтов найдено: {len(found_nft_ids)}")
    return found_nft_ids


async def _send_notify(client: object, peer: object, item: dict) -> None:
    await client.send_message(peer,
                              f"💎 **Дешёвый NFT**\n"
                              f"━━━━━━━━━━━━━━━━━━━━\n"
                              f"💰 `{item[gift_price]} ⭐`\n"
                              f"🔗 https://t.me/nft/{item[gift_slug]}",
                              parse_mode="md"
    )


async def _monitor_loop(client: object, peer: object) -> None:
    monitor_state["running"] = True
    seen_slugs = load_data(DB_FILE)
    expensive_ids = load_data(SKIP_FILE)
    sem = Semaphore(monitor_state["concurrency"])
    _log("MONITOR", "Запущен")

    while monitor_state["running"]:
        try:
            resale = await get_all_gifts_not_hidden(client)
            all_gifts = [g for g in resale.gifts if getattr(g, "limited", False)]
            active_ids = [g.id for g in all_gifts if str(g.id) not in expensive_ids]
            monitor_state["total"] = len(all_gifts)
            monitor_state["active"] = len(active_ids)
            monitor_state["ignored"] = len(expensive_ids)
            monitor_state["last_tick"] = time()

            async def check(gid: int) -> dict | None:
                async with sem:
                    info = await get_price(client, gid)
                    if not info or info[gift_price] is None:
                        return None
                    price: int = int(info[gift_price])
                    if price >= monitor_state["min_expensive"]:
                        if info[gift_id] not in expensive_ids:
                            expensive_ids.add(info[gift_id])
                            save_data(SKIP_FILE, str(info[gift_id]))
                        return None
                    if price <= monitor_state["instant_price"]:
                        if info[gift_slug] not in seen_slugs:
                            seen_slugs.add(info[gift_slug])
                            save_data(DB_FILE, info[gift_slug])
                            await _send_notify(client, peer, info)
                            monitor_state["sent"] += 1
                            _log("INSTANT", f"{info[gift_slug]} — {price}⭐")
                        return None
                    if price <= monitor_state["max_price"] and info[gift_slug] not in seen_slugs:
                        return info
                    return None

            results = await gather(*[check(i) for i in active_ids])
            for best in sorted((r for r in results if r), key=lambda x: x[gift_price]):
                if best[gift_slug] not in seen_slugs:
                    recheck = await get_price(client, best[gift_id])
                    if (
                            recheck
                            and recheck[gift_slug] == best[gift_slug]
                            and int(recheck[gift_price]) <= monitor_state["max_price"]
                    ):
                        await _send_notify(client, peer, best)
                        seen_slugs.add(best[gift_slug])
                        save_data(DB_FILE, best[gift_slug])
                        monitor_state["sent"] += 1
                        _log("SENT", f"{best[gift_slug]} — {best[gift_price]}⭐")

        except Exception as e:
            monitor_state["errors"] += 1
            _log("ERROR", str(e))

    _log("MONITOR", "Остановлен")


def init(client):
    async def send(event, text: str) -> None:
        try: await event.edit(text, parse_mode="md")
        except Exception: await client.send_message(event.chat_id, text, parse_mode="md")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts help$"))
    async def cmd_help(event): await send(event, HELP)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts mon start$"))
    async def cmd_mon_start(event):
        if monitor_state["running"]:
            await send(event, "⚠️ Монитор уже запущен")
            return
        peer = await event.get_input_chat()
        await send(event, "🟢 **Монитор запущен**")
        ensure_future(_monitor_loop(client, peer))

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts mon stop$"))
    async def cmd_mon_stop(event):
        monitor_state["running"] = False
        await send(event, "🔴 **Монитор остановлен**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts mon status$"))
    async def cmd_mon_status(event):
        s = monitor_state
        last = datetime.fromtimestamp(s["last_tick"]).strftime("%H:%M:%S") if s["last_tick"] else "—"
        icon = "🟢" if s["running"] else "🔴"
        await send(event, (
            f"🎁 **Market** {icon} {'работает' if s['running'] else 'остановлен'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"NFT всего    `{s['total']}`\n"
            f"Проверяется  `{s['active']}`\n"
            f"В игноре     `{s['ignored']}`\n"
            f"Отправлено   `{s['sent']}`\n"
            f"Ошибок       `{s['errors']}`\n"
            f"Тик          `{last}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Макс цена    `{s['max_price']} ⭐`\n"
            f"Мгновенная   `{s['instant_price']} ⭐`\n"
            f"Дорогой      `{s['min_expensive']} ⭐`\n"
            f"Параллельно  `{s['concurrency']}`"
        ))

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts mon set (\w+) (\S+)$"))
    async def cmd_mon_set(event):
        key_map = {
            "max": ("max_price", int),
            "instant": ("instant_price", int),
            "expensive": ("min_expensive", int),
            "concurrency": ("concurrency", int),
        }
        _, _, _, param, value = event.raw_text.split()
        if param not in key_map:
            await send(event, f"❌ Неизвестный параметр `{param}`")
            return
        state_key, cast = key_map[param]
        try:
            monitor_state[state_key] = cast(value)
            _log("CONFIG", f"{state_key} = {value}")
            await send(event, f"✅ `{param}` → `{value}`")
        except ValueError:
            await send(event, f"❌ Неверное значение `{value}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts parse (all|info)$"))
    async def cmd_parse(event):
        sub = event.raw_text.split()[2]
        if parser_state["running"]:
            await send(event, "⚠️ Парсер уже работает")
            return

        parser_state.update({"running": True, "progress": 0, "step": None})
        await send(event, f"⏳ Парсинг `{sub}`...")
        all_bytes: bytes = dumps({"ids": []}).encode()

        try:
            if sub == "all":
                parser_state["step"] = "runly"
                api_bytes, all_bytes = await _do_runly(client)
                path1 = "api_gifts.json"
                path2 = "all_gifts.json"
                with open(path1, "wb") as file: file.write(api_bytes)
                with open(path2, "wb") as file: file.write(all_bytes)

                try:
                    await client.send_file(event.chat_id, path1, caption="📄 `api_gifts.json`")
                    await client.send_file(event.chat_id, path2, caption="📄 `all_gifts.json`")
                finally:
                    if path.exists(path1): remove(path1)
                    if path.exists(path2): remove(path2)

            if sub in ("all", "info"):
                parser_state["step"] = "info"
                available_ids = await _do_info_gifts(client, all_bytes)
                info_bytes = dumps(available_ids, indent=4).encode()

                path3 = "available_gifts.json"

                with open(path3, "wb") as f:
                    f.write(info_bytes)

                try:
                    await client.send_file(
                        event.chat_id,
                        path3,
                        caption=f"📄 `available_gifts.json` — {len(available_ids)} доступных",
                    )
                finally:
                    if path.exists(path3):
                        remove(path3)

            s = parser_state
            await send(event, (
                f"✅ **Парсинг завершён** — `{sub}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Доступно  `{s['available_found']}`"
            ))
        except Exception as e:
            _log("PARSER", f"Ошибка: {e}")
            await send(event, f"❌ `{e}`")
        finally:
            parser_state.update({"running": False, "step": None})

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts send (\d+) (\S+) (\d+)$"))
    async def cmd_send(event):
        _, _, gift_id_val, target, count_str = event.raw_text.split()
        gift_id_val, count = int(gift_id_val), int(count_str)
        await send(event, f"📦 `{gift_id_val}` → `{target}` × `{count}`...")
        try:
            entity = int(target) if target.lstrip("-").isdigit() else target
            peer = await client.get_input_entity(entity)
            invoice = InputInvoiceStarGift(
                hide_name=False,
                include_upgrade=False,
                peer=peer,
                gift_id=gift_id_val,
                message=TextWithEntities(text="", entities=[]),
            )
            ok = 0
            for i in range(count):
                try:
                    form = await payment_request(invoice, client)
                    await client(SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
                    ok += 1
                    _log("SEND", f"[{i + 1}/{count}] → {target}")
                    if i < count - 1:
                        await sleep(1)
                except Exception as e:
                    _log("SEND_ERR", str(e))
                    await send(event, f"❌ Шаг {i + 1}: `{e}`")
                    break
            await send(event, f"✅ Отправлено `{ok}/{count}` → `{target}`")
        except Exception as e:
            await send(event, f"❌ `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.gifts log ?(\d*)$"))
    async def cmd_log(event):
        parts = event.raw_text.split()
        n = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 10
        entries = list(activity_log)[:n]
        if not entries:
            await send(event, "📭 Лог пустой")
            return
        lines = [
            f"`{datetime.fromtimestamp(e['ts']).strftime('%H:%M:%S')}` **{e['tag']}**  {e['msg']}"
            for e in entries
        ]
        await send(event, "🎁 **Market** — лог\n━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines))
