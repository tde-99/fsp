
import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import OWNER_ID
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from database.database import *
import logging
import random
import string
import time
from shortzy import Shortzy

# Set up proper logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

def generate_token():
    """Generate random verification token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

async def get_shortlink(long_url):
    """Get a short link using dynamic settings"""
    try:
        # Get current token settings from database
        token_settings = await get_token_settings()
        api_url = token_settings.get('shortlink_url', '')
        api_key = token_settings.get('shortlink_key', '')
        
        if not api_url or not api_key:
            print("No shortlink API configured")
            return long_url
        
        shortzy = Shortzy(api_key=api_key, base_site=api_url)
        return await shortzy.convert(long_url)
    except Exception as e:
        print(f"Error creating short link: {e}")
        return long_url

def get_exp_time(seconds):
    """Convert seconds to human readable time"""
    if seconds <= 0:
        return "0 sᴇᴄs"
    
    periods = [('ᴅᴀʏs', 86400), ('ʜᴏᴜʀs', 3600), ('ᴍɪɴs', 60), ('sᴇᴄs', 1)]
    result = []
    
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value > 0:
                result.append(f'{int(period_value)} {period_name}')
    
    return ' '.join(result) if result else "0 sᴇᴄs"

async def create_verification_link(user_id: int, base_url: str):
    """Create verification link using dynamic settings"""
    try:
        # Generate unique token
        verify_token = generate_token()
        current_time = int(time.time())
        
        # Create verification URL
        verify_url = f"{base_url}?start=verify_{verify_token}_{user_id}"
        
        # Get short link using dynamic settings
        short_link = await get_shortlink(verify_url)
        
        # Update user verification status
        verify_data = {
            'is_verified': False,
            'verified_time': 0,
            'verify_token': verify_token,
            'link': short_link
        }
        
        await update_verify_status(user_id, verify_data)
        
        return short_link, verify_token
    except Exception as e:
        print(f"Error creating verification link: {e}")
        return None, None
    
async def check_banUser(filter, client, update):
    try:
        user_id = update.from_user.id
        return await ban_user_exist(user_id)
    except: #Exception as e:
        #print(f"!Error on check_banUser(): {e}")
        return False

async def check_admin(filter, client, update):
    #Admin_ids = await get_all_admins()
    try:
        user_id = update.from_user.id     
        return any([user_id == OWNER_ID, await admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in check_admin: {e}")
        return False

async def is_subscribed(filter, client, update):
    try:
        logging.info(f"Checking subscription for user {update.from_user.id}")
        
        Channel_ids = await db.get_all_channels()
        logging.info(f"Found {len(Channel_ids) if Channel_ids else 0} channels to check")
        
        if not Channel_ids:
            logging.info("No channels configured, allowing access")
            return True
            
        user_id = update.from_user.id
        
        if any([user_id == OWNER_ID, await db.admin_exist(user_id)]):
            logging.info(f"User {user_id} is admin/owner, allowing access")
            return True
            
        REQFSUB = await db.get_request_forcesub()
        logging.info(f"Request force-sub enabled: {REQFSUB}")
        
        for channel_id in Channel_ids:
            if not channel_id:
                continue
                
            logging.info(f"Checking user {user_id} in channel {channel_id}")
            
            try:
                member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
                logging.info(f"User {user_id} status in {channel_id}: {member.status}")
                
                if member.status not in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER):
                    logging.info(f"User {user_id} not properly joined {channel_id} (status: {member.status})")
                    if REQFSUB and await privateChannel(client, channel_id):
                        req_exists = await db.reqSent_user_exist(channel_id, user_id)
                        logging.info(f"Request exists for {user_id} in {channel_id}: {req_exists}")
                        if not req_exists:
                            return False
                    else:
                        return False
                        
            except UserNotParticipant:
                logging.info(f"User {user_id} not participant in {channel_id}")
                
                if REQFSUB and await privateChannel(client, channel_id):
                    req_exists = await db.reqSent_user_exist(channel_id, user_id)
                    logging.info(f"Request exists for {user_id} in {channel_id}: {req_exists}")
                    if not req_exists:
                        return False
                else:
                    logging.info(f"User {user_id} failed subscription check for {channel_id}")
                    return False
                    
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error checking {user_id} in {channel_id}: {error_msg}")
                
                # Handle bot permission errors
                if "403" in error_msg or "USER_NOT_PARTICIPANT" in error_msg:
                    logging.error(f"Bot doesn't have permission to check membership in {channel_id}")
                    
                    # Check if bot is admin in the channel
                    bot_is_admin = await check_bot_admin_status(client, channel_id)
                    if not bot_is_admin:
                        logging.error(f"Bot is not admin in channel {channel_id}. Please add bot as admin.")
                        # If bot is not admin, we can't verify membership, so deny access
                        return False
                    else:
                        # Bot is admin but still getting permission error - user likely not a member
                        logging.error(f"Bot is admin but can't check user {user_id} in {channel_id} - denying access")
                        if REQFSUB and await privateChannel(client, channel_id):
                            req_exists = await db.reqSent_user_exist(channel_id, user_id)
                            logging.info(f"Fallback: Request exists for {user_id} in {channel_id}: {req_exists}")
                            if not req_exists:
                                return False
                        else:
                            return False
                else:
                    # Other errors - deny access for safety
                    logging.error(f"Unexpected error checking {user_id} in {channel_id} - denying access")
                    return False
                
        logging.info(f"User {user_id} passed all subscription checks")
        return True
        
    except Exception as e:
        logging.error(f"Error in is_subscribed: {e}")
        return False

# Add helper function to check bot admin status
async def check_bot_admin_status(client, channel_id):
    try:
        bot_member = await client.get_chat_member(chat_id=channel_id, user_id=client.me.id)
        is_admin = bot_member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        logging.info(f"Bot admin status in {channel_id}: {is_admin} (status: {bot_member.status})")
        return is_admin
    except Exception as e:
        logging.error(f"Error checking bot admin status in {channel_id}: {e}")
        return False


# Add this new function for direct calls
async def check_subscription(client, message):
    """Direct call version without filter parameter"""
    return await is_subscribed(None, client, message)

# Helper function to check if channel is private
async def privateChannel(client, channel_id):
    try:
        chat_info = await client.get_chat(channel_id)
        is_private = not chat_info.username  # Private channels don't have usernames
        print(f"Channel {channel_id} is private: {is_private}")  # Debug
        return is_private
    except Exception as e:
        print(f"Error checking if channel {channel_id} is private: {e}")
        return True  # Assume private on error


#Chcek user subscription by specifying channel id and user id
async def is_userJoin(client, user_id, channel_id):
    # REQFSUB = await db.get_request_forcesub()
    try:
        member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}

    except UserNotParticipant:
        REQFSUB = await db.get_request_forcesub()

        if REQFSUB:
            try:
                chat_info = await client.get_chat(channel_id)
                is_private_channel = not chat_info.username

                if is_private_channel:
                    return await db.reqSent_user_exist(channel_id, user_id)
                else:
                    return False
            except Exception as e:
                print(f"! Exception in is_userJoin: {e}")
                return await db.reqSent_user_exist(channel_id, user_id)
            
        else:
            return False
        
    except Exception as e:
        print(f"! Exception in is_userJoin: {e}")
        return False
    
async def encode(string):
    try:
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        base64_string = (base64_bytes.decode("ascii")).strip("=")
        return base64_string
    except Exception as e:
        print(f'Error occured on encode, reason: {e}')

async def decode(base64_string):
    try:
        base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes) 
        string = string_bytes.decode("ascii")
        return string
    except Exception as e:
        print(f'Error occured on decode, reason: {e}')

async def get_messages(client, message_ids):
    try:
        messages = []
        total_messages = 0
        while total_messages != len(message_ids):
            temb_ids = message_ids[total_messages:total_messages+200]
            try:
                msgs = await client.get_messages(
                    chat_id=client.db_channel.id,
                    message_ids=temb_ids
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                msgs = await client.get_messages(
                    chat_id=client.db_channel.id,
                    message_ids=temb_ids
                )
            except:
                pass
            total_messages += len(temb_ids)
            messages.extend(msgs)
        return messages
    except Exception as e:
        print(f'Error occured on get_messages, reason: {e}')

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

def get_readable_uptime(seconds: int) -> str:
    """Convert seconds to readable time format with proper day/month handling"""
    if seconds <= 0:
        return "0s"
    
    # Define time units
    time_units = [
        (31536000, 'year', 'years'),    # 365 days
        (2592000, 'month', 'months'),   # 30 days  
        (604800, 'week', 'weeks'),      # 7 days
        (86400, 'day', 'days'),         # 24 hours
        (3600, 'hour', 'hours'),        # 60 minutes
        (60, 'minute', 'minutes'),      # 60 seconds
        (1, 'second', 'seconds')
    ]
    
    result = []
    remaining = seconds
    
    for unit_seconds, singular, plural in time_units:
        if remaining >= unit_seconds:
            count = remaining // unit_seconds
            remaining = remaining % unit_seconds
            
            # Use singular or plural form
            unit_name = singular if count == 1 else plural
            result.append(f"{count} {unit_name}")
            
            # Only show top 2 most significant units
            if len(result) >= 2:
                break
    
    # Join with commas and 'and' for the last item
    if len(result) == 1:
        return result[0]
    elif len(result) == 2:
        return f"{result[0]} and {result[1]}"
    else:
        return ", ".join(result[:-1]) + f" and {result[-1]}"



subscribed = filters.create(is_subscribed)
is_admin = filters.create(check_admin)
banUser = filters.create(check_banUser)
