import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from keep_alive import keep_alive

# پر شده بر اساس اطلاعات تو
api_id = 20653789
api_hash = '15dd050807a9919b75ec982236198e33'
phone = '+989155906210'

source_channel = 'gym_workoutss'  # بدون @
dest_group = 'Fit_Group'  # بدون @

client = TelegramClient('forward_session', api_id, api_hash)


@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        await client.forward_messages(dest_group, event.message)
        print(f"Forwarded new message {event.message.id}")
        await asyncio.sleep(600)
    except FloodWaitError as e:
        print(f"FloodWait: waiting {e.seconds}s")
        await asyncio.sleep(e.seconds + 1)
    except Exception as e:
        print(f"Error forwarding new message: {e}")


async def forward_old_messages():
    print("Fetching last 1800 messages...")
    messages = await client.get_messages(source_channel, limit=1800)
    for m in reversed(messages):
        try:
            await client.forward_messages(dest_group, m)
            print(f"Forwarded old message {m.id}")
            await asyncio.sleep(600)
        except FloodWaitError as e:
            print(f"FloodWait while forwarding old message: {e.seconds}s")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            print(f"Error forwarding old message {m.id}: {e}")


async def main():
    keep_alive()  # شروع وب سرور keep-alive
    await client.start(phone)
    print("Signed in and running...")
    await forward_old_messages()
    print("Listening for new messages...")
    await asyncio.Event().wait()  # نگه داشتن برنامه برای شنیدن پیام‌های جدید


if __name__ == '__main__':
    asyncio.run(main())
