from bot import Bot
from config import OWNER_ID
from database.database import admin_exist, get_token_settings
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from helper_func import get_exp_time
import time

# Admin filter
def admin_filter(_, __, message):
    return message.from_user.id == OWNER_ID or admin_exist(message.from_user.id)

admin_only = filters.create(admin_filter)

@Bot.on_message(filters.command('token') & filters.private & admin_only)
async def token_command(client: Client, message: Message):
    """Show token settings"""
    try:
        # await message.reply_chat_action("typing")
        
        # Get current settings
        settings = await get_token_settings()
        
        # Format settings display
        shortlink_url = settings.get('shortlink_url', '') or "ɴᴏᴛ sᴇᴛ"
        shortlink_key = settings.get('shortlink_key', '') or "ɴᴏᴛ sᴇᴛ"
        verify_expire = settings.get('verify_expire', 86400)
        updated_time = settings.get('updated_time', 0)
        
        # Mask API key for security
        if shortlink_key != "ɴᴏᴛ sᴇᴛ" and len(shortlink_key) > 8:
            masked_key = shortlink_key[:4] + "*" * (len(shortlink_key) - 8) + shortlink_key[-4:]
        else:
            masked_key = shortlink_key
        
        # Format expiry time
        expire_time = get_exp_time(verify_expire)
        
        # Format last updated
        if updated_time > 0:
            from datetime import datetime
            import pytz
            ist = pytz.timezone("Asia/Kolkata")
            last_updated = datetime.fromtimestamp(updated_time, ist).strftime('%d %b %Y, %I:%M %p')
        else:
            last_updated = "ɴᴇᴠᴇʀ"
        
        token_text = (
            f"🔧 <b>ᴛᴏᴋᴇɴ sᴇᴛᴛɪɴɢs</b>\n"
            f"🔗 <b>sʜᴏʀᴛ ᴜʀʟ:</b> <code>{shortlink_url}</code>\n"
            f"🔑 <b>ᴀᴘɪ ᴋᴇʏ:</b> <code>{masked_key}</code>\n"
            f"⏰ <b>ᴇxᴘɪʀᴇs ɪɴ:</b> {expire_time}\n"
            f"🕐 <b>ᴜᴘᴅᴀᴛᴇᴅ:</b> {last_updated}\n\n"
            f"💡 <i>ᴍᴀɴᴀɢᴇ ʙᴇʟᴏᴡ ↓</i>"
        )
        
        token_buttons = [
            [InlineKeyboardButton("🔗 sᴇᴛ ᴜʀʟ", callback_data="set_token_url"),
             InlineKeyboardButton("🔑 sᴇᴛ ᴋᴇʏ", callback_data="set_token_key")],
            [InlineKeyboardButton("⏰ sᴇᴛ ᴇxᴘɪʀᴇ", callback_data="set_token_expire")],
            [InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="refresh_token_settings")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
        ]
        
        await message.reply_text(
            text=token_text,
            reply_markup=InlineKeyboardMarkup(token_buttons),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        print(f"Error in token command: {e}")
        await message.reply("❌ <b>ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴛᴏᴋᴇɴ sᴇᴛᴛɪɴɢs</b>", parse_mode=ParseMode.HTML)
