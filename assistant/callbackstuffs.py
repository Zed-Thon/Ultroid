# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import asyncio
import re
import sys
import time
from asyncio.exceptions import TimeoutError as AsyncTimeOut
from os import execl, remove
from random import choice

from bs4 import BeautifulSoup as bs

try:
    from pyUltroid.functions.gDrive import GDriveManager
except ImportError:
    GDriveManager = None
from pyUltroid.functions.helper import fast_download, progress, uploader
from pyUltroid.functions.tools import (
    Carbon,
    async_searcher,
    get_paste,
    telegraph_client,
)
from pyUltroid.startup.loader import Loader
from telegraph import upload_file as upl
from telethon import Button, events
from telethon.tl.types import MessageMediaWebPage
from telethon.utils import get_peer_id

from . import *

# --------------------------------------------------------------------#
telegraph = telegraph_client()
GDrive = GDriveManager() if GDriveManager else None
# --------------------------------------------------------------------#


def text_to_url(event):
    """function to get media url (with|without) Webpage"""
    if isinstance(event.media, MessageMediaWebPage):
        webpage = event.media.webpage
        if not isinstance(webpage, types.WebPageEmpty) and webpage.type in ["photo"]:
            return webpage.display_url
    return event.text


# --------------------------------------------------------------------#

_buttons = {
    "otvars": {
        "text": "- الفـارات الخـاصـه بسـورس زدثـــون @ZedThon:",
        "buttons": [
            [
                Button.inline("تخـزين الكـروب/الخـاص", data="taglog"),
                Button.inline("الحظـر العـام", data="cbs_sfban"),
            ],
            [
                Button.inline("المطـور المسـاعد", data="sudo"),
                Button.inline("نقطـة الاوامـر", data="hhndlr"),
            ],
            [
                Button.inline("الاضـافـات", data="plg"),
                Button.inline("الدونـات", data="eaddon"),
            ],
            [
                Button.inline("ايمـوجي اللوحـه", data="emoj"),
                Button.inline("الاقـراص", data="gdrive"),
            ],
            [
                Button.inline("صـورة الانـلاين", data="inli_pic"),
                Button.inline("نقطـة المطـور", data="shndlr"),
            ],
            [Button.inline("الوضـع الثنـائي", "cbs_oofdm")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
    "sfban": {
        "text": "SuperFban Settings:",
        "buttons": [
            [Button.inline("FBᴀɴ Gʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("Exᴄʟᴜᴅᴇ Fᴇᴅs", data="abs_sfexf")],
            [Button.inline("« Bᴀᴄᴋ", data="cbs_otvars")],
        ],
    },
    "apauto": {
        "text": "This'll auto approve on outgoing messages",
        "buttons": [
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ ON", data="apon")],
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ OFF", data="apof")],
            [Button.inline("« رجـوع", data="cbs_pmcstm")],
        ],
    },
    "alvcstm": {
        "text": f"Customise your {HNDLR}alive. Choose from the below options -",
        "buttons": [
            [Button.inline("كليشـة الفحـص", data="abs_alvtx")],
            [Button.inline("صـورة الفحـص", data="alvmed")],
            [Button.inline("حـذف صـورة الفحـص", data="delmed")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
    "pmcstm": {
        "text": "Customise your PMPERMIT Settings -",
        "buttons": [
            [
                Button.inline("كليشـة الحمـايه", data="pmtxt"),
                Button.inline("صـورة الحمـايه", data="pmmed"),
            ],
            [
                Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", data="cbs_apauto"),
                Button.inline("PMLOGGER", data="pml"),
            ],
            [
                Button.inline("ضـع تحـذيرات", data="swarn"),
                Button.inline("حـذف صـورة الحمـايه", data="delpmmed"),
            ],
            [Button.inline("حمـاية الخـاص", data="cbs_pmtype")],
            [Button.inline("« رجـوع", data="cbs_ppmset")],
        ],
    },
    "pmtype": {
        "text": "Select the type of PMPermit needed.",
        "buttons": [
            [Button.inline("وضـع الانـلاين", data="inpm_in")],
            [Button.inline("الوضـع العـادي", data="inpm_no")],
            [Button.inline("« رجـوع", data="cbs_pmcstm")],
        ],
    },
    "ppmset": {
        "text": "PMPermit Settings:",
        "buttons": [
            [Button.inline("تفعيـل حمـاية الخـاص", data="pmon")],
            [Button.inline("تعطيـل حمـاية الخـاص", data="pmoff")],
            [Button.inline("تعييـن حمـاية الخـاص", data="cbs_pmcstm")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
    "chatbot": {
        "text": "From This Feature U can chat with ppls Via ur Assistant Bot.\n[More info](https://t.me/UltroidUpdates/2)",
        "buttons": [
            [
                Button.inline("Cʜᴀᴛ Bᴏᴛ  Oɴ", data="onchbot"),
                Button.inline("Cʜᴀᴛ Bᴏᴛ  Oғғ", data="ofchbot"),
            ],
            [
                Button.inline("التـرحيب", data="bwel"),
                Button.inline("التـرحيب ميديـا", data="botmew"),
            ],
            [Button.inline("كليشـة وصـف البـوت", data="botinfe")],
            [Button.inline("الاشتـراك الاجبـاري", data="pmfs")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
    "vcb": {
        "text": "From This Feature U can play songs in group voice chat\n\n[moreinfo](https://t.me/UltroidUpdates/4)",
        "buttons": [
            [Button.inline("جلسـة بـوت الاغـاني", data="abs_vcs")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
    "oofdm": {
        "text": "About [Dual Mode](https://t.me/UltroidUpdates/18)",
        "buttons": [
            [
                Button.inline("تفعيـل الوضـع الثنـائي", "dmof"),
                Button.inline("تعطيـل الوضـع الثنـائي", "dmof"),
            ],
            [Button.inline("نقطـة الوضـع الثنـائي", "dmhn")],
            [Button.inline("« رجـوع", data="cbs_otvars")],
        ],
    },
    "apiset": {
        "text": get_string("ast_1"),
        "buttons": [
            [Button.inline("كود امر ازالة الخلفيات", data="abs_rmbg")],
            [Button.inline("كود كاشف الاباحي", data="abs_dapi")],
            [Button.inline("كود امر ترجمه الصور", data="abs_oapi")],
            [Button.inline("« رجـوع", data="setter")],
        ],
    },
}

_convo = {
    "rmbg": {
        "var": "RMBG_API",
        "name": "Remove.bg API Key",
        "text": get_string("ast_2"),
        "back": "cbs_apiset",
    },
    "dapi": {
        "var": "DEEP_AI",
        "name": "Deep AI Api Key",
        "text": "Get Your Deep Api from deepai.org and send here.",
        "back": "cbs_apiset",
    },
    "oapi": {
        "var": "OCR_API",
        "name": "Ocr Api Key",
        "text": "Get Your OCR api from ocr.space and send that Here.",
        "back": "cbs_apiset",
    },
    "pmlgg": {
        "var": "PMLOGGROUP",
        "name": "Pm Log Group",
        "text": "Send chat id of chat which you want to save as Pm log Group.",
        "back": "pml",
    },
    "vcs": {
        "var": "VC_SESSION",
        "name": "Vc Session",
        "text": "**Vc session**\nEnter the New session u generated for vc bot.\n\nUse /cancel to terminate the operation.",
        "back": "cbs_vcb",
    },
    "settag": {
        "var": "TAG_LOG",
        "name": "Tag Log Group",
        "text": f"Make a group, add your assistant and make it admin.\nGet the `{HNDLR}id` of that group and send it here for tag logs.\n\nUse /cancel to cancel.",
        "back": "taglog",
    },
    "alvtx": {
        "var": "ALIVE_TEXT",
        "name": "Alive Text",
        "text": "**Alive Text**\nEnter the new alive text.\n\nUse /cancel to terminate the operation.",
        "back": "cbs_alvcstm",
    },
    "sfexf": {
        "var": "EXCLUDE_FED",
        "name": "Excluded Fed",
        "text": "Send the Fed IDs you want to exclude in the ban. Split by a space.\neg`id1 id2 id3`\nSet is as `None` if you dont want any.\nUse /cancel to go back.",
        "back": "cbs_sfban",
    },
}


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile(
        "sndplug_(.*)",
    ),
    owner=True,
)
async def send(eve):
    key, name = (eve.data_match.group(1)).decode("UTF-8").split("_")
    thumb = "resources/extras/inline.jpg"
    await eve.answer("■ جـار الارسـال ■")
    data = f"uh_{key}_"
    index = None
    if "|" in name:
        name, index = name.split("|")
    key = "plugins" if key == "Official" else key.lower()
    plugin = f"{key}/{name}.py"
    _ = f"pasta-{plugin}"
    if index is not None:
        data += f"|{index}"
        _ += f"|{index}"
    buttons = [
        [
            Button.inline(
                "« Pᴀsᴛᴇ »",
                data=_,
            )
        ],
        [
            Button.inline("« رجـوع", data=data),
        ],
    ]
    try:
        await eve.edit(file=plugin, thumb=thumb, buttons=buttons)
    except Exception as er:
        await eve.answer(str(er), alert=True)


heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME


@callback("updatenow", owner=True)
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if heroku_api:
        import heroku3

        try:
            heroku = heroku3.from_key(heroku_api)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException:
            return await eve.edit("`خطـأ HEROKU_API.`")
        for app in heroku_applications:
            if app.name == app_name:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`خطـأ HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(get_string("clst_1"))
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + heroku_api + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Here is the error log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Successfully Updated!\nRestarting, please wait...`")
    else:
        await eve.edit(get_string("clst_1"))
        call_back()
        await bash("git pull && pip3 install -r requirements.txt")
        execl(sys.executable, sys.executable, "-m", "pyUltroid")


@callback(re.compile("changes(.*)"), owner=True)
async def changes(okk):
    match = okk.data_match.group(1).decode("utf-8")
    await okk.answer(get_string("clst_3"))
    repo = Repo.init()
    button = [[Button.inline("Update Now", data="updatenow")]]
    changelog, tl_chnglog = await gen_chlog(
        repo, f"HEAD..upstream/{repo.active_branch}"
    )
    cli = "\n\nClick the below button to update!"
    if not match:
        try:
            if len(tl_chnglog) > 700:
                tl_chnglog = tl_chnglog[:700] + "..."
                button.append([Button.inline("View Complete", "changesall")])
            await okk.edit("• Writing Changelogs 📝 •")
            img = await Carbon(
                file_name="changelog",
                code=tl_chnglog,
                backgroundColor=choice(ATRA_COL),
                language="md",
            )
            return await okk.edit(
                f"**• ZThon Userbot •**{cli}", file=img, buttons=button
            )
        except Exception as er:
            LOGS.exception(er)
    changelog_str = changelog + cli
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        await asyncio.sleep(2)
        with open("ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await okk.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=button,
        )
        remove("ultroid_updates.txt")
        return
    await okk.edit(
        changelog_str,
        buttons=button,
        parse_mode="html",
    )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
    owner=True,
)
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    index = None
    if "|" in ok:
        ok, index = ok.split("|")
    with open(ok, "r") as hmm:
        _, key = await get_paste(hmm.read())
    link = "https://spaceb.in/" + key
    raw = f"https://spaceb.in/api/v1/documents/{key}/raw"
    if not _:
        return await e.answer(key[:30], alert=True)
    if ok.startswith("addons"):
        key = "Addons"
    elif ok.startswith("vcbot"):
        key = "VCBot"
    else:
        key = "Official"
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
    await e.edit(
        "",
        buttons=[
            [Button.url("الرابـط", link), Button.url("التفاصيل", raw)],
            [Button.inline("« رجـوع", data=data)],
        ],
    )


@callback(re.compile("cbs_(.*)"), owner=True)
async def _edit_to(event):
    match = event.data_match.group(1).decode("utf-8")
    data = _buttons.get(match)
    if not data:
        return
    await event.edit(data["text"], buttons=data["buttons"], link_preview=False)


@callback(re.compile("abs_(.*)"), owner=True)
async def convo_handler(event: events.CallbackQuery):
    match = event.data_match.group(1).decode("utf-8")
    if not _convo.get(match):
        return
    await event.delete()
    get_ = _convo[match]
    back = get_["back"]
    async with event.client.conversation(event.sender_id) as conv:
        await conv.send_message(get_["text"])
        response = conv.wait_event(events.NewMessage(chats=event.sender_id))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button(back),
            )
        await setit(event, get_["var"], themssg)
        await conv.send_message(
            f"{get_['name']} changed to `{themssg}`",
            buttons=get_back_button(back),
        )


@callback("authorise", owner=True)
async def _(e):
    if not e.is_private:
        return
    url = GDrive._create_token_file()
    await e.edit("Go to the below link and send the code!")
    async with asst.conversation(e.sender_id) as conv:
        await conv.send_message(url)
        code = await conv.get_response()
        if GDrive._create_token_file(code=code.text):
            await conv.send_message(
                "`Success!\nYou are all set to use Google Drive with Ultroid Userbot.`",
                buttons=Button.inline("Main Menu", data="setter"),
            )
        else:
            await conv.send_message("Wrong code! Click authorise again.")


@callback("folderid", owner=True, func=lambda x: x.is_private)
async def _(e):
    if not e.is_private:
        return
    msg = (
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Send link of that folder."
    )
    await e.delete()
    async with asst.conversation(e.sender_id, timeout=150) as conv:
        await conv.send_message(msg)
        repl = await conv.get_response()
        id = repl.text
        if id.startswith("https"):
            id = id.split("?id=")[-1]
        udB.set_key("GDRIVE_FOLDER_ID", id)
        await repl.reply(
            "`Success.`",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive", owner=True)
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Click Authorise and send the code.\n\nYou can use your own CLIENT ID and SECRET by [this](https://t.me/UltroidUpdates/37)",
        buttons=[
            [
                Button.inline("Folder ID", data="folderid"),
                Button.inline("Authorise", data="authorise"),
            ],
            [Button.inline("« رجـوع", data="cbs_otvars")],
        ],
        link_preview=False,
    )


@callback("dmof", owner=True)
async def rhwhe(e):
    if udB.get_key("DUAL_MODE"):
        udB.del_key("DUAL_MODE")
        key = "Off"
    else:
        udB.set_key("DUAL_MODE", "True")
        key = "On"
    Msg = "Dual Mode : " + key
    await e.edit(Msg, buttons=get_back_button("cbs_otvars"))


@callback("dmhn", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "DUAL_HNDLR"
    name = "Dual Handler"
    CH = udB.get_key(var) or "/"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which u want as Handler/Trigger to use your Assistant bot\nUr Current Handler is [ `{CH}` ]\n\n use /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("emoj", owner=True)
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"- الايموجـي المستخـدم بقائمـة امـر `{HNDLR}اوامري` الشفـافه"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("- قـم بارسـال الايمـوجي الذي تريـد وضعـه🙃.\n\n- اضغـط/cancel لـ الالغـاء.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Incorrect Emoji",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}\n",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("plg", owner=True)
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send id or username of a channel from where u want to install all plugins\n\nOur Channel~ @ultroidplugins\n\nUse /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Incorrect channel",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After Setting All Things Do Restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("cbs_otvars"),
            )


@callback("hhndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which u want as Handler/Trigger to use bot\nUr Current Handler is [ `{HNDLR}` ]\n\n use /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "This cannot be used as handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("shndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "SUDO_HNDLR"
    name = "Sudo Handler"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send The Symbol Which u want as Sudo Handler/Trigger to use bot\n\n use /cancel to cancel."
        )

        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "This cannot be used as handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("taglog", owner=True)
async def tagloggrr(e):
    BUTTON = [
        [Button.inline("وضع تخزين الكروب/الخاص", data="abs_settag")],
        [Button.inline("تعطيـل الوضـع", data="deltag")],
        get_back_button("cbs_otvars"),
    ]
    await e.edit(
        "- اختـر من الاسفـل",
        buttons=BUTTON,
    )


@callback("deltag", owner=True)
async def _(e):
    udB.del_key("TAG_LOG")
    await e.answer("- تم بنجـاح ✓ .. تعطيـل تخـزين الكـروبات/الخـاص")


@callback("eaddon", owner=True)
async def pmset(event):
    if not udB.get_key("ADDONS"):
        BT = [Button.inline("تفعيـل الدونـات", data="edon")]
    else:
        BT = [Button.inline("تعطيـل الدونـات", data="edof")]
    await event.edit(
        "ADDONS~ Extra Plugins:",
        buttons=[
            BT,
            [Button.inline("« رجـوع", data="cbs_otvars")],
        ],
    )


@callback("edon", owner=True)
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Done! ADDONS has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("edof", owner=True)
async def eddof(event):
    udB.set_key("ADDONS", "False")
    await event.edit(
        "Done! ADDONS has been turned off!! After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo", owner=True)
async def pmset(event):
    if not udB.get_key("SUDO"):
        BT = [Button.inline("تفعيـل المطـور المسـاعد", data="onsudo")]
    else:
        BT = [Button.inline("تعطيـل المطـور المسـاعد", data="ofsudo")]
    await event.edit(
        f"SUDO MODE ~ Some peoples can use ur Bot which u selected. To know More use `{HNDLR}help sudo`",
        buttons=[
            BT,
            [Button.inline("« رجـوع", data="cbs_otvars")],
        ],
    )


@callback("onsudo", owner=True)
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Done! SUDO MODE has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo", owner=True)
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Done! SUDO MODE has been turned off!! After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("sfgrp", owner=True)
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add @MissRose_Bot, send `{HNDLR}id`, copy that and send it here.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_sfban"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} changed to {themssg}",
            buttons=get_back_button("cbs_sfban"),
        )


@callback("alvmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nSend me a pic/gif/media to set as alive media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        except BaseException:
            pass
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            media = await event.client.download_media(response, "alvpc")
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("cbs_alvcstm"),
        )


@callback("delmed", owner=True)
async def dell(event):
    try:
        udB.del_key("ALIVE_PIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_alabs_vcstm")
        )
    except BaseException:
        return await event.edit(
            get_string("clst_4"),
            buttons=get_back_button("cbs_alabs_vcstm"),
        )


@callback("inpm_in", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "True")
    await event.edit(
        "Done!! PMPermit type has been set to inline!",
        buttons=[[Button.inline("« رجـوع", data="cbs_pmtype")]],
    )


@callback("inpm_no", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "False")
    await event.edit(
        "Done!! PMPermit type has been set to normal!",
        buttons=[[Button.inline("« رجـوع", data="cbs_pmtype")]],
    )


@callback("pmtxt", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nEnter the new Pmpermit text.\n\nu can use `{name}` `{fullname}` `{count}` `{mention}` `{username}` to get this from user Too\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        if len(themssg) > 4090:
            return await conv.send_message(
                "Message too long!\nGive a shorter message please!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                name,
                themssg,
            ),
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("swarn", owner=True)
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Bᴀᴄᴋ", data="cbs_pmcstm")])
    await event.edit(
        "Select the number of warnings for a user before getting blocked in PMs.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"), owner=True)
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set_key("PMWARNS", value)
    if dn:
        await event.edit(
            f"PM Warns Set to {value}.\nNew users will have {value} chances in PMs before getting banned.",
            buttons=get_back_button("cbs_pmcstm"),
        )
    else:
        await event.edit(
            f"Something went wrong, please check your {HNDLR}logs!",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("pmmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nSend me a pic/gif/sticker/link  to set as pmpermit media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("delpmmed", owner=True)
async def dell(event):
    try:
        udB.del_key("PMPIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_pmcstm")
        )
    except BaseException:
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« تعيين صورة الحمايه", data="setter")]],
        )


@callback("apon", owner=True)
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        "Done!! AUTOAPPROVE  Started!!",
        buttons=[[Button.inline("« رجـوع", data="cbs_apauto")]],
    )


@callback("apof", owner=True)
async def apof(event):
    try:
        udB.set_key("AUTOAPPROVE", "False")
        return await event.edit(
            "Done! AUTOAPPROVE Stopped!!",
            buttons=[[Button.inline("« رجـوع", data="cbs_apauto")]],
        )
    except BaseException:
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("pml", owner=True)
async def l_vcs(event):
    if not udB.get_key("PMLOG"):
        BT = [Button.inline("تفعيـل تخـزين الخـاص", data="pmlog")]
    else:
        BT = [Button.inline("تعطيـل تخـزين الخـاص", data="pmlogof")]
    await event.edit(
        "PMLOGGER This Will Forward Ur Pm to Ur Private Group -",
        buttons=[
            BT,
            [Button.inline("تخـزين الكـروبات", "abs_pmlgg")],
            [Button.inline("« رجـوع", data="cbs_pmcstm")],
        ],
    )


@callback("pmlog", owner=True)
async def pmlog(event):
    await setit(event, "PMLOG", "True")
    await event.edit(
        "Done!! PMLOGGER  Started!!",
        buttons=[[Button.inline("« رجـوع", data="pml")]],
    )


@callback("pmlogof", owner=True)
async def pmlogof(event):
    try:
        udB.del_key("PMLOG")
        return await event.edit(
            "Done! PMLOGGER Stopped!!",
            buttons=[[Button.inline("« رجـوع", data="pml")]],
        )
    except BaseException:
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« الاعـدادات", data="setter")]],
        )


@callback("pmon", owner=True)
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        "Done! PMPermit has been turned on!!",
        buttons=[[Button.inline("« رجـوع", data="cbs_ppmset")]],
    )


@callback("pmoff", owner=True)
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        "Done! PMPermit has been turned off!!",
        buttons=[[Button.inline("« رجـوع", data="cbs_ppmset")]],
    )


@callback("botmew", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message("Send Any Media to keep at your Bot's welcome ")
        msg = await conv.get_response()
        if not msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Terminated!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("STARTMEDIA", msg.file.id)
        await conv.send_message("Done!", buttons=get_back_button("cbs_chatbot"))


@callback("botinfe", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message(
            "Send message to set to Display, when user Press Info button in Bot Welcome!\n\nsend `False` to completely remove that button.."
        )
        msg = await conv.get_response()
        if msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Terminated!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("BOT_INFO_START", msg.text)
        await conv.send_message("Done!", buttons=get_back_button("cbs_chatbot"))


@callback("pmfs", owner=True)
async def heheh(event):
    Ll = []
    err = ""
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message(
            "• Send The Chat Id(s), which you want user to Join Before using Chat/Pm Bot\n\n• Send /clear to disable PmBot Force sub..\n• • Send /cancel to stop this process.."
        )
        await conv.send_message(
            "Example : \n`-1001234567\n-100778888`\n\nFor Multiple Chat(s)."
        )
        try:
            msg = await conv.get_response()
        except AsyncTimeOut:
            return await conv.send_message("**• TimeUp!**\nStart from /start back.")
        if not msg.text or msg.text.startswith("/"):
            timyork = "Cancelled!"
            if msg.text == "/clear":
                udB.del_key("PMBOT_FSUB")
                timyork = "Done! Force Subscribe Stopped\nRestart your Bot!"
            return await conv.send_message(
                "Cancelled!", buttons=get_back_button("cbs_chatbot")
            )
        for chat in msg.message.split("\n"):
            if chat.startswith("-") or chat.isdigit():
                chat = int(chat)
            try:
                CHSJSHS = await event.client.get_entity(chat)
                Ll.append(get_peer_id(CHSJSHS))
            except Exception as er:
                err += f"**{chat}** : {er}\n"
        if err:
            return await conv.send_message(err)
        udB.set_key("PMBOT_FSUB", str(Ll))
        await conv.send_message(
            "Done!\nRestart Your Bot.", buttons=get_back_button("cbs_chatbot")
        )


@callback("bwel", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nEnter the msg which u want to show when someone start your assistant Bot.\nYou Can use `{me}` , `{mention}` Parameters Too\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("cbs_chatbot"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            "{} changed to {}".format(
                name,
                themssg,
            ),
            buttons=get_back_button("cbs_chatbot"),
        )


@callback("onchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    Loader(path="assistant/pmbot.py", key="PM Bot").load_single()
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.add_event_handler(i, events.NewMessage(**e))
    await event.edit(
        "Done! Now u Can Chat With People Via This Bot",
        buttons=[Button.inline("« رجـوع", data="cbs_chatbot")],
    )


@callback("ofchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
    await event.edit(
        "Done! Chat People Via This Bot Stopped.",
        buttons=[Button.inline("« رجـوع", data="cbs_chatbot")],
    )


@callback("inli_pic", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\nSend me a pic/gif/ or link  to set as inline media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("setter"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("setter"),
        )


FD_MEDIA = {}


@callback(re.compile("fd(.*)"), owner=True)
async def fdroid_dler(event):
    uri = event.data_match.group(1).decode("utf-8")
    if FD_MEDIA.get(uri):
        return await event.edit(file=FD_MEDIA[uri])
    await event.answer("• Starting Download •", alert=True)
    await event.edit("• جـاري التحميـل.. •")
    URL = f"https://f-droid.org/packages/{uri}"
    conte = await async_searcher(URL, re_content=True)
    BSC = bs(conte, "html.parser", from_encoding="utf-8")
    dl_ = BSC.find("p", "package-version-download").find("a")["href"]
    title = BSC.find("h3", "package-name").text.strip()
    thumb = BSC.find("img", "package-icon")["src"]
    if thumb.startswith("/"):
        thumb = "https://f-droid.org" + thumb
    thumb, _ = await fast_download(thumb, filename=uri + ".png")
    s_time = time.time()
    file, _ = await fast_download(
        dl_,
        filename=title + ".apk",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(
                d,
                t,
                event,
                s_time,
                "Downloading...",
            )
        ),
    )
    tt = time.time()
    n_file = await uploader(file, file, tt, event, "Uploading...")
    buttons = Button.switch_inline("Search Back", query="fdroid", same_peer=True)
    try:
        msg = await event.edit(
            f"**• [{title}]({URL}) •**", file=n_file, thumb=thumb, buttons=buttons
        )
    except Exception as er:
        LOGS.exception(er)
        try:
            msg = await event.client.edit_message(
                await event.get_input_chat(),
                event.message_id,
                f"**• [{title}]({URL}) •**",
                buttons=buttons,
                thumb=thumb,
                file=n_file,
            )
        except Exception as er:
            os.remove(thumb)
            os.remove(file)
            LOGS.exception(er)
            return await event.edit(f"**خطـأ**: `{er}`", buttons=buttons)
    if msg and hasattr(msg, "media"):
        FD_MEDIA.update({uri: msg.media})
    os.remove(thumb)
    os.remove(file)
