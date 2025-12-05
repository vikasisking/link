from telethon import TelegramClient, events
from telethon.tl import functions
import time, random

API_ID = 22922489
API_HASH = "c9188fc0a202b2b3941d02dc9cc0cc84"
BOT_TOKEN = "8301898803:AAEXmobxWaWdCs3eZJYMTsO9A-jKb7qqALw"

# HANDLE MULTIPLE TOPIC GROUPS HERE
GROUP_IDS = [
    -1003393086598,   # Group 1
    -1001234567890    # Group 2  <-- ADD YOUR 2nd GROUP HERE
]

client = TelegramClient('session', API_ID, API_HASH)
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# user_id : {link: "...", expire: timestamp, group: id}
active_links = {}

async def create_invite(user_id):
    group = random.choice(GROUP_IDS)  # pick random group

    invite = await client(functions.messages.ExportChatInviteRequest(
        peer=group,
        expire_date=int(time.time()) + 180,  # 3 min
        usage_limit=1                        # 1 user only
    ))

    active_links[user_id] = {
        "link": invite.link,
        "expire": int(time.time()) + 180,
        "group": group
    }
    return invite.link

def clean_expired_links():
    now = time.time()
    expired = [uid for uid, data in active_links.items() if data["expire"] < now]
    for uid in expired:
        del active_links[uid]

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    clean_expired_links()

    user = event.sender_id

    # If user already has a valid link
    if user in active_links:
        return await event.reply(
            f"⏳ You already have an active link:\n{active_links[user]['link']}\n"
            "⛔ Wait until it expires to get a new one."
        )

    # Create new link for either group 1 or group 2
    link = await create_invite(user)
    await event.reply(
        f"🔥 Unique Invite Link Ready!\n"
        f"🔗 {link}\n"
        f"⏰ Valid 3 minutes Fast Join"
    )

print("Bot running with MULTI-GROUP SUPPORT (2 groups) 🚀")
client.start()
bot.run_until_disconnected()
