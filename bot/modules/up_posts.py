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
            text = "<b>📆 Today's Anime Releases Schedule</b>\n\n"
            for i in aniContent:
                aname = TextEditor(i["title"])
                await aname.load_anilist()
                text += f''' <a href="https://subsplease.org/shows/{i['page']}">{aname.adata.get('title', {}).get('english') or i['title']}</a>\n    • <b>Time</b> : {i["time"]} hrs\n\n'''
                sch_list = text + "<b>⏰ Current TimeZone :</b> <code>IST (UTC +5:30)</code>"
            TD_SCHR = await bot.send_message(Var.MAIN_CHANNEL, sch_list)
            await (await TD_SCHR.pin()).delete()
        except Exception as err:
            await rep.report(str(err), "error")
    if not ffQueue.empty():
        await ffQueue.join()
    await rep.report("Auto Restarting..!!", "info")
    execl(executable, executable, "-m", "bot")

async def update_shdr(name, link):
    global TD_SCHR
    if TD_SCHR is not None:
        try:
            # Retrieve the current text from the pinned message
            TD_lines = await TD_SCHR.text.split('\n')

            # Flag to check if the anime name was found
            found = False

            # Find the line that starts with the anime name and update the status
            for i, line in enumerate(TD_lines):
                if line.startswith(f"📌 {name}"):
                    found = True
                    if i + 2 < len(TD_lines):
                        TD_lines[i + 2] = f"    • **Status :** ✅ __Uploaded__\n    • **Link :** {link}"
                    else:
                        # Handle case where there are not enough lines
                        TD_lines.append(f"    • **Status :** ✅ __Uploaded__\n    • **Link :** {link}")
                    break

            if not found:
                await rep.report(f"Anime '{name}' not found in the schedule.", "warning")

            # Join the updated lines and edit the pinned message
            updated_text = "\n".join(TD_lines)
            await TD_SCHR.edit(updated_text)

        except Exception as e:
            await rep.report(f"Error updating status: {str(e)}", "error")
    else:
        await rep.report("TD_SCHR is not initialized.", "error")
