import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler

# ═══════════════════════════════════════════════════════════════════════════════════
#                                   ʙᴏᴛ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ
# ═══════════════════════════════════════════════════════════════════════════════════

# ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴄʀᴇᴅᴇɴᴛɪᴀʟs - ʀᴇǫᴜɪʀᴇᴅ
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘɪ ᴄʀᴇᴅᴇɴᴛɪᴀʟs - ɢᴇᴛ ғʀᴏᴍ https://my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "21816206"))
API_ID = APP_ID
API_HASH = os.environ.get("API_HASH", "")

# ᴄʜᴀɴɴᴇʟ & ᴜsᴇʀ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-"))  # ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ
OWNER_ID = int(os.environ.get("OWNER_ID", "6109922417"))          # ᴘʀɪᴍᴀʀʏ ᴏᴡɴᴇʀ
OWNER_I = int(os.environ.get("OWNER_ID", "7645440087"))           # sᴇᴄᴏɴᴅᴀʀʏ ᴏᴡɴᴇʀ

# sᴇʀᴠᴇʀ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ
PORT = os.environ.get("PORT", "7079")

SUPPORT_CHAT = int(os.environ.get("SUPPORT_CHAT", "6109922417"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "100"))
# ═══════════════════════════════════════════════════════════════════════════════════
#                                ᴅᴀᴛᴀʙᴀsᴇ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ
# ═══════════════════════════════════════════════════════════════════════════════════

# ᴍᴏɴɢᴏᴅʙ ᴄᴏɴɴᴇᴄᴛɪᴏɴ
DB_URI = os.environ.get(
    "DATABASE_URL", 
    "mongodb+srv://rNbt/?retryWrites=true&w=majority&appName=Cluster0"
)
DB_URL = DB_URI  # ᴀʟɪᴀs ғᴏʀ ᴄᴏᴍᴘᴀᴛɪʙɪʟɪᴛʏ
DB_NAME = os.environ.get("DATABASE_NAME", "H")

# ═══════════════════════════════════════════════════════════════════════════════════
#                                   ᴜɪ ᴄᴜsᴛᴏᴍɪᴢᴀᴛɪᴏɴ
# ═══════════════════════════════════════════════════════════════════════════════════

# ɪᴍᴀɢᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ғᴏʀ ʙᴏᴛ ɪɴᴛᴇʀғᴀᴄᴇ
PICS = (os.environ.get(
    "PICS", 
    "https://telegra.ph/file/5094c60f1122bbae9b3d9.jpg "
    "https://telegra.ph/file/463501fe337f02dc034ba.jpg "
    "https://telegra.ph/file/ad3486519fd59f73f7f46.jpg "
    "https://telegra.ph/file/8d4867e3d7d8e8db70f73.jpg "
    "https://telegra.ph/file/3b8897b58d83a512a56ac.jpg "
    "https://telegra.ph/file/11115f9a5c035e2d90bd8.jpg "
    "https://telegra.ph/file/a292bc4b99f9a1854f6d7.jpg "
    "https://telegra.ph/file/94aac0f8141dc44eadfc6.jpg "
    "https://telegra.ph/file/1f8d855fb7a70b4fcaf68.jpg "
    "https://telegra.ph/file/849b567f8072117353c5c.jpg "
    "https://telegra.ph/file/e8555407480d52ac1a6b7.jpg "
    "https://telegra.ph/file/2a301e221bf3c800bb48c.jpg "
    "https://telegra.ph/file/faefbf4a710eb05647d9c.jpg "
    "https://telegra.ph/file/6219c9d5edbeecfd3a45e.jpg "
    "https://telegra.ph/file/db1f952a28b0aa53bedb1.jpg "
    "https://telegra.ph/file/32797f53236187e9f5e1f.jpg "
    "https://telegra.ph/file/f1038a205b9db5018f1aa.jpg "
    "https://telegra.ph/file/88fb9950df687ff6caa58.jpg "
    "https://telegra.ph/file/63855c358fdd9a02c717c.jpg "
    "https://telegra.ph/file/34fb4b74d70bfc2e9d59c.jpg "
    "https://telegra.ph/file/e92c0b6efb0a77b316e04.jpg "
    "https://telegra.ph/file/2f3adfb321584ad39fd15.jpg"
)).split()

# sᴘᴇᴄɪᴀʟ ɪᴍᴀɢᴇs
FORCE_PIC = os.environ.get("FORCE_PIC", "https://ibb.co/wFHLPpK8")  # ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪᴍᴀɢᴇ
TOKEN_PIC = os.environ.get("TOKEN_PIC", "https://ibb.co/Pvf2yFTZ")  # ᴛᴏᴋᴇɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ ɪᴍᴀɢᴇ
START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/6219c9d5edbeecfd3a45e.jpg")

# ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ғɪʟᴇs
CUSTOM_CAPTION = os.environ.get(
    "CUSTOM_CAPTION", 
    "<b>» ʙʏ <a href=\"https://t.me/MRJHAPLU\">Mʀ Jʜᴀᴘʟᴜ ⚡</a></b>"
)

# ═══════════════════════════════════════════════════════════════════════════════════
#                                ᴘʀᴇᴍɪᴜᴍ ᴘʀɪᴄɪɴɢ
# ═══════════════════════════════════════════════════════════════════════════════════

# sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴘʀɪᴄᴇs (ɪɴ ɪɴʀ)
PRICE1 = "₹20"   # 1 ᴅᴀʏ
PRICE2 = "₹60"   # 1 ᴡᴇᴇᴋ  
PRICE3 = "₹180"   # 2 ᴡᴇᴇᴋs
PRICE4 = "₹340"  # 1 ᴍᴏɴᴛʜ
PRICE5 = "₹680"  # 2 ᴍᴏɴᴛʜs

# ᴘᴀʏᴍᴇɴᴛ ᴅᴇᴛᴀɪʟs
UPI_ID = "nyxking@ybl"                    # ᴜᴘɪ ɪᴅ ғᴏʀ ᴘᴀʏᴍᴇɴᴛs
QR_PIC = "https://ibb.co/mVDMPLwW"        # ǫʀ ᴄᴏᴅᴇ ɪᴍᴀɢᴇ

# ═══════════════════════════════════════════════════════════════════════════════════
#                                ʟᴏɢɢɪɴɢ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ
# ═══════════════════════════════════════════════════════════════════════════════════

# ʟᴏɢ ғɪʟᴇ sᴇᴛᴛɪɴɢs
LOG_FILE_NAME = "hentai-dekho.txt"

# ᴄᴏɴғɪɢᴜʀᴇ ʟᴏɢɢɪɴɢ sʏsᴛᴇᴍ
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,    # 50ᴍʙ ᴍᴀx ғɪʟᴇ sɪᴢᴇ
            backupCount=10        # ᴋᴇᴇᴘ 10 ʙᴀᴄᴋᴜᴘ ғɪʟᴇs
        ),
        logging.StreamHandler()   # ᴄᴏɴsᴏʟᴇ ᴏᴜᴛᴘᴜᴛ
    ]
)

# ʀᴇᴅᴜᴄᴇ ᴘʏʀᴏɢʀᴀᴍ ʟᴏɢ ᴠᴇʀʙᴏsɪᴛʏ
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    """
    ᴄʀᴇᴀᴛᴇ ᴀ ʟᴏɢɢᴇʀ ɪɴsᴛᴀɴᴄᴇ ғᴏʀ ᴀ sᴘᴇᴄɪғɪᴄ ᴍᴏᴅᴜʟᴇ
    
    ᴀʀɢs:
        name (str): ɴᴀᴍᴇ ᴏғ ᴛʜᴇ ᴍᴏᴅᴜʟᴇ
        
    ʀᴇᴛᴜʀɴs:
        logging.Logger: ᴄᴏɴғɪɢᴜʀᴇᴅ ʟᴏɢɢᴇʀ ɪɴsᴛᴀɴᴄᴇ
    """
    return logging.getLogger(name)
