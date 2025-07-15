
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from helper_func import encode, get_message_id, is_admin

@Bot.on_message(filters.command('batch') & filters.private & is_admin)
async def batch(client: Client, message: Message):    
    while True:
        try:
            first_message = await client.ask(text = "<b><blockquote>Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Fɪʀsᴛ Mᴇssᴀɢᴇ ғʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>\n<blockquote>Oʀ Sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ Pᴏsᴛ Lɪɴᴋ</blockquote></b>", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            #await message.delete()
            break
        else:
            await first_message.reply("<b>❌ Eʀʀᴏʀ..\n<blockquote>Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ</blockquote></b>", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "<b><blockquote>Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Lᴀsᴛ Mᴇssᴀɢᴇ ғʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>\n<blockquote>Oʀ Sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ Pᴏsᴛ Lɪɴᴋ</blockquote></b>", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            #await message.delete()
            break
        else:
            await second_message.reply("<b>❌ Eʀʀᴏʀ..\n<blockquote>Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ</blockquote></b>", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Sʜᴀʀᴇ URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<blockquote><b>Jʜᴀᴘʟᴜ Bᴀᴅᴍᴏs</blockquote>\n\n<blockquote>Bᴇʟᴏᴡ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n{link}</blockquote></b>", quote=True, reply_markup=reply_markup, disable_web_page_preview=True)


# @Bot.on_message(filters.command('genlink') & filters.private & is_admin)
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "<b><blockquote>Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Mᴇssᴀɢᴇ ғʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>\n<blockquote>Oʀ Sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ Pᴏsᴛ Lɪɴᴋ</blockquote></b>", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            #await message.delete()
            break
        else:
            await channel_message.reply("<b>❌ Eʀʀᴏʀ..\n<blockquote>Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ</blockquote></b>", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Sʜᴀʀᴇ URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<blockquote><b>Jʜᴀᴘʟᴜ Bᴀᴅᴍᴏs</blockquote>\n\nBᴇʟᴏᴡ ɪs ʏᴏᴜʀ ʟɪɴᴋ:</b>\n<blockquote>{link}</blockquote>", quote=True, reply_markup=reply_markup, disable_web_page_preview=True)
