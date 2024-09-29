from json import loads as jloads
from os import execl, path
from sys import executable
from datetime import datetime
import asyncio
import aiofiles
from aiohttp import ClientSession
from bot import Var, bot
from bot.core.text_utils import TextEditor
from bot.core.reporter import rep

MESSAGE_ID_FILE = "last_message_id.txt"
RESTART_TIME = "03:00"

async def save_last_message_id(message_id):
    async with aiofiles.open(MESSAGE_ID_FILE, "w") as f:
        await f.write(str(message_id))

async def get_last_message_id():
    if path.exists(MESSAGE_ID_FILE):
        async with aiofiles.open(MESSAGE_ID_FILE, "r") as f:
            return int(await f.read().strip())
    return None

async def fetch_and_format_schedule():
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

        return sch_list

async def send_schedule():
    last_message_id = await get_last_message_id()
    if Var.SEND_SCHEDULE:
        try:
            sch_list = await fetch_and_format_schedule()

            text = (f"<b>📆 Today's Anime Releases Schedule</b>\n\n{sch_list}"
                    f"<b>⏰ Current TimeZone :</b> <code>IST (UTC +5:30)</code>")

            # Delete the previous message if it exists
            if last_message_id:
                try:
                    await bot.delete_message(Var.MAIN_CHANNEL, last_message_id)
                except Exception as e:
                    await rep.report(f"Error deleting message: {str(e)}", "error")

            # Send the new message
            sent_message = await bot.send_message(Var.MAIN_CHANNEL, text)

            # Access the correct message ID
            message_id = getattr(sent_message, 'message_id', None) or getattr(sent_message, 'id', None)

            if message_id:
                await save_last_message_id(message_id)

                # Pin the new message
                await (await sent_message.pin()).delete()

        except Exception as err:
            await rep.report(str(err), "error")

async def send_and_restart():
    while True:
        now = datetime.now().strftime("%H:%M")
        if now == RESTART_TIME:
            await rep.report("Auto Restarting..!!", "info")
            execl(executable, executable, "-m", "bot")
        
        await send_schedule()
        await asyncio.sleep(300)  # Wait for 5 minutes

async def main():
    await send_and_restart()

if __name__ == "__main__":
    asyncio.run(main())
