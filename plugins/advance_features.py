#telegram username: @mrxbotx

from bot import Bot
import asyncio
from pyrogram.enums import ChatAction
from helper_func import is_admin, banUser
from plugins.FORMATS import autodel_cmd_pic, files_cmd_pic, on_txt, off_txt, FILES_CMD_TXT, AUTODEL_CMD_TXT
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from pyrogram import Client, filters
from database.database import add_channel, del_channel, get_all_channels, add_admin, del_admin, get_all_admins, get_del_timer, get_auto_delete, get_hide_caption, get_protect_content, get_channel_button, get_channel_button_link, add_ban_user, del_ban_user, get_ban_users
from datetime import datetime, timedelta

#Time conversion for auto delete
def convert_time(duration_seconds: int) -> str:
    periods = [
        ('Yᴇᴀʀ', 60 * 60 * 24 * 365),
        ('Mᴏɴᴛʜ', 60 * 60 * 24 * 30),
        ('Dᴀʏ', 60 * 60 * 24),
        ('Hᴏᴜʀ', 60 * 60),
        ('Mɪɴᴜᴛᴇ', 60),
        ('Sᴇᴄᴏɴᴅ', 1)
    ]

    parts = []
    for period_name, period_seconds in periods:
        if duration_seconds >= period_seconds:
            num_periods = duration_seconds // period_seconds
            duration_seconds %= period_seconds
            parts.append(f"{num_periods} {period_name}{'s' if num_periods > 1 else ''}")

    if len(parts) == 0:
        return "0 Sᴇᴄᴏɴᴅ"
    elif len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) +' ᴀɴᴅ '+ parts[-1]


@Bot.on_message(filters.command('add_fsub') & filters.private & filters.user(OWNER_ID))
async def add_forcesub(client:Client, message:Message):
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    check=0
    channel_ids = await get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    
    if not fsubs:
        return await pro.edit("<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ Aᴅᴅ ᴄʜᴀɴɴᴇʟ ɪᴅs\n<blockquote><u>EXAMPLE</u> :\n/add_fsub [channel_ids] :</b> ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀᴛ ᴀ ᴛɪᴍᴇ.</blockquote>", reply_markup=reply_markup)

    channel_list = ""
    for id in fsubs:
        try:
            id = int(id)
        except:
            channel_list += f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></blockquote></b>\n\n"
            continue
            
        if id in channel_ids:
            channel_list += f"<blockquote><b>ɪᴅ: <code>{id}</code>, ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ..</b></blockquote>\n\n"
            continue
            
        id = str(id)
        if id.startswith('-') and id[1:].isdigit() and len(id)==14:
            try:
                data = await client.get_chat(id)
                link = data.invite_link
                cname = data.title

                if not link:
                    link = await client.export_chat_invite_link(id)
                    
                channel_list += f"<b><blockquote>NAME: <a href = {link}>{cname}</a> (ID: <code>{id}</code>)</blockquote></b>\n\n"
                check+=1
                
            except:
                channel_list += f"<b><blockquote>ɪᴅ: <code>{id}</code>\n<i>ᴜɴᴀʙʟᴇ ᴛᴏ ᴀᴅᴅ ғᴏʀᴄᴇ-sᴜʙ, ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴏʀ ʙᴏᴛ ᴘᴇʀᴍɪsɪᴏɴs ᴘʀᴏᴘᴇʀʟʏ..</i></blockquote></b>\n\n"
            
        else:
            channel_list += f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></blockquote></b>\n\n"
            continue
    
    if check == len(fsubs):
        for id in fsubs:
            await add_channel(int(id))
        await pro.edit(f'<b>Fᴏʀᴄᴇ-Sᴜʙ Cʜᴀɴɴᴇʟ Aᴅᴅᴇᴅ ✅</b>\n\n{channel_list}', reply_markup=reply_markup, disable_web_page_preview = True)
        
    else:
        await pro.edit(f'<b>❌ Eʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ Aᴅᴅɪɴɢ Fᴏʀᴄᴇ-Sᴜʙ Cʜᴀɴɴᴇʟs</b>\n\n{channel_list.strip()}\n\n<b><i>Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ...</i></b>', reply_markup=reply_markup, disable_web_page_preview = True)


@Bot.on_message(filters.command('del_fsub') & filters.private & filters.user(OWNER_ID))
async def delete_all_forcesub(client:Client, message:Message):
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    channels = await get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])

    if not fsubs:
        return await pro.edit("<b>⁉️ Pʟᴇᴀsᴇ, Pʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ɪᴅs ᴏʀ ᴀʀɢᴜᴍᴇɴᴛs\n<blockquote><u>EXAMPLES</u> :\n/del_fsub [channel_ids] :</b> ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ sᴘᴇᴄɪғɪᴇᴅ ɪᴅs\n<code>/del_fsub all</code> : ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀᴄᴇ-sᴜʙ ɪᴅs</blockquote>", reply_markup=reply_markup)

    if len(fsubs) == 1 and fsubs[0].lower() == "all":
        if channels:
            for id in channels:
                await del_channel(id)
            ids = "\n".join([f"<code>{channel}</code> ✅" for channel in channels])
            return await pro.edit(f"<b>⛔️ Aʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ Cʜᴀɴɴᴇʟ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n<blockquote>{ids}</blockquote></b>", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>⁉️ Nᴏ Cʜᴀɴɴᴇʟ ɪᴅ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)
            
    if len(channels) >= 1:
        passed = ''
        for sub_id in fsubs:
            try:
                id = int(sub_id)
            except:
                passed += f"<b><blockquote><i>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{sub_id}</code></i></blockquote></b>\n"
                continue
            if id in channels:
                await del_channel(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += f"<b><blockquote><code>{id}</code> ɴᴏᴛ ɪɴ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs</blockquote></b>\n"
                
        await pro.edit(f"<b>⛔️ Pʀᴏᴠɪᴅᴇᴅ Cʜᴀɴɴᴇʟ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n\n{passed}</b>", reply_markup=reply_markup)
        
    else:
        await pro.edit("<b><blockquote>⁉️ Nᴏ Cʜᴀɴɴᴇʟ ɪᴅ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)
      

@Bot.on_message(filters.command('fsub_chnl') & filters.private & is_admin)
async def get_forcesub(client:Client, message: Message):
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    channels = await get_all_channels()
    channel_list = "<b><blockquote>❌ Nᴏ Fᴏʀᴄᴇ Sᴜʙ Cʜᴀɴɴᴇʟ Fᴏᴜɴᴅ !</b></blockquote>"
    if channels:
        channel_list = ""
        for id in channels:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                data = await client.get_chat(id)
                link = data.invite_link
                cname = data.title

                if not link:
                    link = await client.export_chat_invite_link(id)
                    
                channel_list += f"<b><blockquote>NAME: <a href = {link}>{cname}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n"
                
            except:
                channel_list += f"<b><blockquote>ɪᴅ: <code>{id}</code>\n<i>ᴜɴᴀʙʟᴇ ᴛᴏ ʟᴏᴀᴅ ᴏᴛʜᴇʀ ᴅᴇᴛᴀɪʟs..</i></blockquote></b>\n\n"
                
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(f"<b>⚡ 𝗙𝗢𝗥𝗖𝗘-𝗦𝗨𝗕 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗦𝗧 :</b>\n\n{channel_list}", reply_markup=reply_markup, disable_web_page_preview = True)


#Commands for adding Admins by Owner
@Bot.on_message(filters.command('add_admins') & filters.private & filters.user(OWNER_ID))
async def add_admins(client:Client, message:Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    check = 0
    admin_ids = await get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    
    if not admins:
        return await pro.edit("<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ Aᴅᴍɪɴ ɪᴅs\n<blockquote><u>EXAMPLE</u> :\n/add_admins [user_id] :</b> ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅ ᴀᴛ ᴀ ᴛɪᴍᴇ.</blockquote>", reply_markup=reply_markup)
    
    admin_list = ""
    for id in admins:
        try:
            id = int(id)
        except:
            admin_list += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></b></blockquote>\n"
            continue
            
        if id in admin_ids:
            admin_list += f"<blockquote><b>ɪᴅ: <code>{id}</code>, ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ..</b></blockquote>\n"
            continue
            
        id = str(id)  
        if id.isdigit() and len(id) == 10:
            admin_list += f"<b><blockquote>(ID: <code>{id}</code>)</blockquote></b>\n"
            check += 1
        else:
            admin_list += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></b></blockquote>\n"
            continue            
    
    if check == len(admins):
        for id in admins:
            await add_admin(int(id))
        await pro.edit(f'<b>Nᴇᴡ ɪᴅs Aᴅᴅᴇᴅ ɪɴ Aᴅᴍɪɴ Lɪsᴛ ✅</b>\n\n{admin_list}', reply_markup=reply_markup)
        
    else:
        await pro.edit(f'<b>❌ Eʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ Aᴅᴅɪɴɢ Aᴅᴍɪɴs</b>\n\n{admin_list.strip()}\n\n<b><i>Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ...</i></b>', reply_markup=reply_markup)
    #await update_fsub(1)


@Bot.on_message(filters.command('del_admins') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client:Client, message:Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    admin_ids = await get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])

    if not admins:
        return await pro.edit("<b>⁉️ Pʟᴇᴀsᴇ, Pʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ɪᴅs ᴏʀ ᴀʀɢᴜᴍᴇɴᴛs</b>\n<blockquote><b><u>EXAMPLES:</u>\n/del_admins [user_ids] :</b> ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ sᴘᴇᴄɪғɪᴇᴅ ɪᴅs\n<code>/del_admins all</code> : ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴜsᴇʀ ɪᴅs</blockquote>", reply_markup=reply_markup)

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await del_admin(id)
            ids = "\n".join([f"<code>{admin}</code> ✅" for admin in admin_ids])
            return await pro.edit(f"<b>⛔️ Aʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ Aᴅᴍɪɴ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n<blockquote>{ids}</blockquote></b>", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>⁉️ Nᴏ Aᴅᴍɪɴ Lɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)
  
    if len(admin_ids) >= 1:
        passed = ''
        for ad_id in admins:
            try:
                id = int(ad_id)
            except:
                passed += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{ad_id}</code></b></blockquote>\n"
                continue
                
            if id in admin_ids:
                await del_admin(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += f"<blockquote><b><code>{id}</code> ɴᴏᴛ ɪɴ ᴀᴅᴍɪɴ ʟɪsᴛ</b></blockquote>\n"
                
        await pro.edit(f"<b>⛔️ Pʀᴏᴠɪᴅᴇᴅ Aᴅᴍɪɴ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n\n{passed}</b>", reply_markup=reply_markup)
        
    else:
        await pro.edit("<b><blockquote>⁉️ Nᴏ Aᴅᴍɪɴ Lɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admin_list') & filters.private & filters.user(OWNER_ID))
async def get_admin_list(client:Client, message: Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    admin_ids = await get_all_admins()
    admin_list = "<b><blockquote>❌ Nᴏ Aᴅᴍɪɴ ɪᴅ Lɪsᴛ Fᴏᴜɴᴅ !</blockquote></b>"
    
    if admin_ids:
        admin_list = ""
        for id in admin_ids:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                user = await client.get_users(id)
                user_link = f"tg://openmessage?user_id={id}"
                first_name = user.first_name if user.first_name else "No first name !"
                    
                admin_list += f"<b><blockquote>NAME: <a href = {user_link}>{first_name}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n"
                
            except:
                admin_list += f"<b><blockquote>ɪᴅ: <code>{id}</code>\n<i>ᴜɴᴀʙʟᴇ ᴛᴏ ʟᴏᴀᴅ ᴏᴛʜᴇʀ ᴅᴇᴛᴀɪʟs..</i></blockquote></b>\n\n"
                
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(f"<b>🤖 𝗕𝗢𝗧 𝗔𝗗𝗠𝗜𝗡𝗦 𝗟𝗜𝗦𝗧 :</b>\n\n{admin_list}", reply_markup=reply_markup, disable_web_page_preview = True)


#Commands for banned user function............

@Bot.on_message(filters.command('add_banuser') & filters.private & filters.user(OWNER_ID))
async def add_banuser(client:Client, message:Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    check, autho_users = 0, []
    banuser_ids = await get_ban_users()
    autho_users = await get_all_admins(); autho_users.append(OWNER_ID)
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    
    if not banusers:
        return await pro.edit("<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ Bᴀɴɴᴇᴅ Usᴇʀ ɪᴅs\n<blockquote><u>EXAMPLE</u> :\n/add_banuser [user_id] :</b> ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅ ᴀᴛ ᴀ ᴛɪᴍᴇ.</blockquote>", reply_markup=reply_markup)

    banuser_list = ""
    for id in banusers:
        try:
            id = int(id)
        except:
            banuser_list += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></b></blockquote>\n"
            continue

        if id in autho_users:
            banuser_list += f"<blockquote><b>ɪᴅ: <code>{id}</code>, ᴄᴏᴜʟᴅ ʙᴇ ᴀᴅᴍɪɴ ᴏʀ ᴏᴡɴᴇʀ</b></blockquote>\n"
            continue
            
        if id in banuser_ids:
            banuser_list += f"<blockquote><b>ɪᴅ: <code>{id}</code>, ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ..</b></blockquote>\n"
            continue
            
        id = str(id)  
        if id.isdigit() and len(id) == 10:
            banuser_list += f"<b><blockquote>(ID: <code>{id}</code>)</blockquote></b>\n"
            check += 1
        else:
            banuser_list += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></b></blockquote>\n"
            continue            
    
    if check == len(banusers):
        for id in banusers:
            await add_ban_user(int(id))
        await pro.edit(f'<b>Nᴇᴡ ɪᴅs Aᴅᴅᴇᴅ ɪɴ Bᴀɴɴᴇᴅ Usᴇʀ Lɪsᴛ ✅</b>\n\n{banuser_list}', reply_markup=reply_markup)
        
    else:
        await pro.edit(f'<b>❌ Eʀʀᴏʀ oᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ Aᴅᴅɪɴɢ Bᴀɴɴᴇᴅ Usᴇʀs</b>\n\n{banuser_list.strip()}\n\n<b><i>Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ...</i></b>', reply_markup=reply_markup)
    #await update_fsub(1)


@Bot.on_message(filters.command('del_banuser') & filters.private & filters.user(OWNER_ID))
async def delete_banuser(client:Client, message:Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    banuser_ids = await get_ban_users()
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])

    if not banusers:
        return await pro.edit("<b>⁉️ Pʟᴇᴀsᴇ, Pʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ɪᴅs ᴏʀ ᴀʀɢᴜᴍᴇɴᴛs</b>\n<blockquote><b><u>EXAMPLES:</u>\n/del_banuser [user_ids] :</b> ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ sᴘᴇᴄɪғɪᴇᴅ ɪᴅs\n<code>/del_banuser all</code> : ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴜsᴇʀ ɪᴅs</blockquote>", reply_markup=reply_markup)

    if len(banusers) == 1 and banusers[0].lower() == "all":
        if banuser_ids:
            for id in banuser_ids:
                await del_ban_user(id)
            ids = "\n".join([f"<code>{user}</code> ✅" for user in banuser_ids])
            return await pro.edit(f"<b>⛔️ Aʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ Bᴀɴɴᴇᴅ Usᴇʀ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n<blockquote>{ids}</blockquote></b>", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>⁉️ Nᴏ Bᴀɴɴᴇᴅ Usᴇʀ ɪᴅ Lɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)
  
    if len(banuser_ids) >= 1:
        passed = ''
        for ban_id in banusers:
            try:
                id = int(ban_id)
            except:
                passed += f"<blockquote><b>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{ban_id}</code></b></blockquote>\n"
                continue
                
            if id in banuser_ids:
                await del_ban_user(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += f"<blockquote><b><code>{id}</code> ɴᴏᴛ ɪɴ ʙᴀɴɴᴇᴅ ʟɪsᴛ</b></blockquote>\n"
                
        await pro.edit(f"<b>⛔️ Pʀᴏᴠɪᴅᴇᴅ Bᴀɴɴᴇᴅ Usᴇʀ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :</u>\n\n{passed}</b>", reply_markup=reply_markup)
        
    else:
        await pro.edit("<b><blockquote>⁉️ Nᴏ Bᴀɴɴᴇᴅ Usᴇʀ ɪᴅ Lɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('banuser_list') & filters.private & filters.user(OWNER_ID))
async def get_banuser_list(client:Client, message: Message):        
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    
    banuser_ids = await get_ban_users()
    banuser_list = "<b><blockquote>❌ Nᴏ Bᴀɴɴᴇᴅ Usᴇʀ Lɪsᴛ Fᴏᴜɴᴅ !</blockquote></b>"
    
    if banuser_ids:
        banuser_list = ""
        for id in banuser_ids:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                user = await client.get_users(id)
                user_link = f"tg://openmessage?user_id={id}"
                first_name = user.first_name if user.first_name else "No first name !"
                    
                banuser_list += f"<b><blockquote>NAME: <a href = {user_link}>{first_name}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n"
                
            except:
                banuser_list += f"<b><blockquote>ɪᴅ: <code>{id}</code>\n<i>ᴜɴᴀʙʟᴇ ᴛᴏ ʟᴏᴀᴅ ᴏᴛʜᴇʀ ᴅᴇᴛᴀɪʟs..</i></blockquote></b>\n\n"
                
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(f"<b>🚫 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥 𝗟𝗜𝗦𝗧 :</b>\n\n{banuser_list}", reply_markup=reply_markup, disable_web_page_preview = True)


#=====================================================================================##
#.........Auto Delete Functions.......#
#=====================================================================================##
DEL_MSG = """<b>⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
<blockquote>Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ <a href="https://t.me/{username}">{time}</a>. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.</blockquote></b>"""

@Bot.on_message(filters.command('auto_del') & filters.private & ~banUser)
async def autoDelete_settings(client, message):
    await message.reply_chat_action(ChatAction.TYPING)
    try:
            timer = convert_time(await get_del_timer())
            if await get_auto_delete():
                autodel_mode = on_txt
                mode = 'Dɪsᴀʙʟᴇ Mᴏᴅᴇ ❌'
            else:
                autodel_mode = off_txt
                mode = 'Eɴᴀʙʟᴇ Mᴏᴅᴇ ✅'
            
            await message.reply_photo(
                photo = autodel_cmd_pic,
                caption = AUTODEL_CMD_TXT.format(autodel_mode=autodel_mode, timer=timer),
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton('◈ Sᴇᴛ Tɪᴍᴇʀ ⏱', callback_data='set_timer')],
                    [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='autodel_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                ]),
                # message_effect_id = 5104841245755180586 #🔥
            )
    except Exception as e:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
            await message.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote><b><i>Cᴏɴᴛᴀɴᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @mrxbotx</i></b>", reply_markup=reply_markup)
            

async def auto_del_notification(bot_username, msg, delay_time, transfer):
    # Create like/dislike buttons
    like_dislike_buttons = [
        [
            InlineKeyboardButton("👍 Lɪᴋᴇ", callback_data=f"like_{msg.id}"),
            InlineKeyboardButton("👎 Dɪsʟɪᴋᴇ", callback_data=f"dislike_{msg.id}")
        ]
    ]
    
    temp = await msg.reply_text(
        DEL_MSG.format(username=bot_username, time=convert_time(delay_time)), 
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(like_dislike_buttons)
    )

    await asyncio.sleep(delay_time)
    try:
        if transfer:
            try:
                name = "♻️ Cʟɪᴄᴋ Hᴇʀᴇ"
                link = f"https://t.me/{bot_username}?start={transfer}"
                button = [
                    [InlineKeyboardButton(text=name, url=link), InlineKeyboardButton(text="Cʟᴏsᴇ ✖️", callback_data="close")]
                ]

                await temp.edit_text(
                    text=f"<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑\n<blockquote>Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: [<a href={link}>{name}</a>] ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</blockquote></b>", 
                    reply_markup=InlineKeyboardMarkup(button), 
                    disable_web_page_preview=True
                )

            except Exception as e:
                await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")
                print(f"Error occured while editing the Delete message: {e}")
        else:
            await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")

    except Exception as e:
        print(f"Error occured while editing the Delete message: {e}")
        await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")

    try: 
        await msg.delete()
    except Exception as e: 
        print(f"Error occurred on auto_del_notification() : {e}")
 
async def delete_message(msg, delay_time):
    #AUTO_DEL = await get_auto_delete()
    #if AUTO_DEL: 
    await asyncio.sleep(delay_time)
    try: await msg.delete()
    except Exception as e: print(f"Error occurred on delete_message() : {e}")


#=====================================================================================##
#.........Extra Functions.......#
#=====================================================================================##


@Bot.on_message(filters.command('files') & filters.private & ~banUser)
async def files_commands(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
        
    try:
        protect_content = hide_caption = channel_button = off_txt
        pcd = hcd = cbd = '❌'
        if await get_protect_content():
            protect_content = on_txt
            pcd = '✅'
        if await get_hide_caption():
            hide_caption = on_txt
            hcd = '✅'
        if await get_channel_button():
            channel_button = on_txt
            cbd = '✅'
        name, link = await get_channel_button_link()
        
        await message.reply_photo(
            photo = files_cmd_pic,
            caption = FILES_CMD_TXT.format(
                protect_content = protect_content,
                hide_caption = hide_caption,
                channel_button = channel_button,
                name = name,
                link = link
            ),
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ: {pcd}', callback_data='pc'), InlineKeyboardButton(f'Hɪᴅᴇ Cᴀᴘᴛɪᴏɴ: {hcd}', callback_data='hc')],
                [InlineKeyboardButton(f'Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ: {cbd}', callback_data='cb'), InlineKeyboardButton(f'◈ Sᴇᴛ Bᴜᴛᴛᴏɴ ➪', callback_data='setcb')],
                [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='files_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
            ]),
            # message_effect_id = 5104841245755180586 #🔥
        )
    except Exception as e:
        # reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
        await message.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote><b><i>Cᴏɴᴛᴀɴᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ: @mrxbotx</i></b>")
   
