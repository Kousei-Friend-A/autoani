from json import loads as jloads
from os import execl
from sys import executable
from aiohttp import ClientSession
from bot import Var, bot, ffQueue
from bot.core.text_utils import TextEditor
from bot.core.reporter import rep
from mongodb import MongoDB  # Import MongoDB class

# Initialize MongoDB
db = MongoDB(Var.MONGO_URI, "FZAutoAnimes")

TD_SCHR = None  # Ensure TD_SCHR is initialized properly

async def upcoming_animes():
    global TD_SCHR
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

            # Send the message and pin it
            if TD_SCHR:
                await TD_SCHR.edit(sch_list)
            else:
                TD_SCHR = await bot.send_message(Var.MAIN_CHANNEL, sch_list)
                await (await TD_SCHR.pin()).delete()
            
            # Save the message ID to MongoDB
            await db.saveAnime("schedule", "schedule", "status", post_id=TD_SCHR.message_id)

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
            # Retrieve message ID from MongoDB
            post_id = await db.getMessageId(name)
            
            if post_id:
                message = await bot.get_message(Var.MAIN_CHANNEL, post_id)
                if message:
                    # Update message content based on new data
                    TD_lines = message.text.split('\n')
                    for i, line in enumerate(TD_lines):
                        if line.startswith(f"<a href=\"https://subsplease.org/shows/{name}\">"):
                            if i + 2 < len(TD_lines):
                                TD_lines[i + 2] = f"    • **Status :** ✅ __Uploaded__\n    • **Link :** {link}"
                            else:
                                TD_lines.append(f"    • **Status :** ✅ __Uploaded__\n    • **Link :** {link}")

                    updated_text = "\n".join(TD_lines)
                    await message.edit(updated_text)
                else:
                    await rep.report(f"Message with ID {post_id} not found.", "error")
            else:
                await rep.report(f"No post ID found for anime {name}.", "error")
        except Exception as e:
            await rep.report(f"Error updating status: {str(e)}", "error")
    else:
        await rep.report("TD_SCHR is not initialized.", "error")
