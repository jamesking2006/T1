import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from datetime import datetime

from alpaca_client import AlpacaClient
from strategy import CoveredCallEngine
from db import init_db, SessionLocal, Position

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("t1")

app = FastAPI(title="T1 Covered Call")

app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

MODE = os.environ.get("MODE", "PAPER").upper()
if MODE == "LIVE":
    API_KEY = os.environ.get("APCA_LIVE_API_KEY_ID")
    API_SECRET = os.environ.get("APCA_LIVE_API_SECRET_KEY")
    BASE = os.environ.get("ALPACA_LIVE_BASE", "https://api.alpaca.markets")
else:
    API_KEY = os.environ.get("APCA_API_KEY_ID")
    API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
    BASE = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

alpaca = AlpacaClient(API_KEY, API_SECRET, BASE)
engine = CoveredCallEngine(alpaca_client=alpaca)

@app.on_event("startup")
async def startup():
    asyncio.create_task(engine.scheduler_loop())

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/api/status")
async def status():
    return {"running": engine.is_running, "last_run": engine.last_run.isoformat() if engine.last_run else None, "mode": MODE}

@app.post("/api/start")
async def start_engine():
    engine.start()
    return {"status":"started"}

@app.post("/api/pause")
async def pause_engine():
    engine.pause()
    return {"status":"paused"}

@app.post("/api/stop")
async def stop_engine():
    engine.stop()
    return {"status":"stopped"}

@app.get("/api/positions")
async def positions():
    db = SessionLocal()
    rows = db.query(Position).all()
    out = []
    for r in rows:
        out.append({"id": r.id, "symbol": r.symbol, "qty": r.qty, "entry_price": r.entry_price, "metadata": r.metadata, "created_at": r.created_at.isoformat()})
    db.close()
    return JSONResponse(out)

@app.post("/api/manual/close/{pos_id}")
async def manual_close(pos_id: int):
    await engine.manual_close_by_id(pos_id)
    return {"status":"close_requested", "id": pos_id}
