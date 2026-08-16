import os
import re
import sys
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION = os.getenv("TELEGRAM_SESSION", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
PASSWORD = os.getenv("TELEGRAM_PASSWORD", "")
BOT_USERNAME = os.getenv("GETBRIDGES_BOT", "GetBridgesBot")
REQUESTS = ["obfs4 bridges", "webtunnel bridges"]


def looks_like_bridges(text):
    if not text:
        return False
    if "No bridges" in text or "no bridges" in text:
        return True
    bridge_lines = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or len(line) < 10:
            continue
        if re.search(r'\d+\.\d+\.\d+\.\d+|\[[0-9a-fA-F:]+\]|https?://|obfs4|webtunnel', line):
            bridge_lines += 1
    return bridge_lines > 0


async def ask_bot(client):
    for request in REQUESTS:
        print(f"\n=== Requesting: {request} ===")
        try:
            async with client.conversation(BOT_USERNAME, timeout=30) as conv:
                await conv.send_message("/start")
                try:
                    start_reply = await conv.get_response(timeout=20)
                    print(f"[START REPLY] {start_reply.text[:300]}")
                except Exception as e:
                    print(f"[START] no /start reply: {type(e).__name__}: {e}")

                await conv.send_message(request)
                replies = 0
                while True:
                    try:
                        msg = await conv.get_response(timeout=25)
                    except Exception as e:
                        print(f"[WAIT] no more replies: {type(e).__name__}: {e}")
                        break
                    replies += 1
                    text = msg.text or ""
                    print(f"[REPLY {replies}] {text[:400]}")
                    if looks_like_bridges(text):
                        break
                print(f"[SUMMARY] {request} -> {replies} reply message(s)")
        except Exception as e:
            print(f"[ERROR] {request} failed: {type(e).__name__}: {e}")


async def main():
    if API_ID == 0 or not API_HASH:
        print("[ERROR] TELEGRAM_API_ID and TELEGRAM_API_HASH secrets are required.")
        sys.exit(1)

    client = TelegramClient(StringSession(SESSION or None), API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print("[ERROR] No valid Telegram session found.")
        print("        Generate one locally and add it as the TELEGRAM_SESSION secret:")
        print("          pip install telethon")
        print("          python test_telegram_bridges.py --generate-session")
        await client.disconnect()
        sys.exit(1)

    me = await client.get_me()
    print(f"[INFO] Connected as: {me.first_name} (@{me.username})")

    await ask_bot(client)

    await client.disconnect()
    print("\n[DONE] Test finished. No data was saved.")


async def generate_session():
    if API_ID == 0 or not API_HASH:
        print("[ERROR] TELEGRAM_API_ID and TELEGRAM_API_HASH env vars are required.")
        sys.exit(1)
    session = StringSession()
    client = TelegramClient(session, API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    print(f"[OK] Logged in as {me.first_name}")
    print("TELEGRAM_SESSION=" + session.save())
    await client.disconnect()


if __name__ == "__main__":
    if "--generate-session" in sys.argv:
        asyncio.run(generate_session())
    else:
        asyncio.run(main())
