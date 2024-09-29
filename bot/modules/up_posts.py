from json import loads as jloads
from os import execl, path
from sys import executable
from datetime import datetime
import asyncio

from aiohttp import ClientSession
from bot import Var, bot, ffQueue
from bot.core.text_utils import TextEditor
from bot.core.reporter import rep

MESSAGE_ID_FILE = "last_message_id.txt"

async def save_last_message_id(message_id):
    """Save the last message ID to a file."""
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(message_id))

async def get_last_message_id():
    """Retrieve the last message ID from a file."""
    if path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            return int(f.read().strip())
    return None

async def send_schedule():
    """Fetch and send the anime schedule."""
    last_message_id = await get_last_message_id()  # Load last message ID
    if Var.SEND_SCHEDULE:
        try:
            async with ClientSession() as ses:
                res = await ses.get("https://subsplease.org/api/?f=schedule&h=true&tz=Asia/Kolkata")
                aniContent = jloads(await res.text())["schedule"]

            sch_list = ""
            for i in aniContent:
                aname = TextEditor(i["title"])
                await aname.load_anilist()
                title = aname.adata.get('title', {}).get('english') or i['title']
                time = i["time"]
                aired_icon = "✅" if i["aired"] else ""
                sch_list += f"[<code>{time}</code>] - 📌 <b>{title}</b> {aired_icon}\n\n"

            text = f"<b>📆 Today's Anime Releases Schedule</b>\n\n{sch_list}<b>⏰ Current TimeZone :</b> <code>IST (UTC +5:30)</code>"

            # Delete the previous message if it exists
            if last_message_id:
                try:
                    await bot.delete_message(Var.MAIN_CHANNEL, last_message_id)
                except Exception as e:
                    await rep.report(f"Error deleting message: {str(e)}", "error")

            # Send the new message and save the message ID
            sent_message = await bot.send_message(Var.MAIN_CHANNEL, text)
            await save_last_message_id(sent_message.message_id)  # Save the new message ID

            # Pin the new message
            await (await sent_message.pin()).delete()

        except Exception as err:
            await rep.report(str(err), "error")

async def send_and_restart():
    # Define the scheduled time for restarting the bot (24-hour format)
    restart_time = "04:30"  # Example: 4:30 AM

    while True:
        now = datetime.now().strftime("%H:%M")

        # Check for restart time
        if now == restart_time:
            await rep.report("Auto Restarting..!!", "info")
            execl(executable, executable, "-m", "bot")

        await send_schedule()  # Send the anime schedule
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

# Start the main function
async def main():
    await send_and_restart()

# If you're using an event loop, make sure to call main() appropriately
