#@mrxbotx

import os
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
import time
import re
from datetime import datetime, timedelta

from bot import Bot
from config import *
from helper_func import banUser, is_userJoin, is_admin, subscribed, encode, decode, get_messages
from database.database import db
import subprocess
import sys
from plugins.advance_features import auto_del_notification, delete_message
from plugins.FORMATS import *

on_txt = "🟢 Eɴᴀʙʟᴇᴅ"
off_txt = "🔴 Dɪsᴀʙʟᴇᴅ"

import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatAction
from bot import Bot
from config import OWNER_ID
from database.database import db, verify_status_data, user_data

@Bot.on_message(filters.command('verify_stats') & filters.private & filters.user(OWNER_ID))
async def verification_stats_command(client: Client, message: Message):
    """Show verification statistics"""
    await message.reply_chat_action(ChatAction.TYPING)
    
    try:
        stats_text, reply_markup = await get_verification_stats("today")
        
        await message.reply_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        print(f"Error in verification stats: {e}")
        await message.reply_text(
            f"❌ <b>ᴇʀʀᴏʀ ɢᴇᴛᴛɪɴɢ sᴛᴀᴛs:</b>\n<code>{str(e)}</code>",
            parse_mode=ParseMode.HTML
        )

async def get_verification_stats(period="today"):
    """Get verification statistics for specified period"""
    now = datetime.now()
    
    if period == "today":
        start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
        end_date = datetime(now.year, now.month, now.day, 23, 59, 59)
        period_text = f"ᴛᴏᴅᴀʏ ({now.strftime('%d/%m')})"
    else:  # weekly
        start_date = now - timedelta(days=7)
        end_date = now
        period_text = f"ᴡᴇᴇᴋʟʏ ({start_date.strftime('%d/%m')} - {now.strftime('%d/%m')})"
    
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    # Get total users
    total_users = len(await db.full_userbase())
    
    # Get users verified in period
    verified_period_cursor = verify_status_data.find({
        "is_verified": True,
        "verified_time": {
            "$gte": start_timestamp,
            "$lte": end_timestamp
        }
    })
    
    verified_period_list = await verified_period_cursor.to_list(length=None)
    verified_period_count = len(verified_period_list)
    
    # Get currently verified users
    token_settings = await db.get_token_settings()
    verify_expire = token_settings.get('verify_expire', 86400)
    current_time = int(time.time())
    
    currently_verified_cursor = verify_status_data.find({
        "is_verified": True,
        "verified_time": {"$gt": current_time - verify_expire}
    })
    
    currently_verified_list = await currently_verified_cursor.to_list(length=None)
    currently_verified_count = len(currently_verified_list)
    
    # Calculate stats
    not_verified_count = total_users - currently_verified_count
    verification_rate = (currently_verified_count/total_users*100) if total_users > 0 else 0
    activity_rate = (verified_period_count/total_users*100) if total_users > 0 else 0
    
    # Format expiry time
    expire_hours = verify_expire // 3600
    if expire_hours < 24:
        expire_text = f"{expire_hours}ʜ"
    else:
        expire_days = expire_hours // 24
        expire_text = f"{expire_days}ᴅ"
    
    # Create stats text
    stats_text = f"""
📊 <b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴛᴀᴛs</b>

📅 <b>{period_text}:</b>
├ ✅ ᴠᴇʀɪғɪᴇᴅ: <code>{verified_period_count}</code>
├ 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total_users}</code>
└ ⏰ ᴇxᴘɪʀᴇs: <code>{expire_text}</code>

🔄 <b>ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs:</b>
├ ✅ ᴀᴄᴛɪᴠᴇ: <code>{currently_verified_count}</code>
├ ❌ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ: <code>{not_verified_count}</code>
└ 📈 ʀᴀᴛᴇ: <code>{verification_rate:.1f}%</code>

⚡ <b>ɪɴsɪɢʜᴛs:</b>
├ 🎯 ᴀᴄᴛɪᴠɪᴛʏ: <code>{activity_rate:.1f}%</code>
└ 🔄 ᴇxᴘɪʀᴇs ᴇᴠᴇʀʏ <code>{expire_text}</code>
"""

    # Create buttons
    if period == "today":
        buttons = [
            [InlineKeyboardButton("📊 ᴡᴇᴇᴋʟʏ", callback_data="vstats_weekly")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("📅 ᴛᴏᴅᴀʏ", callback_data="vstats_today")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
        ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    return stats_text, reply_markup

@Bot.on_callback_query(filters.regex("^vstats_"))
async def handle_stats_callback(client: Client, query: CallbackQuery):
    """Handle verification stats callbacks"""
    await query.answer()
    
    try:
        period = query.data.split("_")[1]  # today or weekly
        stats_text, reply_markup = await get_verification_stats(period)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        print(f"Error handling stats callback: {e}")
        await query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ sᴛᴀᴛs", show_alert=True)


@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def start_command(client: Client, message: Message): 
    await message.reply_chat_action(ChatAction.CHOOSE_STICKER)
    user_id = message.from_user.id  
    
    # Add user to database if not present
    if not await db.present_user(user_id):
        try: 
            await db.add_user(user_id)
        except: 
            pass
    
    text = message.text
    
    # Handle start command with parameters
    if len(text) > 7:
        await message.delete()
        
        try: 
            base64_string = text.split(" ", 1)[1]
        except: 
            return
        
        # Handle verification
        if base64_string.startswith('verify_'):
            await handle_verification(client, message, base64_string)
            return
        
        # Handle file sharing
        await handle_file_sharing(client, message, base64_string)
    else:
        # Handle simple start command
        await handle_start_message(client, message)

async def handle_verification(client: Client, message: Message, verify_string: str):
    """Handle user verification process"""
    try:
        # Parse verification data: verify_token_userid
        parts = verify_string.replace('verify_', '').split('_')
        if len(parts) != 2:
            return await message.reply("❌ <b>Iɴᴠᴀʟɪᴅ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ</b>")
        
        verify_token, target_user_id = parts
        target_user_id = int(target_user_id)
        current_user_id = message.from_user.id
        
        # Check if user is verifying their own link
        if current_user_id != target_user_id:
            return await message.reply("❌ <b>Tʜɪs ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ</b>")
        
        # Get user's verification status
        verify_status = await db.get_verify_status(current_user_id)
        
        # Check if token matches
        if verify_status.get('verify_token') != verify_token:
            return await message.reply("❌ <b>Iɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ</b>")
        
        # Check if already verified
        if await db.is_user_verified(current_user_id):
            return await message.reply("✅ <b>Yᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪғɪᴇᴅ..!</b>")
        
        # Verify the user
        import time
        current_time = int(time.time())
        success = await db.set_user_verified(
            user_id=current_user_id,
            verify_token=verify_token,
            verified_time=current_time,
            link=verify_status.get('link', '')
        )
        
        if success:
            await message.reply(
                "✅ <b>Vᴇʀɪғɪᴄᴀᴛɪᴏɴ Sᴜᴄᴄᴇssғᴜʟ..!</b>\n\n"
            )
        else:
            await message.reply("❌ <b>Verification failed. Please try again.</b>")
            
    except Exception as e:
        print(f"Error in verification: {e}")
        await message.reply("❌ <b>Verification error. Please try again.</b>")

async def handle_file_sharing(client: Client, message: Message, base64_string: str):
    """Handle file sharing with access control"""
    user_id = message.from_user.id
    
    # Check access permissions
    has_access = await check_user_access(user_id)
    if not has_access:
        await send_access_required_message(client, message)
        return
    
    # Decode and process file request
    string = await decode(base64_string)
    argument = string.split("-")
    
    if len(argument) == 3:
        try:
            start = int(int(argument[1]) / abs(client.db_channel.id))
            end = int(int(argument[2]) / abs(client.db_channel.id))
        except:
            return
        
        if start <= end:
            ids = range(start, end + 1)
        else:
            ids = list(range(start, end - 1, -1))
            
    elif len(argument) == 2:
        try: 
            ids = [int(int(argument[1]) / abs(client.db_channel.id))]
        except: 
            return
    else:
        return
    
    # Send files
    await send_files_to_user(client, message, ids, user_id)

async def check_user_access(user_id: int) -> bool:
    """Check if user has access (premium or verified)"""
    try:
        # Check if user is premium
        is_premium = await db.is_premium_user(user_id)
        if is_premium:
            return True
        
        # Check free mode
        free_mode = await db.get_free_mode()
        if free_mode:
            return True
        
        # Check if user is verified
        is_verified = await db.is_user_verified(user_id)
        if is_verified:
            return True
        
        return False
    except Exception as e:
        print(f"Error checking user access: {e}")
        return False

async def send_access_required_message(client: Client, message: Message):
    """Send message when user needs premium or verification"""
    try:
        from helper_func import create_verification_link, get_exp_time
        from database.database import get_token_settings
        
        user_id = message.from_user.id
        bot_username = client.me.username
        base_url = f"https://t.me/{bot_username}"
        
        # Get token settings for expiry time
        token_settings = await get_token_settings()
        verify_expire = token_settings.get('verify_expire', 86400)
        expire_text = get_exp_time(verify_expire)
        
        # Check if user is already verified
        is_verified = await db.is_user_verified(user_id)
        if is_verified:
            verify_status = await db.get_verify_status(user_id)
            verified_time = verify_status.get('verified_time', 0)
            current_time = int(time.time())
            remaining_seconds = verify_expire - (current_time - verified_time)
            
            if remaining_seconds > 0:
                remaining_time = get_exp_time(remaining_seconds)
                access_text = (
                    f"✅ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪғɪᴇᴅ!</b>\n\n"
                    f"👋 ʜɪ {message.from_user.first_name}!\n\n"
                    f"⏰ <b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴇxᴘɪʀᴇs ɪɴ:</b> {remaining_time}\n\n"
                    f"🎯 ʏᴏᴜʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪs ᴀᴄᴛɪᴠᴇ. ᴛʀʏ ᴀᴄᴄᴇssɪɴɢ ᴛʜᴇ ғɪʟᴇ ᴀɢᴀɪɴ.\n\n"
                )
                
                access_buttons = [
                    [InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")],
                    [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
                ]
                
                await message.reply_text(
                    text=access_text,
                    reply_markup=InlineKeyboardMarkup(access_buttons),
                    parse_mode=ParseMode.HTML
                )
                return
        
        # Create verification link for non-verified users
        verify_link, verify_token = await create_verification_link(user_id, base_url)
        
        if verify_link:
            access_buttons = [
                [InlineKeyboardButton(f"• ᴠᴇʀɪғʏ ɴᴏᴡ •", url=verify_link)],
                [InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ (ᴜɴʟɪᴍɪᴛᴇᴅ) •", callback_data="buy_prem")],
                [InlineKeyboardButton("• ɴᴇᴡ ᴠᴇʀɪғʏ ʟɪɴᴋ •", callback_data="new_verify_link"),
                InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
            ]
        else:
            access_buttons = [
                [InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")],
                [InlineKeyboardButton("• ᴛʀʏ ᴠᴇʀɪғʏ ᴀɢᴀɪɴ •", callback_data="new_verify_link"),
                InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
            ]
        
        await message.reply_photo(
            photo=TOKEN_PIC,
            caption=PREM_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(access_buttons),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        print(f"Error sending access required message: {e}")
        # Fallback message
        await message.reply_text(
            "🔒 <b>ᴀᴄᴄᴇss ʀᴇǫᴜɪʀᴇᴅ</b>\n\n"
            "ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴀᴄᴄᴇss ᴍᴇᴛʜᴏᴅ:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")],
                [InlineKeyboardButton("• ɢᴇᴛ ᴠᴇʀɪғʏ ʟɪɴᴋ •", callback_data="new_verify_link")],
                [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
            ]),
            parse_mode=ParseMode.HTML
        )

async def send_files_to_user(client: Client, message: Message, ids: list, user_id: int):
    """Send files to user with proper settings"""
    try:
        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)
        
        # Get messages
        try: 
            messages = await get_messages(client, ids)
        except: 
            return await message.reply("<b>Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!</b>")
        
        # Get bot settings
        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(
            db.get_auto_delete(), 
            db.get_del_timer(), 
            db.get_hide_caption(), 
            db.get_channel_button(), 
            db.get_protect_content()
        )
        
        if CHNL_BTN: 
            button_name, button_link = await db.get_channel_button_link()
        
        last_message = None
        
        # Send each file
        for idx, msg in enumerate(messages):
            # Prepare caption using the improved function
            caption = await prepare_caption(msg, HIDE_CAPTION)
            
            # Prepare reply markup
            if CHNL_BTN:
                reply_markup = await prepare_reply_markup(msg, CHNL_BTN, button_name, button_link)
            else:
                reply_markup = msg.reply_markup   
            
            try:
                copied_msg = await msg.copy(
                    chat_id=message.chat.id ,  # Changed from hardcoded chat_id to message.chat.id
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_MODE
                )
                await asyncio.sleep(0.1)
                
                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: 
                        last_message = copied_msg
                        
            except FloodWait as e:
                # Fixed: Use 'value' instead of 'x' for newer Pyrogram versions
                wait_time = getattr(e, 'value', getattr(e, 'x', 1))
                await asyncio.sleep(wait_time)
                copied_msg = await msg.copy(
                    chat_id=message.chat.id ,  # Changed from hardcoded chat_id to message.chat.id
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_MODE
                )
                await asyncio.sleep(0.1)
                
                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: 
                        last_message = copied_msg
        
        # Send auto-delete notification
        if AUTO_DEL and last_message:
            asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))
            
    except Exception as e:
        print(f"Error sending files: {e}")
        await message.reply("❌ <b>Error sending files. Please try again.</b>")


async def prepare_caption(msg, hide_caption: bool) -> str:
    """Prepare caption for the message"""
    try:
        from config import CUSTOM_CAPTION
        
        # If hide_caption is enabled, return empty caption for all media types
        if hide_caption:
            return ""
        
        # Handle custom caption for different media types
        if bool(CUSTOM_CAPTION):
            previous_caption = "" if not msg.caption else msg.caption.html
            
            if bool(msg.document):
                filename = msg.document.file_name or "Document"
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename=filename
                )
            elif bool(msg.photo):
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename="Photo"
                )
            elif bool(msg.video):
                filename = msg.video.file_name or "Video"
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename=filename
                )
            elif bool(msg.audio):
                filename = msg.audio.file_name or f"{msg.audio.performer or 'Unknown'} - {msg.audio.title or 'Audio'}"
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename=filename
                )
            elif bool(msg.voice):
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename="Voice Message"
                )
            elif bool(msg.video_note):
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename="Video Note"
                )
            elif bool(msg.animation):  # GIF support
                filename = msg.animation.file_name or "Animation"
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename=filename
                )
            elif bool(msg.sticker):
                sticker_name = msg.sticker.set_name or "Sticker"
                emoji = msg.sticker.emoji or "🎭"
                return CUSTOM_CAPTION.format(
                    previouscaption=previous_caption, 
                    filename=f"{emoji} {sticker_name}"
                )
            else:
                # For any other media type, use original caption
                return previous_caption
        
        # If no custom caption, return original caption or empty string
        return "" if not msg.caption else msg.caption.html
        
    except Exception as e:
        print(f"Error preparing caption: {e}")
        # Fallback: return original caption or empty string
        return "" if not msg.caption else msg.caption.html


async def prepare_reply_markup(msg, chnl_btn: bool, button_name: str = None, button_link: str = None):
    """Prepare reply markup for the message"""
    try:
        if chnl_btn and button_name and button_link:
            # Add channel button for media files
            if (msg.document or msg.photo or msg.video or msg.audio or 
                msg.voice or msg.video_note or msg.animation or msg.sticker):
                return InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]])
            else:
                return msg.reply_markup
        else:
            return msg.reply_markup
    except Exception as e:
        print(f"Error preparing reply markup: {e}")
        return msg.reply_markup

async def handle_start_message(client: Client, message: Message):
    """Handle simple start command"""
    try:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('🤖 Aʙᴏᴜᴛ ᴍᴇ', callback_data='about'), 
             InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='setting')]
        ])
        
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id = 5104841245755180586 #🔥
        )
        
        try: 
            await message.delete()
        except: 
            pass
            
    except Exception as e:
        print(f"Error handling start message: {e}")



   
#=====================================================================================##
#------------- HANDLE FORCE MESSAGE -------------
#=====================================================================================##   

# Global dictionary to store channel data
chat_data_cache = {}

@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    temp = await message.reply(f"<b>??</b>")
    
    user_id = message.from_user.id
    REQFSUB = await db.get_request_forcesub()
    
    buttons = []
    count = 0

    try:
        for total, chat_id in enumerate(await db.get_all_channels(), start=1):
            await message.reply_chat_action(ChatAction.PLAYING)
            
            # Show the join button of non-subscribed Channels.....
            if not await is_userJoin(client, user_id, chat_id):
                try:
                    # Check if chat data is in cache
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]  # Get data from cache
                    else:
                        data = await client.get_chat(chat_id)  # Fetch from API
                        chat_data_cache[chat_id] = data  # Store in cache
                    
                    cname = data.title
                    
                    # Handle private channels and links
                    if REQFSUB and not data.username:
                        link = await db.get_stored_reqLink(chat_id)
                        await db.add_reqChannel(chat_id)
                        if not link:
                            link = (await client.create_chat_invite_link(chat_id=chat_id, creates_join_request=True)).invite_link
                            await db.store_reqLink(chat_id, link)
                    else:
                        link = data.invite_link
                    
                    # Add button for the chat
                    buttons.append([InlineKeyboardButton(text=cname, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")
                    
                except Exception as e:
                    print(f"Can't Export Channel Name and Link..., Please Check If the Bot is admin in the FORCE SUB CHANNELS:\nProvided Force sub Channel:- {chat_id}")
                    return await temp.edit(f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @mrxbotx</i></b>\n<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")

        # Add try again button
        try:
            buttons.append([InlineKeyboardButton(text='♻️ Tʀʏ Aɢᴀɪɴ', url=f"https://t.me/{client.username}?start={message.command[1]}")])
        except IndexError:
            pass

        await temp.delete()

        # Reply with force-sub message
        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username='@' + message.from_user.username if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id,
                count=count,
                total=total
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        try: 
            await message.delete()
        except: 
            pass
            
    except Exception as e:
        print(f"Unable to perform forcesub buttons reason : {e}")
        return await temp.edit(f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @mrxbotx</i></b>\n<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")


#=====================================================================================##
#------------- REQUEST FORCE-SUB HANDLERS -------------
#=====================================================================================##

@Bot.on_callback_query(filters.regex("^req_fsub$"))
async def req_fsub_handler(client, query):
    await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
    try:
        on = off = ""
        if await db.get_request_forcesub():
            on = "🟢"
            texting = on_txt
        else:
            off = "🔴"
            texting = off_txt
        
        buttons = [
            [InlineKeyboardButton(f"{on} ON", callback_data="chng_req"),
             InlineKeyboardButton(f"{off} OFF", callback_data="chng_req")],
            [InlineKeyboardButton("⚙️ Mᴏʀᴇ Sᴇᴛᴛɪɴɢs ⚙️", callback_data="more_settings")]
        ]
        
        await query.message.edit_text(
            text=RFSUB_CMD_TXT.format(req_mode=texting),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        print(f"! Error Occurred on callback data = 'req_fsub' : {e}")

@Bot.on_callback_query(filters.regex("^req_fsub$"))
async def req_fsub_handler(client, query):
    await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
    try:
        on = off = ""
        if await db.get_request_forcesub():
            on = "🟢"
            texting = on_txt
        else:
            off = "🔴"
            texting = off_txt
        
        buttons = [
            [InlineKeyboardButton(f"{on} ON", callback_data="chng_req"),
             InlineKeyboardButton(f"{off} OFF", callback_data="chng_req")],
            [InlineKeyboardButton("⚙️ Mᴏʀᴇ Sᴇᴛᴛɪɴɢs ⚙️", callback_data="more_settings")]
        ]
        
        await query.message.edit_text(
            text=RFSUB_CMD_TXT.format(req_mode=texting),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        print(f"! Error Occurred on callback data = 'req_fsub' : {e}")

@Bot.on_message(filters.command('req_fsub') & filters.private & ~banUser & filters.user(OWNER_ID))
async def handle_reqFsub(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    try:
        on = off = ""
        if await db.get_request_forcesub():
            on = "🟢"
            texting = on_txt
        else:
            off = "🔴"
            texting = off_txt
        
        button = [
            [InlineKeyboardButton(f"{on} ON", callback_data="chng_req"), 
             InlineKeyboardButton(f"{off} OFF", callback_data="chng_req")],
            [InlineKeyboardButton("⚙️ Mᴏʀᴇ Sᴇᴛᴛɪɴɢs ⚙️", callback_data="more_settings")]
        ]
        
        await message.reply(
            text=RFSUB_CMD_TXT.format(req_mode=texting), 
            reply_markup=InlineKeyboardMarkup(button)
        )
        #message_effect_id=5046509860389126442
    except Exception as e:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]])
        await message.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote><b><i>Cᴏɴᴛᴀɴᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @rohit_1888</i></b>", reply_markup=reply_markup)


#=====================================================================================##
#.........Extra Features .......#
#=====================================================================================##

@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    print("Restarting bot...")
    msg = await message.reply(text=f"<b><i><blockquote>⚠️ {client.name} ɢᴏɪɴɢ ᴛᴏ Rᴇsᴛᴀʀᴛ...</blockquote></i></b>")
    try:
        await asyncio.sleep(6)  # Wait for 6 seconds before restarting
        await msg.delete()
        args = [sys.executable, "main.py"]  # Adjust this if your start file is named differently
        os.execl(sys.executable, *args)
    except Exception as e:
        print(f"Error occured while Restarting the bot: {e}")
        return await msg.edit_text(f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @mrxbotx</i>\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")