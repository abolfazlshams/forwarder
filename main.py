import asyncio
from flask import Flask, jsonify
from threading import Thread
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import os

app = Flask('')

# اطلاعات ربات
API_ID = int(os.getenv('API_ID', '20653789'))
API_HASH = os.getenv('API_HASH', '15dd050807a9919b75ec982236198e33')
PHONE = os.getenv('PHONE', '+98155906210')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL', 'gym_workoutss')
DEST_GROUP = os.getenv('DEST_GROUP', 'Fit_Group')

# کلاینت تلگرام
client = TelegramClient('session', API_ID, API_HASH)

@app.route('/')
def home():
    return f"Bot is running! Forwarding from {SOURCE_CHANNEL} to {DEST_GROUP}"

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "telethon_connected": client.is_connected() if client else False,
        "source_channel": SOURCE_CHANNEL,
        "destination_group": DEST_GROUP
    })

# پیام‌های جدید
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        await client.forward_messages(DEST_GROUP, event.message)
        print(f"✅ Forwarded new message {event.message.id}")
    except FloodWaitError as e:
        print(f"⏳ FloodWait: waiting {e.seconds}s")
        await asyncio.sleep(e.seconds + 1)
    except Exception as e:
        print(f"❌ Error: {e}")

# پیام‌های قدیمی
async def forward_old_messages():
    print("📜 Forwarding last 1600 old messages...")
    try:
        messages = await client.get_messages(SOURCE_CHANNEL, limit=1600)
        for msg in reversed(messages):
            try:
                await client.forward_messages(DEST_GROUP, msg)
                print(f"📨 Forwarded old message {msg.id}")
                await asyncio.sleep(600)
            except FloodWaitError as e:
                print(f"⏳ FloodWait while forwarding old: {e.seconds}s")
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                print(f"❌ Error forwarding old message {msg.id}: {e}")
    except Exception as e:
        print(f"❌ Error getting old messages: {e}")

# شروع ربات
async def init_bot():
    await client.start(PHONE)
    print("🚀 Bot started!")

    await forward_old_messages()

    print(f"📡 Listening for new messages from {SOURCE_CHANNEL}")
    await client.run_until_disconnected()

# Flask
def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

# Telegram
def run_telegram():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_bot())

# اجرای همزمان
def keep_alive():
    Thread(target=run_flask, daemon=True).start()
    run_telegram()

if __name__ == '__main__':
    keep_alive()
