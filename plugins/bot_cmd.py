
import os
import asyncio
from asyncio import Lock
from bot import Bot
from config import *
import time
from datetime import datetime 
from pyrogram import Client, filters
from helper_func import *
from plugins.FORMATS import HELP_TEXT, BAN_TXT, CMD_TXT, USER_CMD_TXT, FSUB_CMD_TXT
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.database import add_user, del_user, full_userbase, present_user, get_ban_users, ban_user_exist
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

REPLY_ERROR = """Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ Tᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ sᴘᴀᴄᴇs."""
# Define a global variable to store the cancel state
is_canceled = False
cancel_lock = Lock()

#Settings for banned users..
@Bot.on_message(banUser & filters.private & filters.command(['start', 'help']))
async def handle_banuser(client, message):
    return await message.reply(text=BAN_TXT, message_effect_id=5046589136895476101,)#💩)

#--------------------------------------------------------------[[ADMIN COMMANDS]]---------------------------------------------------------------------------#
# Handler for the /cancel command
@Bot.on_message(filters.command('cancel') & filters.private & is_admin)
async def cancel_broadcast(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True

@Bot.on_message(filters.command('broadcast') & filters.private & is_admin)
async def send_text(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = False
    mode = False
    broad_mode = ''
    store = message.text.split()[1:]
    
    if store and len(store) == 1 and store[0] == 'silent':
        mode = True
        broad_mode = 'SILENT '

    if message.reply_to_message:
        query = await full_userbase()
        
        # Get admin list and add OWNER_ID to skip list
        admin_list = await get_all_admins()
        skip_list = set(admin_list)  # Convert to set for faster lookup
        skip_list.add(OWNER_I)  # Add owner ID to skip list
        
        # Filter out admins and owner from broadcast list
        filtered_query = [user_id for user_id in query if user_id not in skip_list]
        
        broadcast_msg = message.reply_to_message
        total = len(filtered_query)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        skipped = len(query) - len(filtered_query)  # Count of skipped users

        pls_wait = await message.reply("<i>Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ Mᴇssᴀɢᴇ... Tʜɪs ᴡɪʟʟ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ.</i>")
        bar_length = 20
        final_progress_bar = "●" * bar_length
        complete_msg = f"🤖 {broad_mode}BROADCAST COMPLETED ✅"
        progress_bar = ''
        last_update_percentage = 0
        percent_complete = 0
        update_interval = 0.05  # Update progress bar every 5%

        for i, chat_id in enumerate(filtered_query, start=1):
            async with cancel_lock:
                if is_canceled:
                    final_progress_bar = progress_bar
                    complete_msg = f"🤖 {broad_mode}BROADCAST CANCELED ❌"
                    break
            try:
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1

            # Calculate percentage complete
            percent_complete = i / total

            # Update progress bar
            if percent_complete - last_update_percentage >= update_interval or last_update_percentage == 0:
                num_blocks = int(percent_complete * bar_length)
                progress_bar = "●" * num_blocks + "○" * (bar_length - num_blocks)
    
                # Send periodic status updates
                status_update = f"""<b>🤖 {broad_mode}BROADCAST IN PROGRESS...

<blockquote>⏳:</b> [{progress_bar}] <code>{percent_complete:.0%}</code></blockquote>

<b>🚻 Tᴏᴛᴀʟ Usᴇʀs: <code>{len(query)}</code>
👥 Sᴋɪᴘᴘᴇᴅ (Aᴅᴍɪɴs): <code>{skipped}</code>
📤 Tᴀʀɢᴇᴛ Usᴇʀs: <code>{total}</code>
✅ Sᴜᴄᴄᴇssғᴜʟ: <code>{successful}</code>
🚫 Bʟᴏᴄᴋᴇᴅ Usᴇʀs: <code>{blocked}</code>
⚠️ Dᴇʟᴇᴛᴇᴅ Aᴄᴄᴏᴜɴᴛs: <code>{deleted}</code>
❌ Uɴsᴜᴄᴄᴇssғᴜʟ: <code>{unsuccessful}</code></b>

<i>➪ Tᴏ sᴛᴏᴘ ᴛʜᴇ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴄʟɪᴄᴋ: <b>/cancel</b></i>"""
                await pls_wait.edit(status_update)
                last_update_percentage = percent_complete

        # Final status update
        final_status = f"""<b>{complete_msg}

<blockquote>Dᴏɴᴇ:</b> [{final_progress_bar}] {percent_complete:.0%}</blockquote>

<b>🚻 Tᴏᴛᴀʟ Usᴇʀs: <code>{len(query)}</code>
👥 Sᴋɪᴘᴘᴇᴅ (Aᴅᴍɪɴs): <code>{skipped}</code>
📤 Tᴀʀɢᴇᴛ Usᴇʀs: <code>{total}</code>
✅ Sᴜᴄᴄᴇssғᴜʟ: <code>{successful}</code>
🚫 Bʟᴏᴄᴋᴇᴅ Usᴇʀs: <code>{blocked}</code>
⚠️ Dᴇʟᴇᴛᴇᴅ Aᴄᴄᴏᴜɴᴛs: <code>{deleted}</code>
❌ Uɴsᴜᴄᴄᴇssғᴜʟ: <code>{unsuccessful}</code></b>"""
        return await pls_wait.edit(final_status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()


from database.database import get_all_admins


def parse_time(time_str):
    """Parse time string like '1h', '30m', '2d' into seconds"""
    if not time_str:
        return None
    
    time_str = time_str.lower().strip()
    
    # Extract number and unit
    if time_str[-1] in ['s', 'm', 'h', 'd']:
        try:
            number = int(time_str[:-1])
            unit = time_str[-1]
        except ValueError:
            return None
    else:
        try:
            # If no unit provided, assume minutes
            number = int(time_str)
            unit = 'm'
        except ValueError:
            return None
    
    # Convert to seconds
    multipliers = {
        's': 1,      # seconds
        'm': 60,     # minutes
        'h': 3600,   # hours
        'd': 86400   # days
    }
    
    return number * multipliers.get(unit, 60)  # default to minutes

def format_time(seconds):
    """Format seconds into readable time string"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds // 60} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} hours {minutes} minutes"
        return f"{hours} hours"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if hours > 0:
            return f"{days} days {hours} hours"
        return f"{days} days"

@Bot.on_message(filters.command('deluser') & filters.private & is_admin)
async def delete_user_from_db(client: Bot, message: Message):
    args = message.text.split()[1:]
    
    if not args:
        return await message.reply(
            "<b>❌ Please provide user ID(s)</b>\n\n"
            "<code>/deluser 123456789</code>\n"
            "<code>/deluser 123456789 987654321</code>"
        )
    
    deleted = []
    not_found = []
    invalid = []
    
    for user_id in args:
        try:
            user_id = int(user_id)
            if await present_user(user_id):
                await del_user(user_id)
                deleted.append(str(user_id))
            else:
                not_found.append(str(user_id))
        except ValueError:
            invalid.append(user_id)
    
    # Build response
    response = "<b>🗑️ USER DELETION RESULT:</b>\n\n"
    
    if deleted:
        response += f"✅ <b>Deleted:</b> <code>{', '.join(deleted)}</code>\n"
    if not_found:
        response += f"❌ <b>Not Found:</b> <code>{', '.join(not_found)}</code>\n"
    if invalid:
        response += f"⚠️ <b>Invalid IDs:</b> <code>{', '.join(invalid)}</code>\n"
    
    await message.reply(response)


@Bot.on_message(filters.command('dbroadcast') & filters.private & is_admin)
async def broadcast_all_users(client: Bot, message: Message):
    if message.reply_to_message:
        args = message.text.split()[1:]
        
        auto_delete_seconds = 600  # Default: 10 minutes
        delete_time_str = "10 minutes"
        
        if args:
            parsed_time = parse_time(args[0])
            if parsed_time:
                auto_delete_seconds = parsed_time
                delete_time_str = format_time(auto_delete_seconds)
            else:
                error_msg = await message.reply(
                    "<b>❌ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ!</b>\n\n"
                    "<blockquote><b>ᴜsᴀɢᴇ:</b> <code>/dbroadcast [time]</code>\n\n"
                    "<b>ᴇxᴀᴍᴘʟᴇs:</b>\n"
                    "• <code>/dbroadcast 30s</code> - 30 seconds\n"
                    "• <code>/dbroadcast 5m</code> - 5 minutes\n"
                    "• <code>/broadcast 1h</code> - 1 hour\n"
                    "• <code>/dbroadcast 2d</code> - 2 days\n"
                    "• <code>/dbroadcast 45</code> - 45 minutes (default unit)</blockquote>"
                )
                await asyncio.sleep(10)
                return await error_msg.delete()

        query = await full_userbase()
        admin_ids = await get_all_admins()
        admin_ids.append(OWNER_I)

        # Filter: Remove admins from the list
        target_users = [user_id for user_id in query if user_id not in admin_ids]

        broadcast_msg = message.reply_to_message
        total = len(target_users)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        sent_messages = []

        pls_wait = await message.reply(
            f"<i>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ <b>{total}</b> ᴜsᴇʀs sɪʟᴇɴᴛʟʏ...\n"
            f"⏰ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ: {delete_time_str}</i>"
        )

        for chat_id in target_users:
            try:
                sent_msg = await broadcast_msg.copy(chat_id, disable_notification=True)
                sent_messages.append((chat_id, sent_msg.id))
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                try:
                    sent_msg = await broadcast_msg.copy(chat_id, disable_notification=True)
                    sent_messages.append((chat_id, sent_msg.id))
                    successful += 1
                except:
                    unsuccessful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1

        final_status = f"""<b>✅ sɪʟᴇɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!

📊 ʙʀᴏᴀᴅᴄᴀsᴛ sᴜᴍᴍᴀʀʏ:
🚻 ᴛᴏᴛᴀʟ ᴜsᴇʀs ɪɴ ᴅʙ: <code>{len(query)}</code>
👥 ᴀᴅᴍɪɴs sᴋɪᴘᴘᴇᴅ: <code>{len(admin_ids)}</code>
🎯 ᴛᴀʀɢᴇᴛᴇᴅ ᴜsᴇʀs: <code>{total}</code>
✅ sᴜᴄᴄᴇssғᴜʟ: <code>{successful}</code>
🚫 ʙʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>
⚠️ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: <code>{deleted}</code>
❌ ᴜɴsᴜᴄᴄᴇssғᴜʟ: <code>{unsuccessful}</code></b>

<i>🔕 ᴀʟʟ ᴍᴇssᴀɢᴇs sᴇɴᴛ sɪʟᴇɴᴛʟʏ
⏰ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴀғᴛᴇʀ: {delete_time_str}</i>"""

        await pls_wait.edit(final_status)

        await asyncio.sleep(auto_delete_seconds)

        deleted_count = 0
        for chat_id, message_id in sent_messages:
            try:
                await client.delete_messages(chat_id, message_id)
                deleted_count += 1
            except:
                pass

        try:
            await pls_wait.edit(f"{final_status}\n\n<b>🗑️ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ {deleted_count}/{len(sent_messages)} ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇs</b>")
        except:
            pass
    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()



@Bot.on_message(filters.command('status') & filters.private & is_admin)
async def info(client: Bot, message: Message):   
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    #msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    
    start_time = time.time()
    temp_msg = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)  # Temporary message
    end_time = time.time()
    # Calculate ping time in milliseconds
    ping_time = (end_time - start_time) * 1000
    
    users = await full_userbase()
    now = datetime.now()
    delta = now - client.uptime
    bottime = get_readable_time(delta.seconds)
    
    await temp_msg.edit(f"🚻 : <b>{len(users)} ᴜsᴇʀ\n\n🤖 ᴜᴘᴛɪᴍᴇ » {bottime}\n\n📡 ᴘɪɴɢ » {ping_time:.2f} ms</b>", reply_markup = reply_markup,)


@Bot.on_message(filters.command('ronak') & filters.private & is_admin)
async def users_list(client: Bot, message: Message):   
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    
    temp_msg = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    
    try:
        users = await full_userbase()
        total_users = len(users)
        
        if total_users == 0:
            await temp_msg.edit("<b><blockquote>❌ Nᴏ Usᴇʀs Fᴏᴜɴᴅ ɪɴ Dᴀᴛᴀʙᴀsᴇ!</blockquote></b>", reply_markup=reply_markup)
            return
        
        user_list = ""
        count = 0
        
        for user_id in users:
            count += 1
            # await message.reply_chat_action(ChatAction.TYPING)
            
            try:
                user = await client.get_users(user_id)
                user_link = f"tg://openmessage?user_id={user_id}"
                first_name = user.first_name if user.first_name else "No Name"
                username = f"@{user.username}" if user.username else "No Username"
                
                user_list += f"<b>{count}. <a href='{user_link}'>{first_name}</a></b>\n"
                user_list += f"   <blockquote>ID: <code>{user_id}</code>\n   Username: {username}</blockquote>\n\n"
                
                # If message gets too long, send it and start a new one
                if len(user_list) > 3500:  # Telegram message limit is ~4096 chars
                    await temp_msg.edit(
                        f"<b>👥 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 ({count-50}-{count}/{total_users}):</b>\n\n{user_list}",
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )
                    
                    # Send continuation message
                    temp_msg = await message.reply("<b><i>Cᴏɴᴛɪɴᴜɪɴɢ....</i></b>")
                    user_list = ""
                    
            except Exception as e:
                user_list += f"<b>{count}. <blockquote>ID: <code>{user_id}</code>\n<i>Uɴᴀʙʟᴇ ᴛᴏ ʟᴏᴀᴅ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs</i></blockquote></b>\n\n"
                continue
        
        # Send final message
        await temp_msg.edit(
            f"<b>👥 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 (Total: {total_users}):</b>\n\n{user_list}",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await temp_msg.edit(
            f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote><b><i>Cᴏɴᴛᴀɴᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @mrxbotx</i></b>",
            reply_markup=reply_markup
        )


@Bot.on_message(filters.command('cmd') & filters.private & is_admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------#    

@Bot.on_message(filters.command('forcesub') & filters.private & ~banUser)
async def fsub_commands(client: Client, message: Message):
    button = [[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]]
    await message.reply(text=FSUB_CMD_TXT, reply_markup=InlineKeyboardMarkup(button), quote=True)


@Bot.on_message(filters.command('users') & filters.private & ~banUser)
async def user_setting_commands(client: Client, message: Message):
    button = [[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]]
    await message.reply(text=USER_CMD_TXT, reply_markup=InlineKeyboardMarkup(button), quote=True)

    
HELP = "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"
@Bot.on_message(filters.command('help') & filters.private & ~banUser)
async def help(client: Client, message: Message):
    if OWNER_ID:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('𝘚𝘵𝘪𝘭𝘭 𝘩𝘢𝘷𝘦 𝘥𝘰𝘶𝘣𝘵𝘴, 𝘊𝘰𝘯𝘵𝘢𝘤𝘵 𝘖𝘸𝘯𝘦𝘳', url=f"tg://openmessage?user_id={OWNER_ID}")]])
    else:
        reply_markup = None

    await message.reply_photo(
        photo = HELP,
        caption = HELP_TEXT.format(
            first = message.from_user.first_name,
            last = message.from_user.last_name,
            username = None if not message.from_user.username else '@' + message.from_user.username,
            mention = message.from_user.mention,
            id = message.from_user.id
        ),
        reply_markup = reply_markup,
    )
        
