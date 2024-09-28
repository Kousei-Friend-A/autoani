from json import loads as jloads
from os import path as ospath, execl
from sys import executable

from aiohttp import ClientSession
from bot import Var, bot, ffQueue
from bot.core.text_utils import TextEditor
from bot.core.reporter import rep

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
            TD_SCHR = await bot.send_message(Var.MAIN_CHANNEL, text)
        except Exception as err:
            await rep.report(str(err), "error")
            # Optionally log the error here
    if not ffQueue.empty():
        await ffQueue.join()
    await rep.report("Auto Restarting..!!", "info")
    execl(executable, executable, "-m", "bot")
