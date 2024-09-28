from json import loads as jloads
from os import execl
from sys import executable
from datetime import datetime
import asyncio

from aiohttp import ClientSession
from bot import Var, bot, ffQueue
from bot.core.text_utils import TextEditor
from bot.core.reporter import rep

async def send_and_restart():
    # Define the scheduled time for sending and restarting (24-hour format)
    schedule_time = "04:30"  # Example: 4.30 AM

    while True:
        now = datetime.now().strftime("%H:%M")
        
        if now == schedule_time:
            await upcoming_animes()  # Send the anime schedule
            await rep.report("Auto Restarting..!!", "info")
            execl(executable, executable, "-m", "bot")

        await asyncio.sleep(60)  # Check every minute

async def upcoming_animes():
    if Var.SEND_SCHEDULE:
        try:
            async with ClientSession() as ses:
                res = await ses.get("https://subsplease.org/api/?f=schedule&h=true&tz=Asia/Kolkata")
                aniContent = jloads(await res.text())["schedule"]
            sch_list = ""
            for i in aniContent:
                aname = TextEditor(i["title"])
                await aname.load_anilist()
                sch_list += f''' <a href="https://subsplease.org/shows/{i['page']}">{aname.adata.get('title', {}).get('english') or i['title']}</a>\n    • <b>Time</b> : {i["time"]} hrs\n\n'''
            text = f"<b>📆 Today's Anime Releases Schedule</b>\n\n{sch_list}<b>⏰ Current TimeZone :</b> <code>IST (UTC +5:30)</code>"
            await bot.send_message(Var.MAIN_CHANNEL, text)
        except Exception as err:
            await rep.report(str(err), "error")
            # Optionally log the error here

# Start the time check in the main function or entry point of your bot
async def main():
    await send_and_restart()

# If you're using an event loop, make sure to call main() appropriately
