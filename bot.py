from telethon import TelegramClient, events
from telethon.tl import functions
import time

API_ID = 22922489
API_HASH = "c9188fc0a202b2b3941d02dc9cc0cc84"
BOT_TOKEN = "8303362525:AAHlv8WBXbsSBvc2NAF1k1yQUw65sfAsiSE"

GROUP1 = -1003389826969    # Group 1 ID
GROUP2 = -1003368646989     # Group 2 ID  <-- change this to your second group

client = TelegramClient('session', API_ID, API_HASH)
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Store links: user -> {group1:{link,expire}, group2:{link,expire}}
active_links = {}

async def create_invite(group_id):
    invite = await client(functions.messages.ExportChatInviteRequest(
        peer=group_id,
        expire_date=int(time.time()) + 180,  # 3 minutes
        usage_limit=1                        # only 1 join
    ))
    return invite.link, int(time.time()) + 180

def clean_expired_links():
    now = time.time()
    to_delete = []
    for uid, data in active_links.items():
        if data["group1"]["expire"] < now and data["group2"]["expire"] < now:
            to_delete.append(uid)
    for uid in to_delete:
        del active_links[uid]

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    clean_expired_links()
    user = event.sender_id

    # If user already has active links
    if user in active_links:
        g1 = active_links[user]['group1']['link']
        g2 = active_links[user]['group2']['link']
        return await event.reply(
            f"⏳ Your existing active links:\n\n"
            f"1️⃣ Group 1 → {g1}\n"
            f"2️⃣ Group 2 → {g2}\n\n"
            f"⛔ Wait until both links expire for new ones.",
            link_preview=False
        )

    # Create two links
    link1, exp1 = await create_invite(GROUP1)
    link2, exp2 = await create_invite(GROUP2)

    active_links[user] = {
        "group1": {"link": link1, "expire": exp1},
        "group2": {"link": link2, "expire": exp2}
    }

    await event.reply(
        f"🔥 H2I Private Invite Links (Valid 3 min)\n\n"
        f"1️⃣ File Group Link:\n{link1}\n\n"
        f"2️⃣ O*TP Group Link:\n{link2}\n\n"
        f"⚠️ Fast Join Link Valid Only 3 Minutes.",
        link_preview=False
    )

print("Bot running with DUAL TOPIC INVITE SYSTEM 🚀")
client.start()
bot.run_until_disconnected()
