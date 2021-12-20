from email.message import EmailMessage
from typing import Any, Callable, Coroutine, Dict, Optional
from fastapi.param_functions import Form
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from secrets import token_bytes, token_hex
from starlette.responses import JSONResponse, RedirectResponse, Response
from dataclasses import dataclass
from validate_email_address import validate_email
from pydantic import BaseModel
import asyncio
import os
import asyncpg
import aioredis
import fastapi
import aiohttp
import datetime
import aiosmtplib
import dotenv

dotenv.load_dotenv()

vipay_url = "https://vipay.loca.lt/"
redirect = "{}/api/pay".format(os.environ["S_HOST"])
pay_url = vipay_url + "pay?transaction_id={0}"
hostname = os.environ["S_HOSTNAME"]
user = os.environ["S_USERNAME"]
passwd = os.environ["S_PASSWORD"]

class state:
    db: asyncpg.Pool
    redis: aioredis.Redis
    http: aiohttp.ClientSession
    email: aiosmtplib.SMTP
    email_task: asyncio.Task

async def keep_alive():
    while True:
        try:
            await state.email.ehlo()
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            return

@dataclass
class Transaction:
    id: str
    amount: int
    redirect: str
    description: Optional[str]
    status: bool


class Item(BaseModel):
    id: str
    quantity: int


async def create_transaction(amount: int):
    async with state.http.post(
        vipay_url + "api/transactions", json={"redirect": redirect, "amount": amount}
    ) as resp:
        return Transaction(**(await resp.json()))


app = fastapi.FastAPI()


@app.middleware("http")
async def session_item_adder(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
):
    if "items" not in request.session:
        request.session["items"] = {}
    return await call_next(request)


app.add_middleware(SessionMiddleware, secret_key=token_bytes(10))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def on_startup():
    state.http = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
    state.db = await asyncpg.create_pool(
        "postgres://postgres@192.168.0.2/santo-stefanus", max_size=2, min_size=1
    )
    state.email = aiosmtplib.SMTP(hostname=hostname, username=user, password=passwd, use_tls=True)
    await state.email.connect()
    state.email_task = asyncio.create_task(keep_alive())


@app.on_event("shutdown")
async def on_shutdown():
    state.email.close()
    state.email_task.cancel()
    await asyncio.gather(state.http.close(), state.db.close())


@app.get("/api/items")
async def api_items_get():
    return [dict(i) for i in await state.db.fetch("SELECT * FROM barang")]


@app.get("/api/items/{id}")
async def api_item_get(id: str):
    item = await state.db.fetchrow("SELECT * FROM barang WHERE id = $1", id)
    if not item:
        raise fastapi.HTTPException(404, detail="item not found")
    return dict(item)


@app.get("/api/cart")
async def api_sessions_get(request: Request, id: Optional[str] = None):
    if id is None:
        return request.session["items"]
    item = request.session["items"].get(id)
    if not item:
        raise fastapi.HTTPException(404, detail="item not found")
    return item


@app.post("/api/cart")
async def api_sessions_post(request: Request, item: Item):
    try:
        request.session["items"][item.id]["quantity"] += item.quantity
    except KeyError:
        name, price = await state.db.fetchrow(
            "SELECT name, price FROM barang WHERE id = $1", item.id
        )
        request.session["items"][item.id] = {
            **item.dict(),
            "name": name,
            "price": price,
        }
    return JSONResponse({"status": True}, 201)


@app.delete("/api/cart")
async def api_sessions_post(request: Request, id: str, quantity: Optional[int] = None):
    if quantity:
        try:
            request.session["items"][id]["quantity"] -= quantity
        except KeyError:
            raise fastapi.HTTPException(404, "item not found")
    else:
        request.session["items"].pop(id, None)
    return Response(status_code=204)


@app.post("/api/pay")
async def beli_post(
    request: Request,
    fullname: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    description: Optional[str] = Form(None),
):
    valid = await asyncio.to_thread(validate_email, email, verify=True)
    if not valid:
        return fastapi.HTTPException(404, "email not found")
    created_at = datetime.datetime.now()
    items: Dict[str, Dict] = request.session["items"]
    id = token_hex(8)
    async with state.db.acquire() as conn:
        conn: asyncpg.Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO pemesanan VALUES ($1, $2, $3, $4, $5, $6, $7)",
                id,
                fullname,
                address,
                email,
                phone,
                description,
                created_at,
            )
            await conn.executemany(
                "INSERT INTO pemesanan_items (pemesanan, total, price, barang) VALUES ($1, $2, $3, $4)",
                [
                    (id, i["quantity"], i["price"] * i["quantity"], i["id"])
                    for i in items.values()
                ]
            )
            await conn.executemany(
                "UPDATE barang SET total = total - $1 WHERE id = $2", [(i["quantity"], i["id"]) for i in items.values()]
            )
    transaction = await create_transaction(sum((i["price"] * i["quantity"] for i in items.values())))
    request.session["transaction"] = {
        "id": id,
        "fullname": fullname,
        "email": email,
        "total_price": transaction.amount,
        "items": [i for i in request.session["items"].values()]
    }
    request.session["items"].clear()
    return RedirectResponse(pay_url.format(transaction.id), 301)

@app.get("/api/pay")
async def beli_get(request: Request):
    transaction = request.session.get("transaction")
    if transaction is None:
        raise fastapi.HTTPException(404, "not in a transaction")
    msg = EmailMessage()
    msg["Subject"] = f"Information order {transaction['id']}"
    msg["From"] = user
    msg["To"] = transaction["email"]

    items = "<br>".join([f"{i['name']}: {i['quantity']:,}x Rp.{i['quantity']*i['price']:,}" for i in transaction["items"]])
    content = f"""
    Hai {transaction["fullname"]}!, pesanan anda sedang diproses mohon menunggu dan terima kasih telah berbelanja!
    <h2 style="border-bottom: solid rgb(200,200,200) 1px">Receipt</h2>
    Total: <b>{transaction["total_price"]}</b><br>

    <h2>Items</h2>
    {items}
    """
    msg.set_content(content)
    msg.set_type("text/html")
    await state.email.send_message(msg)
    return RedirectResponse("/pay/done", 301)