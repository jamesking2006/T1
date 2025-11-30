import asyncio, logging
from datetime import datetime
from db import SessionLocal, Position

logger = logging.getLogger("strategy")

class CoveredCallEngine:
    def __init__(self, alpaca_client, tickers=["SPY","QQQ","AAPL"]):
        self.alpaca = alpaca_client
        self.tickers = tickers
        self.is_running = False
        self.last_run = None
        self._pause = False
        self._stop = False

        self.profit_take_pct = 0.6
        self.force_close_days = 2

    def start(self):
        self.is_running = True
        self._pause = False
        logger.info("Engine started")

    def pause(self):
        self._pause = True
        logger.info("Engine paused")

    def stop(self):
        self._stop = True
        self.is_running = False
        logger.info("Engine stopped")

    async def scheduler_loop(self):
        while True:
            if self._stop:
                break
            if self._pause:
                await asyncio.sleep(5)
                continue
            try:
                await self.run_once()
            except Exception as e:
                logger.exception("run_once error: %s", e)
            await asyncio.sleep(60)
        logger.info("scheduler loop ended")

    async def run_once(self):
        self.last_run = datetime.utcnow()
        logger.info("run_once at %s", self.last_run.isoformat())
        for symbol in self.tickers:
            price = self.alpaca.get_latest_trade(symbol)
            if price is None:
                continue
            chain = self.alpaca.get_option_chain(symbol)
            candidate = self.select_candidate(chain, price)
            if candidate:
                await self.open_covered_call(symbol, price, candidate)
        await self.monitor_positions()

    def select_candidate(self, chain, price):
        # placeholder: no chain data — skip until options API implemented
        return None

    async def open_covered_call(self, symbol, price, call_option):
        qty = 100
        self.alpaca.place_stock_order(symbol, qty, side="buy")
        self.alpaca.place_option_order(call_option.get("symbol","UNKNOWN"), 1, side="sell")
        db = SessionLocal()
        p = Position(symbol=symbol, type="covered_call", qty=qty, entry_price=price, metadata=str({"call": call_option}))
        db.add(p); db.commit(); db.refresh(p); db.close()
        logger.info("opened covered call %s", p.id)

    async def monitor_positions(self):
        db = SessionLocal()
        rows = db.query(Position).filter(Position.type=="covered_call").all()
        db.close()

    async def manual_close_by_id(self, pos_id):
        db = SessionLocal()
        p = db.query(Position).filter(Position.id==pos_id).first()
        if not p:
            db.close(); return
        db.delete(p); db.commit(); db.close()
