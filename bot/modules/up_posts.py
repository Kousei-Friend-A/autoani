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
            text = "<b>📆 Today's Schedule [IST]</b>\n\n"
            for i in aniContent:
                aname = TextEditor(i["title"])
                await aname.load_anilist()
                title = aname.adata.get('title', {}).get('english') or i['title']
                time = i["time"]
                sch_list += f"[<code>{time}</code>] - 📌 <b>{title}</b>\n\n"

            text += sch_list
            text += "<b>⏰ Current TimeZone :</b> <code>IST (UTC +5:30)</code>"
            await bot.send_message(Var.MAIN_CHANNEL, text)

        except Exception as err:
            await rep.report(str(err), "error")

    if not ffQueue.empty():
        await ffQueue.join()
        
    await rep.report("Auto Restarting..!!", "info")
    execl(executable, executable, "-m", "bot")
