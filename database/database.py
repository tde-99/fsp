import motor.motor_asyncio
from config import DB_URI, DB_NAME
import time

# Create an async MongoDB client
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# Define the collections
user_data = database['users']
channel_data = database['channels']
admins_data = database['admins']
banned_user_data = database['banned_user']
autho_user_data = database['autho_user']

auto_delete_data = database['auto_delete']
hide_caption_data = database['hide_caption']
protect_content_data = database['protect_content']
channel_button_data = database['channel_button']
used_transactions = database['used_transactions']
message_reactions = database['message_reactions']
# Collection references
del_timer_data = database['del_timer']
channel_button_link_data = database['channelButton_link']
rqst_fsub_Channel_data = database['rqst_fsub_channels']
store_reqLink_data = database['store_reqLink']
request_forcesub_data = database['request_forcesub']
premium_users_data = database['premium_users']
free_mode_data = database['free_mode']
verify_status_data = database['verify_status']
token_settings_data = database['token_settings']


default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "", 
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        },
        'premium': False,  # Add this line
        'premium_expiry': 0 , # Add this line
        'referrals':0,
        'referral_points': 0,
        'purchased_points': 0 ,
        'purchased_files': [],
        'free_media_count': 0
    }


# Create a class to group functions for easier access
class DatabaseFunctions:

    async def add_reaction(message_id, user_id, reaction_type):
        """Add or update user reaction (like/dislike)"""
        try:
            await message_reactions.update_one(
                {"message_id": message_id, "user_id": user_id},
                {"$set": {"reaction": reaction_type, "timestamp": time.time()}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error adding reaction: {e}")
            return False
    
    async def get_user_reaction(message_id, user_id):
        """Get user's current reaction for a message"""
        try:
            reaction = await message_reactions.find_one({"message_id": message_id, "user_id": user_id})
            return reaction["reaction"] if reaction else None
        except Exception as e:
            print(f"Error getting user reaction: {e}")
            return None

    async def get_message_stats(message_id):
        """Get like/dislike stats for a message"""
        try:
            likes = await message_reactions.count_documents({"message_id": message_id, "reaction": "like"})
            dislikes = await message_reactions.count_documents({"message_id": message_id, "reaction": "dislike"})
            return likes, dislikes
        except Exception as e:
            print(f"Error getting message stats: {e}")
            return 0, 0
    # ==================== TOKEN SETTINGS MANAGEMENT ====================
    async def get_token_settings(self):
        """Get current token settings"""
        try:
            result = await token_settings_data.find_one({"_id": "token_config"})
            if result:
                return {
                    'shortlink_url': result.get('shortlink_url', ''),
                    'shortlink_key': result.get('shortlink_key', ''),
                    'verify_expire': result.get('verify_expire', 86400),  # 24 hours default
                    'updated_time': result.get('updated_time', 0)
                }
            else:
                # Return default settings
                default_settings = {
                    'shortlink_url': '',
                    'shortlink_key': '',
                    'verify_expire': 86400,  # 24 hours
                    'updated_time': 0
                }
                await self.update_token_settings(default_settings)
                return default_settings
        except Exception as e:
            print(f"Error getting token settings: {e}")
            return {
                'shortlink_url': '',
                'shortlink_key': '',
                'verify_expire': 86400,
                'updated_time': 0
            }
    
    async def update_token_settings(self, settings: dict):
        """Update token settings"""
        try:
            import time
            settings['updated_time'] = int(time.time())
            
            await token_settings_data.update_one(
                {"_id": "token_config"},
                {"$set": settings},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error updating token settings: {e}")
            return False
    
    async def set_shortlink_url(self, url: str):
        """Set shortlink URL"""
        try:
            current_settings = await self.get_token_settings()
            current_settings['shortlink_url'] = url
            return await self.update_token_settings(current_settings)
        except Exception as e:
            print(f"Error setting shortlink URL: {e}")
            return False
    
    async def set_shortlink_key(self, key: str):
        """Set shortlink API key"""
        try:
            current_settings = await self.get_token_settings()
            current_settings['shortlink_key'] = key
            return await self.update_token_settings(current_settings)
        except Exception as e:
            print(f"Error setting shortlink key: {e}")
            return False
    
    async def set_verify_expire(self, expire_seconds: int):
        """Set verification expiry time"""
        try:
            current_settings = await self.get_token_settings()
            current_settings['verify_expire'] = expire_seconds
            return await self.update_token_settings(current_settings)
        except Exception as e:
            print(f"Error setting verify expire: {e}")
            return False
        
    # ==================== VERIFICATION MANAGEMENT ====================
    async def get_verify_status(self, user_id: int):
        """Get user verification status"""
        try:
            result = await verify_status_data.find_one({"_id": user_id})
            if result:
                return result
            else:
                # Return default verification status
                default_status = {
                    '_id': user_id,
                    'is_verified': False,
                    'verified_time': 0,
                    'verify_token': "",
                    'link': ""
                }
                return default_status
        except Exception as e:
            print(f"Error getting verify status: {e}")
            return {
                '_id': user_id,
                'is_verified': False,
                'verified_time': 0,
                'verify_token': "",
                'link': ""
            }
    
    async def update_verify_status(self, user_id: int, verify_data: dict):
        """Update user verification status"""
        try:
            await verify_status_data.update_one(
                {"_id": user_id},
                {"$set": verify_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error updating verify status: {e}")
            return False
    
    async def set_user_verified(self, user_id: int, verify_token: str = "", verified_time: int = 0, link: str = ""):
        """Set user as verified"""
        try:
            verify_data = {
                'is_verified': True,
                'verified_time': verified_time,
                'verify_token': verify_token,
                'link': link
            }
            return await self.update_verify_status(user_id, verify_data)
        except Exception as e:
            print(f"Error setting user verified: {e}")
            return False
    
    async def is_user_verified(self, user_id: int):
        """Check if user is verified and not expired"""
        try:
            import time
            current_time = time.time()
            verify_status = await self.get_verify_status(user_id)
            
            if not verify_status.get('is_verified', False):
                return False
            
            # Get dynamic expiry time from settings
            token_settings = await self.get_token_settings()
            verify_expire = token_settings.get('verify_expire', 86400)  # Default 24 hours
            
            # Check if verification is expired
            verified_time = verify_status.get('verified_time', 0)
            if current_time - verified_time > verify_expire:
                # Reset verification status
                await self.update_verify_status(user_id, {
                    'is_verified': False,
                    'verified_time': 0,
                    'verify_token': "",
                    'link': ""
                })
                return False
            
            return True
        except Exception as e:
            print(f"Error checking user verification: {e}")
            return False


    
    # ==================== PREMIUM USER MANAGEMENT ====================
    async def add_premium_user(self, user_id: int, duration_seconds: int):
        try:
            expiry_time = time.time() + duration_seconds
            await premium_users_data.update_one(
                {'_id': user_id},
                {'$set': {'expiry_time': expiry_time, 'added_time': time.time()}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error adding premium user: {e}")
            return False

    async def is_premium_user(self, user_id: int):
        """Check if user has active premium"""
        try:
            current_time = time.time()
            user = await premium_users_data.find_one({"_id": user_id})
            if user and user.get("expiry_time", 0) > current_time:
                return True
            return False
        except Exception as e:
            print(f"Error checking premium user: {e}")
            return False

    async def remove_premium_user(self, user_id: int):
        try:
            result = await premium_users_data.delete_one({'_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error removing premium user: {e}")
            return False

    async def get_premium_users(self):
        try:
            current_time = time.time()
            # Remove expired users first
            await premium_users_data.delete_many({'expiry_time': {'$lt': current_time}})
            
            # Get active premium users
            users = await premium_users_data.find().to_list(length=None)
            return users
        except Exception as e:
            print(f"Error getting premium users: {e}")
            return []

    async def get_premium_user_info(self, user_id: int):
        """Get premium user information"""
        try:
            current_time = time.time()
            user = await premium_users_data.find_one({"_id": user_id})
            if user and user.get("expiry_time", 0) > current_time:
                return user
            return None
        except Exception as e:
            print(f"Error getting premium user info: {e}")
            return None
        
    async def add_premium_user_days(self, user_id: int, days: int):
        """Add premium subscription for specified days"""
        try:
            current_time = time.time()
            expiry_time = current_time + (days * 24 * 60 * 60)
            
            # Check if user already has premium
            existing_user = await premium_users_data.find_one({"_id": user_id})
            
            if existing_user and existing_user.get("expiry_time", 0) > current_time:
                # Extend existing premium
                new_expiry = existing_user["expiry_time"] + (days * 24 * 60 * 60)
                await premium_users_data.update_one(
                    {"_id": user_id},
                    {"$set": {"expiry_time": new_expiry}}
                )
            else:
                # Add new premium or reactivate expired
                await premium_users_data.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "expiry_time": expiry_time,
                            "added_time": current_time
                        }
                    },
                    upsert=True
                )
            return True
        except Exception as e:
            print(f"Error adding premium user: {e}")
            return False
        
    async def get_premium_users_count(self):
        """Get count of active premium users"""
        try:
            current_time = time.time()
            count = await premium_users_data.count_documents({"expiry_time": {"$gt": current_time}})
            return count
        except Exception as e:
            print(f"Error getting premium users count: {e}")
            return 0
    
    async def get_all_premium_users(self):
        """Get all active premium users"""
        try:
            current_time = time.time()
            users = premium_users_data.find({"expiry_time": {"$gt": current_time}})
            return [user["_id"] async for user in users]
        except Exception as e:
            print(f"Error getting all premium users: {e}")
            return []
    
    async def remove_expired_premium_users(self):
        """Remove expired premium users"""
        try:
            current_time = time.time()
            result = await premium_users_data.delete_many({"expiry_time": {"$lt": current_time}})
            return result.deleted_count
        except Exception as e:
            print(f"Error removing expired premium users: {e}")
            return 0
        

# ==================== FREE MODE MANAGEMENT ====================
    async def get_free_mode(self):
        """Get free mode status"""
        try:
            result = await free_mode_data.find_one({"_id": "free_mode"})
            return result.get("enabled", True) if result else True
        except Exception as e:
            print(f"Error getting free mode: {e}")
            return True
    
    async def set_free_mode(self, enabled: bool):
        """Set free mode status"""
        try:
            await free_mode_data.update_one(
                {"_id": "free_mode"},
                {"$set": {"enabled": enabled}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error setting free mode: {e}")
            return False
        
    # ==================== REQUEST FORCE-SUB MANAGEMENT ====================
    
    # Get the request force-sub setting
    async def get_request_forcesub(self):
        data = await request_forcesub_data.find_one({})
        return data.get('value', False) if data else False

    # Set the request force-sub setting
    async def set_request_forcesub(self, value: bool):
        existing = await request_forcesub_data.find_one({})
        if existing:
            await request_forcesub_data.update_one({}, {'$set': {'value': value}})
        else:
            await request_forcesub_data.insert_one({'value': value})

    # Initialize a channel with an empty user_ids array
    async def add_reqChannel(self, channel_id: int):
        await rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$setOnInsert': {'user_ids': []}},
            upsert=True
        )

    # Set the request_forcesub mode for a specific channel
    async def set_request_forcesub_channel(self, channel_id: int, fsub_mode: bool):
        await rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$set': {'fsub_mode': fsub_mode}},
            upsert=True
        )

    # Add user to the channel's set
    async def reqSent_user(self, channel_id: int, user_id: int):
        await rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$addToSet': {'user_ids': user_id}},
            upsert=True
        )

    # Remove a user from the channel's set
    async def del_reqSent_user(self, channel_id: int, user_id: int):
        await rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$pull': {'user_ids': user_id}}
        )

    # Clear all users from a channel
    async def clear_reqSent_user(self, channel_id: int):
        if await self.reqChannel_exist(channel_id):
            await rqst_fsub_Channel_data.update_one(
                {'_id': channel_id},
                {'$set': {'user_ids': []}}
            )

    # Check if a user exists in a channel's set
    async def reqSent_user_exist(self, channel_id: int, user_id: int):
        found = await rqst_fsub_Channel_data.find_one(
            {'_id': channel_id, 'user_ids': user_id}
        )
        return bool(found)

    # Remove an entire channel
    async def del_reqChannel(self, channel_id: int):
        await rqst_fsub_Channel_data.delete_one({'_id': channel_id})

    # Check if a channel exists
    async def reqChannel_exist(self, channel_id: int):
        found = await rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return bool(found)

    # Get all users for a channel
    async def get_reqSent_user(self, channel_id: int):
        data = await rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return data.get('user_ids', []) if data else []

    # Get all channel IDs from rqst_fsub_Channel_data
    async def get_reqChannel(self):
        channel_docs = await rqst_fsub_Channel_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    # Get all channel IDs from store_reqLink_data
    async def get_reqLink_channels(self):
        channel_docs = await store_reqLink_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    # Get the stored link for a specific channel
    async def get_stored_reqLink(self, channel_id: int):
        data = await store_reqLink_data.find_one({'_id': channel_id})
        return data.get('link') if data else None

    # Store or update the link for a channel
    async def store_reqLink(self, channel_id: int, link: str):
        await store_reqLink_data.update_one(
            {'_id': channel_id},
            {'$set': {'link': link}},
            upsert=True
        )

    # Delete the stored link for a channel
    async def del_stored_reqLink(self, channel_id: int):
        await store_reqLink_data.delete_one({'_id': channel_id})

    # Set the channel button link
    async def set_channel_button_link(self, button_name: str, button_link: str):
        await channel_button_link_data.delete_many({})
        await channel_button_link_data.insert_one({'button_name': button_name, 'button_link': button_link})

    # Get the channel button link
    async def get_channel_button_link(self):
        data = await channel_button_link_data.find_one({})
        if data:
            return data.get('button_name'), data.get('button_link')
        return 'Join Channel', 'https://t.me/btth480p'

    # Set/Delete Timer
    async def set_del_timer(self, value: int):
        existing = await del_timer_data.find_one({})
        if existing:
            await del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 600

    # Set/Auto Delete
    async def set_auto_delete(self, value: bool):
        existing = await auto_delete_data.find_one({})
        if existing:
            await auto_delete_data.update_one({}, {'$set': {'value': value}})
        else:
            await auto_delete_data.insert_one({'value': value})

    async def set_hide_caption(self, value: bool):
        existing = await hide_caption_data.find_one({})
        if existing:
            await hide_caption_data.update_one({}, {'$set': {'value': value}})
        else:
            await hide_caption_data.insert_one({'value': value})

    async def set_protect_content(self, value: bool):
        existing = await protect_content_data.find_one({})
        if existing:
            await protect_content_data.update_one({}, {'$set': {'value': value}})
        else:
            await protect_content_data.insert_one({'value': value})

    async def set_channel_button(self, value: bool):
        existing = await channel_button_data.find_one({})
        if existing:
            await channel_button_data.update_one({}, {'$set': {'value': value}})
        else:
            await channel_button_data.insert_one({'value': value})

    # Get settings
    async def get_auto_delete(self):
        data = await auto_delete_data.find_one({})
        if data:
            return data.get('value', False)
        return False

    async def get_hide_caption(self):
        data = await hide_caption_data.find_one({})
        if data:
            return data.get('value', False)
        return False

    async def get_protect_content(self):
        data = await protect_content_data.find_one({})
        if data:
            return data.get('value', False)
        return False

    async def get_channel_button(self):
        data = await channel_button_data.find_one({})
        if data:
            return data.get('value', False)
        return False

    # User Management
    async def present_user(self, user_id: int):
        found = await user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_docs = await user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def del_user(self, user_id: int):
        await user_data.delete_one({'_id': user_id})
        return

    # Channel Management
    async def channel_exist(self, channel_id: int):
        found = await channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await channel_data.insert_one({'_id': channel_id})
            return

    async def del_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await channel_data.delete_one({'_id': channel_id})
            return

    async def get_all_channels(self):
        channel_docs = await channel_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    # Admin Management
    async def admin_exist(self, admin_id: int):
        found = await admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids

    # Banned User Management
    async def ban_user_exist(self, user_id: int):
        found = await banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids

# Create the db instance
db = DatabaseFunctions()

# For backward compatibility, keep the standalone functions
async def present_user(user_id: int):
    return await db.present_user(user_id)

async def add_user(user_id: int):
    return await db.add_user(user_id)

async def full_userbase():
    return await db.full_userbase()

async def del_user(user_id: int):
    return await db.del_user(user_id)

async def channel_exist(channel_id: int):
    return await db.channel_exist(channel_id)

async def add_channel(channel_id: int):
    return await db.add_channel(channel_id)

async def del_channel(channel_id: int):
    return await db.del_channel(channel_id)

async def get_all_channels():
    return await db.get_all_channels()

async def admin_exist(admin_id: int):
    return await db.admin_exist(admin_id)

async def add_admin(admin_id: int):
    return await db.add_admin(admin_id)

async def del_admin(admin_id: int):
    return await db.del_admin(admin_id)

async def get_all_admins():
    return await db.get_all_admins()

async def ban_user_exist(user_id: int):
    return await db.ban_user_exist(user_id)

async def add_ban_user(user_id: int):
    return await db.add_ban_user(user_id)

async def del_ban_user(user_id: int):
    return await db.del_ban_user(user_id)

async def get_ban_users():
    return await db.get_ban_users()

async def get_auto_delete():
    return await db.get_auto_delete()

async def get_del_timer():
    return await db.get_del_timer()

async def get_hide_caption():
    return await db.get_hide_caption()

async def get_channel_button():
    return await db.get_channel_button()

async def get_protect_content():
    return await db.get_protect_content()

async def get_channel_button_link():
    return await db.get_channel_button_link()

async def set_auto_delete(value: bool):
    return await db.set_auto_delete(value)

async def set_del_timer(value: int):
    return await db.set_del_timer(value)

async def set_hide_caption(value: bool):
    return await db.set_hide_caption(value)

async def set_channel_button(value: bool):
    return await db.set_channel_button(value)

async def set_protect_content(value: bool):
    return await db.set_protect_content(value)

async def set_channel_button_link(button_name: str, button_link: str):
    return await db.set_channel_button_link(button_name, button_link)

# Request Force-Sub backward compatibility functions
async def get_request_forcesub():
    return await db.get_request_forcesub()

async def set_request_forcesub(value: bool):
    return await db.set_request_forcesub(value)

async def add_reqChannel(channel_id: int):
    return await db.add_reqChannel(channel_id)

async def set_request_forcesub_channel(channel_id: int, fsub_mode: bool):
    return await db.set_request_forcesub_channel(channel_id, fsub_mode)

async def reqSent_user(channel_id: int, user_id: int):
    return await db.reqSent_user(channel_id, user_id)

async def del_reqSent_user(channel_id: int, user_id: int):
    return await db.del_reqSent_user(channel_id, user_id)

async def clear_reqSent_user(channel_id: int):
    return await db.clear_reqSent_user(channel_id)

async def reqSent_user_exist(channel_id: int, user_id: int):
    return await db.reqSent_user_exist(channel_id, user_id)

async def del_reqChannel(channel_id: int):
    return await db.del_reqChannel(channel_id)

async def reqChannel_exist(channel_id: int):
    return await db.reqChannel_exist(channel_id)

async def get_reqSent_user(channel_id: int):
    return await db.get_reqSent_user(channel_id)

async def get_reqChannel():
    return await db.get_reqChannel()

async def get_reqLink_channels():
    return await db.get_reqLink_channels()

async def get_stored_reqLink(channel_id: int):
    return await db.get_stored_reqLink(channel_id)

async def store_reqLink(channel_id: int, link: str):
    return await db.store_reqLink(channel_id, link)

async def del_stored_reqLink(channel_id: int):
    return await db.del_stored_reqLink(channel_id)

async def add_premium_user(user_id: int, duration_seconds: int):
    return await db.add_premium_user(user_id, duration_seconds)

# Add these standalone functions after your DatabaseFunctions class
async def is_premium_user(user_id: int):
    """Check if user has active premium - standalone function"""
    return await db.is_premium_user(user_id)

async def get_premium_user_info(user_id: int):
    """Get premium user information - standalone function"""
    return await db.get_premium_user_info(user_id)

async def add_premium_user_days(user_id: int, days: int):
    """Add premium subscription for specified days - standalone function"""
    return await db.add_premium_user_days(user_id, days)

async def get_free_mode():
    """Get free mode status - standalone function"""
    return await db.get_free_mode()

async def set_free_mode(enabled: bool):
    """Set free mode status - standalone function"""
    return await db.set_free_mode(enabled)
async def get_verify_status(user_id: int):
    return await db.get_verify_status(user_id)

async def update_verify_status(user_id: int, verify_data: dict):
    return await db.update_verify_status(user_id, verify_data)

async def is_user_verified(user_id: int):
    return await db.is_user_verified(user_id)

async def set_user_verified(user_id: int, verify_token: str = "", verified_time: int = 0, link: str = ""):
    return await db.set_user_verified(user_id, verify_token, verified_time, link)

async def get_token_settings():
    return await db.get_token_settings()

async def update_token_settings(settings: dict):
    return await db.update_token_settings(settings)

async def set_shortlink_url(url: str):
    return await db.set_shortlink_url(url)

async def set_shortlink_key(key: str):
    return await db.set_shortlink_key(key)

async def set_verify_expire(expire_seconds: int):
    return await db.set_verify_expire(expire_seconds)

async def add_reaction(message_id, user_id, reaction_type):
    """Add or update user reaction (like/dislike)"""
    return await DatabaseFunctions.add_reaction(message_id, user_id, reaction_type)

async def get_user_reaction(message_id, user_id):
    """Get user's current reaction for a message"""
    return await DatabaseFunctions.get_user_reaction(message_id, user_id)

async def get_message_stats(message_id):
    """Get like/dislike stats for a message"""
    return await DatabaseFunctions.get_message_stats(message_id)