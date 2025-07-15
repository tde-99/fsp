import time
import re
from datetime import datetime, timedelta
from bot import Bot
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import *
from config import *


def parse_time_duration(time_str):
    """Parse time duration string like '1m', '1h', '1d', '1M', '1y' to seconds"""
    time_units = {
        's': 1,           # seconds
        'm': 60,          # minutes
        'h': 3600,        # hours
        'd': 86400,       # days
        'M': 2592000,     # months (30 days)
        'y': 31536000     # years (365 days)
    }
    
    match = re.match(r'^(\d+)([smhdMy])$', time_str)
    if match:
        amount, unit = match.groups()
        return int(amount) * time_units[unit]
    return None

# Premium management commands
@Bot.on_message(filters.command('addpaid') & filters.private & filters.user(OWNER_ID))
async def add_premium_user_cmd(client: Client, message: Message):
    try:
        if len(message.command) != 3:
            return await message.reply(
                "<b>❌ Iɴᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ!</b>\n\n"
                "<b>Usᴀɢᴇ:</b> <code>/addpaid user_id duration</code>\n\n"
                "<b>Exᴀᴍᴘʟᴇs:</b>\n"
                "• <code>/addpaid 123456789 1m</code> (1 minute)\n"
                "• <code>/addpaid 123456789 1h</code> (1 hour)\n"
                "• <code>/addpaid 123456789 1d</code> (1 day)\n"
                "• <code>/addpaid 123456789 1M</code> (1 month)\n"
                "• <code>/addpaid 123456789 1y</code> (1 year)"
            )
        
        user_id = int(message.command[1])
        duration_str = message.command[2]
        
        duration_seconds = parse_time_duration(duration_str)
        if not duration_seconds:
            return await message.reply(
                "<b>❌ Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ғᴏʀᴍᴀᴛ!</b>\n\n"
                "<b>Vᴀʟɪᴅ ғᴏʀᴍᴀᴛs:</b>\n"
                "• <code>s</code> - seconds\n"
                "• <code>m</code> - minutes\n"
                "• <code>h</code> - hours\n"
                "• <code>d</code> - days\n"
                "• <code>M</code> - months\n"
                "• <code>y</code> - years\n\n"
                "<b>Exᴀᴍᴘʟᴇ:</b> <code>/addpaid 123456789 1M</code>"
            )
        
        success = await db.add_premium_user(user_id, duration_seconds)
        if success:
            # Calculate expiry time for display
            expiry_time = datetime.fromtimestamp(time.time() + duration_seconds)
            await message.reply(
                f"<b>✅ Pʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                f"👤 <b>Usᴇʀ ID:</b> <code>{user_id}</code>\n"
                f"⏰ <b>Dᴜʀᴀᴛɪᴏɴ:</b> <code>{duration_str}</code>\n"
                f"📅 <b>Exᴘɪʀᴇs ᴏɴ:</b> <code>{expiry_time.strftime('%Y-%m-%d %H:%M:%S')}</code>"
            )
        else:
            await message.reply("<b>❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!</b>")
            
    except ValueError:
        await message.reply("<b>❌ Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID!</b>")
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> <code>{e}</code>")

@Bot.on_message(filters.command('removepaid') & filters.private & filters.user(OWNER_ID))
async def remove_premium_user_cmd(client: Client, message: Message):
    try:
        if len(message.command) != 2:
            return await message.reply(
                "<b>❌ Iɴᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ!</b>\n\n"
                "<b>Usᴀɢᴇ:</b> <code>/removepaid user_id</code>\n\n"
                "<b>Exᴀᴍᴘʟᴇ:</b> <code>/removepaid 123456789</code>"
            )
        
        user_id = int(message.command[1])
        
        # Check if user exists in premium list
        user_info = await db.get_premium_user_info(user_id)
        if not user_info:
            return await message.reply(
                f"<b>❌ Usᴇʀ <code>{user_id}</code> ɪs ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!</b>"
            )
        
        success = await db.remove_premium_user(user_id)
        if success:
            await message.reply(
                f"<b>✅ Pʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                f"👤 <b>Usᴇʀ ID:</b> <code>{user_id}</code>"
            )
        else:
            await message.reply("<b>❌ Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!</b>")
            
    except ValueError:
        await message.reply("<b>❌ Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID!</b>")
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> <code>{e}</code>")

@Bot.on_message(filters.command('listpaid') & filters.private & filters.user(OWNER_ID))
async def list_premium_users_cmd(client: Client, message: Message):
    try:
        premium_users = await db.get_premium_users()
        
        if not premium_users:
            return await message.reply("<b>📋 Nᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ғᴏᴜɴᴅ!</b>")
        
        text = "<b>💎 Pʀᴇᴍɪᴜᴍ Usᴇʀs Lɪsᴛ</b>\n\n"
        
        for idx, user in enumerate(premium_users, 1):
            user_id = user['_id']
            expiry_time = datetime.fromtimestamp(user['expiry_time'])
            added_time = datetime.fromtimestamp(user.get('added_time', 0))
            
            # Calculate remaining time
            remaining_seconds = user['expiry_time'] - time.time()
            if remaining_seconds > 0:
                remaining_days = int(remaining_seconds // 86400)
                remaining_hours = int((remaining_seconds % 86400) // 3600)
                remaining_mins = int((remaining_seconds % 3600) // 60)
                
                if remaining_days > 0:
                    remaining_str = f"{remaining_days}d {remaining_hours}h"
                elif remaining_hours > 0:
                    remaining_str = f"{remaining_hours}h {remaining_mins}m"
                else:
                    remaining_str = f"{remaining_mins}m"
            else:
                remaining_str = "Expired"
            
            text += (
                f"<b>{idx}.</b> <code>{user_id}</code>\n"
                f"   📅 <b>Added:</b> {added_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"   ⏰ <b>Expires:</b> {expiry_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"   ⏳ <b>Remaining:</b> {remaining_str}\n\n"
            )
        
        text += f"<b>📊 Total Premium Users:</b> <code>{len(premium_users)}</code>"
        
        await message.reply(text)
        
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> <code>{e}</code>")

@Bot.on_message(filters.command('free') & filters.private & filters.user(OWNER_ID))
async def toggle_free_mode_cmd(client: Client, message: Message):
    try:
        current_mode = await db.get_free_mode()
        new_mode = not current_mode
        
        success = await db.set_free_mode(new_mode)
        if success:
            mode_text = "Eɴᴀʙʟᴇᴅ ✅" if new_mode else "Dɪsᴀʙʟᴇᴅ ❌"
            status_text = "Users can access files for free" if new_mode else "Premium subscription required"
            
            await message.reply(
                f"<b>🔄 Fʀᴇᴇ Mᴏᴅᴇ {mode_text}</b>\n\n"
            )
        else:
            await message.reply("<b>❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ғʀᴇᴇ ᴍᴏᴅᴇ!</b>")
            
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> <code>{e}</code>")

# Command to check premium status (for users)
@Bot.on_message(filters.command('premium') & filters.private)
async def check_premium_status_cmd(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        user_info = await db.get_premium_user_info(user_id)
        
        if user_info:
            expiry_time = datetime.fromtimestamp(user_info['expiry_time'])
            remaining_seconds = user_info['expiry_time'] - time.time()
            
            if remaining_seconds > 0:
                remaining_days = int(remaining_seconds // 86400)
                remaining_hours = int((remaining_seconds % 86400) // 3600)
                remaining_mins = int((remaining_seconds % 3600) // 60)
                
                if remaining_days > 0:
                    remaining_str = f"{remaining_days} days {remaining_hours} hours"
                elif remaining_hours > 0:
                    remaining_str = f"{remaining_hours} hours {remaining_mins} minutes"
                else:
                    remaining_str = f"{remaining_mins} minutes"
                
                await message.reply(
                    f"<b>💎 Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b>\n\n"
                    f"✅ <b>Status:</b> Active\n"
                    f"📅 <b>Expires on:</b> {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"⏳ <b>Time remaining:</b> {remaining_str}"
                )
            else:
                await message.reply(
                    f"<b>💎 Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b>\n\n"
                    f"❌ <b>Status:</b> Expired\n\n"
                    f"<i>Contact admin to renew your premium subscription.</i>"
                )
        else:
            free_mode = await db.get_free_mode()
            status_text = "You can access files for free" if free_mode else "Premium subscription required"
            
            await message.reply(
                f"<b>💎 Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b>\n\n"
                f"❌ <b>Status:</b> Not Premium\n\n"
                f"📋 <b>Current Mode:</b> {status_text}\n\n"
                f"<i>Contact admin to get premium subscription.</i>"
            )
            
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> <code>{e}</code>")
