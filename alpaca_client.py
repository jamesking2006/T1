import requests, logging
from typing import Optional

logger = logging.getLogger("alpaca_client")

class AlpacaClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str="https://paper-api.alpaca.markets"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json"
        })

    def get_latest_trade(self, symbol: str) -> Optional[float]:
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest"
        r = self.session.get(url)
        if r.status_code == 200:
            return float(r.json()['trade']['p'])
        logger.warning("get_latest_trade failed for %s: %s", symbol, r.text)
        return None

    def place_stock_order(self, symbol: str, qty: int, side: str="buy", type:str="market", time_in_force:str="day"):
        url = f"{self.base_url}/v2/orders"
        payload = {"symbol": symbol, "qty": qty, "side": side, "type": type, "time_in_force": time_in_force}
        r = self.session.post(url, json=payload)
        logger.info("place_stock_order %s %s -> %s", side, symbol, r.status_code)
        try:
            return r.json()
        except:
            return {"error": r.text}

    # Options endpoints are placeholders — implement when Alpaca options access enabled
    def get_option_chain(self, symbol: str, expiry: str=None):
        logger.info("get_option_chain placeholder for %s expiry=%s", symbol, expiry)
        return {"symbol": symbol, "expirations": [], "options": []}

    def place_option_order(self, option_symbol: str, qty: int, side: str="sell"):
        logger.info("place_option_order placeholder for %s qty=%s side=%s", option_symbol, qty, side)
        return {"status":"simulated", "option_symbol": option_symbol, "qty": qty, "side": side}
