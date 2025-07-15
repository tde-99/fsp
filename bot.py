
from aiohttp import web
from plugins import web_server
import time
import asyncio
import pyromod.listen
import random
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime, timedelta
from config import *
import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009147483647
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT, OWNER_ID

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.start_time = time.time()

    async def start(self):
        await super().start()
        bot_info = await self.get_me()
        self.name = bot_info.first_name
        self.username = bot_info.username
        self.uptime = datetime.now()
                
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Testing")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("Bot Stopped..")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"[CREDITS::- @CodeXBotz, More advanced features added by:- @mrxbotx]")
        self.LOGGER(__name__).info(f"{self.name} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅")
        self.LOGGER(__name__).info(f"ᴏᴘᴇʀᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟʟ ✅")
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))

        try: 
            await self.send_photo(
                SUPPORT_CHAT, 
                photo=random.choice(PICS),
                caption=(
                    "<b>sᴀᴠᴇ ʀᴇsᴛɪᴄᴛᴇᴅ ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛᴇᴅ ᴀɢᴀɪɴ!</b>\n\n"
                    f"ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ: <code>{uptime_string}</code>"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/nyxkingsupport")]
                ])
            )
        except: 
            pass


    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"{self.name} ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ ✅")
