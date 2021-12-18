import json
from typing import Optional
from fastapi.param_functions import Form
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from secrets import token_bytes, token_hex
from starlette.responses import JSONResponse, RedirectResponse
from dataclasses import dataclass
from pydantic import BaseModel
import asyncio
import asyncpg
import aioredis
import fastapi
import aiohttp
import datetime

vipay_url = "http://192.168.0.2:8000/"
redirect = "http://localhost:8000/pay/done"
pay_url = vipay_url + "pay?transaction_id={0}"


class state:
    db: asyncpg.Pool
    redis: aioredis.Redis
    http: aiohttp.ClientSession


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
    state.http = aiohttp.ClientSession()
    state.db = await asyncpg.create_pool(
        "postgres://void:void@localhost/santo-stefanus", max_size=2, min_size=1
    )


@app.on_event("shutdown")
async def on_shutdown():
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
    await asyncio.sleep(2)
    if id is None:
        return request.session
    item = request.session.get(id)
    if not item:
        raise fastapi.HTTPException(404, detail="item not found")
    return item
    
@app.post("/api/cart")
async def api_sessions_post(request: Request, item: Item):
    request.session[item.id] = item.dict()
    return JSONResponse({"status": True}, 201)

@app.delete("/api/cart")
async def api_sessions_post(request: Request, id: str):
    request.session.pop(id, None)
    return JSONResponse({"status": True}, 201)

@app.post("/api/pay")
async def beli_post(
    request: Request,
    fullname: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    description: Optional[str] = Form(None)
):
    created_at = datetime.datetime.now()
    id = token_hex(8)
    async with state.db.acquire() as conn:
        conn: asyncpg.Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO pemesanan VALUES ($1, $2, $3, $4, $5, $6, $7)",
                id, fullname, address, email, phone, description, created_at
            )
    transaction = await create_transaction(1000)
    return RedirectResponse(pay_url.format(transaction.id), 301)
