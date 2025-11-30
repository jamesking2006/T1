# T1 — Covered Call PWA (Alpaca)

Public repo ready to deploy.

## Quick deploy (Render)
1. Create Render Web Service → Connect this GitHub repo → Docker.
2. Set environment variables (Render > Dashboard > Environment):
   - APCA_API_KEY_ID = <your Alpaca PAPER key id>
   - APCA_API_SECRET_KEY = <your Alpaca PAPER secret>
   - ALPACA_BASE_URL = https://paper-api.alpaca.markets
   - MODE = PAPER
3. Deploy. Visit the provided URL on your iPhone and **Share → Add to Home Screen**.

## Notes
- Options endpoints are placeholders — request Alpaca options access and implement those endpoints (I can provide code).
- Paper-first recommended.
