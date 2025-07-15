#telegram username: @mrxbotx

import random
from bot import Bot
from plugins.FORMATS import *
from plugins.FORMATS import CLEAR_USERS_TXT
from config import OWNER_ID, PICS
from pyrogram.enums import ParseMode
from plugins.advance_features import convert_time
from database.database import *
from pyrogram.types import Message,ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from pyrogram.enums import ChatAction
# Define these variables if not already defined
on_txt = "🟢 Eɴᴀʙʟᴇᴅ"
off_txt = "🔴 Dɪsᴀʙʟᴇᴅ"

    
async def fileSettings(getfunc, setfunc=None, delfunc=False) :
    btn_mode, txt_mode, pic_mode = '❌', off_txt, off_pic
    del_btn_mode = 'Eɴᴀʙʟᴇ Mᴏᴅᴇ ✅'
    try:
        if not setfunc:
            if await getfunc():
                txt_mode = on_txt    
                btn_mode = '✅'
                del_btn_mode = 'Dɪsᴀʙʟᴇ Mᴏᴅᴇ ❌'
        
            return txt_mode, (del_btn_mode if delfunc else btn_mode)
            
        else:
            if await getfunc():
                await setfunc(False)
            else:
                await setfunc(True)
                pic_mode, txt_mode = on_pic, on_txt
                btn_mode = '✅'
                del_btn_mode = 'Dɪsᴀʙʟᴇ Mᴏᴅᴇ ❌'
                
            return pic_mode, txt_mode, (del_btn_mode if delfunc else btn_mode)
            
    except Exception as e:
        print(f"Error occured at [fileSettings(getfunc, setfunc=None, delfunc=False)] : {e}")

def buttonStatus(pc_data: str, hc_data: str, cb_data: str) -> list:
    button = [
        [
            InlineKeyboardButton(f'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ: {pc_data}', callback_data='pc'),
            InlineKeyboardButton(f'Hɪᴅᴇ Cᴀᴘᴛɪᴏɴ: {hc_data}', callback_data='hc')
        ],
        [
            InlineKeyboardButton(f'Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ: {cb_data}', callback_data='cb'), 
            InlineKeyboardButton(f'◈ Sᴇᴛ Bᴜᴛᴛᴏɴ ➪', callback_data='setcb')
        ],
        [
            InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='files_cmd'), 
            InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')
        ],
    ]
    return button

#functin help to checking if a user is admin or owner before processing query....
async def authoUser(query, user_id, owner_only=False):
    if not owner_only:
        if not any([user_id == OWNER_ID, await admin_exist(user_id)]):
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Aᴅᴍɪɴ !", show_alert=True)
            return False
    else:
        if user_id != OWNER_ID:
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Oᴡɴᴇʀ !", show_alert=True)
            return False
        
    await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
    return True   

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data        
    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
            
    elif data == "about":
        user = await client.get_users(OWNER_ID)
        user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}" 
        ownername = f"<b><a href={user_link}>{user.first_name}</a></b>" if user.first_name else f"<a href={user_link}>no name !</a>"
        await query.edit_message_media(
            InputMediaPhoto("https://telegra.ph/file/ff8fbe7d67a3c7492c353.jpg", 
                            ABOUT_TXT.format(
                                botname = client.name,
                                ownername = ownername, 
                            )
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅️ Bᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
            ]),
        )
        
    elif data == "setting":
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), "<b>Pʟᴇᴀsᴇ wᴀɪᴛ !\n\n<i>🔄 Rᴇᴛʀɪᴇᴠɪɴɢ ᴀʟʟ Sᴇᴛᴛɪɴɢs...</i></b>"))
        try:
            total_fsub = len(await get_all_channels())
            total_admin = len(await get_all_admins())
            total_ban = len(await get_ban_users())
            autodel_mode = 'Eɴᴀʙʟᴇᴅ' if await get_auto_delete() else 'Dɪsᴀʙʟᴇᴅ'
            protect_content = 'Eɴᴀʙʟᴇᴅ' if await get_protect_content() else 'Dɪsᴀʙʟᴇᴅ'
            hide_caption = 'Eɴᴀʙʟᴇᴅ' if await get_hide_caption() else 'Dɪsᴀʙʟᴇᴅ'
            chnl_butn = 'Eɴᴀʙʟᴇᴅ' if await get_channel_button() else 'Dɪsᴀʙʟᴇᴅ'
            reqfsub = 'Eɴᴀʙʟᴇᴅ' if await get_request_forcesub() else 'Dɪsᴀʙʟᴇᴅ'
            free_mode = 'Eɴᴀʙʟᴇᴅ' if await get_free_mode() else 'Dɪsᴀʙʟᴇᴅ'
            
            await query.edit_message_media(
                InputMediaPhoto(random.choice(PICS),
                                SETTING_TXT.format(
                                    total_fsub = total_fsub,
                                    total_admin = total_admin,
                                    total_ban = total_ban,
                                    autodel_mode = autodel_mode,
                                    protect_content = protect_content,
                                    hide_caption = hide_caption,
                                    chnl_butn = chnl_butn,
                                    reqfsub=reqfsub,
                                    free_mode=free_mode,
                                )
                ),
                reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅️ Bᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                ]),
            )
        except Exception as e:
            print(f"! Error Occured on callback data = 'setting' : {e}")
        
    elif data == "start":
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), 
                            START_MSG.format(
                                first = query.from_user.first_name,
                                last = query.from_user.last_name,
                                username = None if not query.from_user.username else '@' + query.from_user.username,
                                mention = query.from_user.mention,
                                id = query.from_user.id
                            )
            ),
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('🤖 Aʙᴏᴜᴛ ᴍᴇ', callback_data='about'), InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='setting')]
            ]),
        )
        
    elif data == "files_cmd":
        if await authoUser(query, query.from_user.id):   
            try:
                protect_content, pcd = await fileSettings(get_protect_content)
                hide_caption, hcd = await fileSettings(get_hide_caption)
                channel_button, cbd = await fileSettings(get_channel_button)
                name, link = await get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(files_cmd_pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd)),
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'files_cmd' : {e}")
            
    elif data == "pc":
        if await authoUser(query, query.from_user.id):   
            try:
                pic, protect_content, pcd = await fileSettings(get_protect_content, set_protect_content)
                hide_caption, hcd = await fileSettings(get_hide_caption)   
                channel_button, cbd = await fileSettings(get_channel_button) 
                name, link = await get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'pc' : {e}")
            
    elif data == "hc":
        if await authoUser(query, query.from_user.id):     
            try:
                protect_content, pcd = await fileSettings(get_protect_content)
                pic, hide_caption, hcd = await fileSettings(get_hide_caption, set_hide_caption)   
                channel_button, cbd = await fileSettings(get_channel_button) 
                name, link = await get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'hc' : {e}")
            
    elif data == "cb":
        if await authoUser(query, query.from_user.id):   
            try:
                protect_content, pcd = await fileSettings(get_protect_content)
                hide_caption, hcd = await fileSettings(get_hide_caption)   
                pic, channel_button, cbd = await fileSettings(get_channel_button, set_channel_button) 
                name, link = await get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'cb' : {e}")
            
    elif data == "setcb":
        id = query.from_user.id
        if await authoUser(query, id):   
            try:
                button_name, button_link = await get_channel_button_link()
            
                button_preview = [[InlineKeyboardButton(text=button_name, url=button_link)]]  
                set_msg = await client.ask(chat_id = id, text=f'<b>Tᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴ, Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛs ᴡɪᴛʜɪɴ 1 ᴍɪɴᴜᴛᴇ.\nFᴏʀ ᴇxᴀᴍᴘʟᴇ:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Bᴇʟᴏᴡ ɪs ʙᴜᴛᴛᴏɴ Pʀᴇᴠɪᴇᴡ ⬇️</i></b>', timeout=60, reply_markup=InlineKeyboardMarkup(button_preview), disable_web_page_preview = True)
                button = set_msg.text.split(' - ')
                
                if len(button) != 2:
                    markup = [[InlineKeyboardButton(f'◈ Sᴇᴛ Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ ➪', callback_data='setcb')]]
                    return await set_msg.reply("<b>Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛs.\nFᴏʀ ᴇxᴀᴍᴘʟᴇ:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ..</i></b>", reply_markup=InlineKeyboardMarkup(markup), disable_web_page_preview = True)
                
                button_name = button[0].strip(); button_link = button[1].strip()
                button_preview = [[InlineKeyboardButton(text=button_name, url=button_link)]]
                
                await set_msg.reply("<b><i>Aᴅᴅᴇᴅ Sᴜᴄcᴇssғᴜʟʟʏ ✅</i>\n<blockquote>Sᴇᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴀs Pʀᴇᴠɪᴇᴡ ⬇️</blockquote></b>", reply_markup=InlineKeyboardMarkup(button_preview))
                await set_channel_button_link(button_name, button_link)
                return
            except Exception as e:
                try:
                    await set_msg.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")
                    print(f"! Error Occured on callback data = 'setcb' : {e}")
                except:
                    await client.send_message(id, text=f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote><i>Rᴇᴀsᴏɴ: 1 minute Time out ..</i></b></blockquote>", disable_notification=True)
                    print(f"! Error Occured on callback data = 'setcb' -> Rᴇᴀsᴏɴ: 1 minute Time out ..")

    elif data == 'autodel_cmd':
        if await authoUser(query, query.from_user.id, owner_only=True):            
            try:
                timer = convert_time(await get_del_timer())
                autodel_mode, mode = await fileSettings(get_auto_delete, delfunc=True)
                
                await query.edit_message_media(
                    InputMediaPhoto(autodel_cmd_pic,
                                    AUTODEL_CMD_TXT.format(
                                        autodel_mode = autodel_mode,
                                        timer = timer
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton('◈ Sᴇᴛ Tɪᴍᴇʀ ⏱', callback_data='set_timer')],
                        [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='autodel_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"! Error Occured on callback data = 'autodel_cmd' : {e}")
            
    elif data == 'chng_autodel':
        if await authoUser(query, query.from_user.id, owner_only=True):              
            try:
                timer = convert_time(await get_del_timer())
                pic, autodel_mode, mode = await fileSettings(get_auto_delete, set_auto_delete, delfunc=True)
            
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    AUTODEL_CMD_TXT.format(
                                        autodel_mode = autodel_mode,
                                        timer = timer
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton('◈ Sᴇᴛ Tɪᴍᴇʀ ⏱', callback_data='set_timer')],
                        [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='autodel_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"! Error Occured on callback data = 'chng_autodel' : {e}")

    elif data == 'set_timer':
        id = query.from_user.id
        if await authoUser(query, id, owner_only=True):  
            try:
                timer = convert_time(await get_del_timer())
                set_msg = await client.ask(chat_id = id, text=f'<b><blockquote>⏱ Cᴜʀʀᴇɴᴛ Tɪᴍᴇʀ: {timer}</blockquote>\n\nTᴏ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ, Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɪɴ sᴇᴄᴏɴᴅs ᴡɪᴛʜɪɴ 1 ᴍɪɴᴜᴛᴇ.\n<blockquote>Fᴏʀ ᴇxᴀᴍᴘʟᴇ: <code>300</code>, <code>600</code>, <code>900</code></b></blockquote>', timeout=60)
                del_timer = set_msg.text.split()
                
                if len(del_timer) == 1 and del_timer[0].isdigit():
                    DEL_TIMER = int(del_timer[0])
                    await set_del_timer(DEL_TIMER)
                    timer = convert_time(DEL_TIMER)
                    await set_msg.reply(f"<b><i>Aᴅᴅᴇᴅ Sᴜᴄcᴇssғᴜʟʟʏ ✅</i>\n<blockquote>⏱ Cᴜʀʀᴇɴᴛ Tɪᴍᴇʀ: {timer}</blockquote></b>")
                else:
                    markup = [[InlineKeyboardButton('◈ Sᴇᴛ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ⏱', callback_data='set_timer')]]
                    return await set_msg.reply("<b>Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɪɴ sᴇᴄᴏɴᴅs.\n<blockquote>Fᴏʀ ᴇxᴀᴍᴘʟᴇ: <code>300</code>, <code>600</code>, <code>900</code></blockquote>\n\n<i>Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ..</i></b>", reply_markup=InlineKeyboardMarkup(markup))

            except Exception as e:
                try:
                    await set_msg.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")
                    print(f"! Error Occured on callback data = 'set_timer' : {e}")
                except:
                    await client.send_message(id, text=f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote><i>Rᴇᴀsᴏɴ: 1 minute Time out ..</i></b></blockquote>", disable_notification=True)
                    print(f"! Error Occured on callback data = 'set_timer' -> Rᴇᴀsᴏɴ: 1 minute Time out ..")

    elif data == "more_settings":
        user_id = query.from_user.id
        if not await authoUser(query, user_id, owner_only=True):
            await query.answer("❌ You are not authorized to do this.", show_alert=True)
            return
        try:
            await query.message.edit_text(
                "<b>Pʟᴇᴀsᴇ wᴀɪᴛ !\n\n<i>🔄 Rᴇᴛʀɪᴇᴠɪɴɢ ᴀʟʟ Sᴇᴛᴛɪɴɢs...</i></b>"
            )
            REQFSUB_CHNLS = await db.get_reqChannel()
            if REQFSUB_CHNLS:
                LISTS = ""
                for CHNL in REQFSUB_CHNLS:
                    await query.message.reply_chat_action(ChatAction.TYPING)
                    try:
                        chat = await client.get_chat(CHNL)
                        channel_name = chat.title or "<i>Uɴᴀʙʟᴇ Lᴏᴀᴅ Nᴀᴍᴇ..</i>"
                    except Exception:
                        channel_name = "<i>Uɴᴀʙʟᴇ Lᴏᴀᴅ Nᴀᴍᴇ..</i>"
                    user = await db.get_reqSent_user(CHNL)
                    channel_users = len(user) if user else 0
                    link = await db.get_stored_reqLink(CHNL)
                    if link:
                        channel_name = f'<a href="{link}">{channel_name}</a>'
                    LISTS += f"NAME: {channel_name}\n(ID: <code>{CHNL}</code>)\nUSERS: {channel_users}\n\n"
            else:
                LISTS = "Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ Lɪsᴛ !?"
            
            buttons = [
                [InlineKeyboardButton("ᴄʟᴇᴀʀ ᴜsᴇʀs", callback_data="clear_users"),
                 InlineKeyboardButton("cʟᴇᴀʀ cʜᴀɴɴᴇʟs", callback_data="clear_chnls")],
                [InlineKeyboardButton("cʟᴇᴀʀ ʟɪɴᴋs", callback_data="clear_links")],
                [InlineKeyboardButton("♻️  Rᴇғʀᴇsʜ Sᴛᴀᴛᴜs  ♻️", callback_data="more_settings")],
                [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="req_fsub"),
                 InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
            ]
            await query.message.reply_chat_action(ChatAction.CANCEL)
            await query.message.edit_text(
                text=RFSUB_MS_TXT.format(reqfsub_list=LISTS.strip()),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            print(f"! Error in more_settings_handler: {e}")

    elif data == "clear_users":
        user_id = query.from_user.id
        if not await authoUser(query, user_id, owner_only=True):
            await query.answer("❌ Unauthorized", show_alert=True)
            return
        try:
            REQFSUB_CHNLS = await db.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer("Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ !?", show_alert=True)
            
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i + 2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNELS USER'])
            
            user_reply = await client.ask(
                user_id,
                text=CLEAR_USERS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    await db.clear_reqSent_user(int(user_reply.text))
                    return await user_reply.reply(
                        f"<b><blockquote>✅ Usᴇʀ Dᴀᴛᴀ Sᴜᴄᴄᴇssғᴜʟʟʏ Cʟᴇᴀʀᴇᴅ ғʀᴏᴍ Cʜᴀɴɴᴇʟ ɪᴅ: <code>{user_reply.text}</code></blockquote></b>",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            elif user_reply.text == 'DELETE ALL CHANNELS USER':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        await db.clear_reqSent_user(int(CHNL))
                    return await user_reply.reply(
                        "<b><blockquote>✅ Usᴇʀ Dᴀᴛᴀ Sᴜᴄᴄᴇssғᴜʟʟʏ Cʟᴇᴀʀᴇᴅ ғʀᴏᴍ Aʟʟ Cʜᴀɴɴᴇʟ ɪᴅs</blockquote></b>",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            else:
                return await user_reply.reply(
                    "<b><blockquote>INVALID SELECTIONS</blockquote></b>",
                    reply_markup=ReplyKeyboardRemove()
                )
        except Exception as e:
            print(f"! Error Occurred on callback data = 'clear_users' : {e}")

    elif data == "clear_chnls":
        user_id = query.from_user.id
        if not await authoUser(query, user_id, owner_only=True):
            await query.answer("❌ Unauthorized", show_alert=True)
            return
        try:
            REQFSUB_CHNLS = await db.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer("Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ !?", show_alert=True)
            
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i + 2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNEL IDS'])
            
            user_reply = await client.ask(
                user_id,
                text=CLEAR_CHNLS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    chnl_id = int(user_reply.text)
                    await db.del_reqChannel(chnl_id)
                    try:
                        await client.revoke_chat_invite_link(chnl_id, await db.get_stored_reqLink(chnl_id))
                    except Exception:
                        pass
                    await db.del_stored_reqLink(chnl_id)
                    return await user_reply.reply(
                        f"<b><blockquote><code>{user_reply.text}</code> Cʜᴀɴɴᴇʟ ɪᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ɪᴛs ᴅᴀᴛᴀ sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            elif user_reply.text == 'DELETE ALL CHANNEL IDS':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        chnl = int(CHNL)
                        await db.del_reqChannel(chnl)
                        try:
                            await client.revoke_chat_invite_link(chnl, await db.get_stored_reqLink(chnl))
                        except Exception:
                            pass
                        await db.del_stored_reqLink(chnl)
                    return await user_reply.reply(
                        "<b><blockquote>Aʟʟ Cʜᴀɴɴᴇʟ ɪᴅs ᴀʟᴏɴɢ ᴡɪᴛʜ ɪᴛs ᴅᴀᴛᴀ sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            else:
                return await user_reply.reply(
                    "<b><blockquote>INVALID SELECTIONS</blockquote></b>",
                    reply_markup=ReplyKeyboardRemove()
                )
        except Exception as e:
            print(f"! Error Occurred on callback data = 'clear_chnls' : {e}")

    elif data == "clear_links":
        user_id = query.from_user.id
        if not await authoUser(query, user_id, owner_only=True):
            await query.answer("❌ Unauthorized", show_alert=True)
            return
        try:
            REQFSUB_CHNLS = await db.get_reqLink_channels()
            if not REQFSUB_CHNLS:
                return await query.answer("Nᴏ Sᴛᴏʀᴇᴅ Rᴇǫᴜᴇsᴛ Lɪɴᴋ Aᴠᴀɪʟᴀʙʟᴇ !?", show_alert=True)
            
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i + 2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL REQUEST LINKS'])
            
            user_reply = await client.ask(
                user_id,
                text=CLEAR_LINKS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                channel_id = int(user_reply.text)
                try:
                    try:
                        await client.revoke_chat_invite_link(channel_id, await db.get_stored_reqLink(channel_id))
                    except Exception:
                        text = (
                            "<b>❌ Uɴᴀʙʟᴇ ᴛᴏ Rᴇᴠᴏᴋᴇ ʟɪɴᴋ !"
                            "<blockquote expandable>ɪᴅ: <code>{}</code></b>"
                            "<i>Eɪᴛʜᴇʀ ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏᴛ ɪɴ ᴀʙᴏᴠᴇ ᴄʜᴀɴɴᴇʟ Oʀ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘʀᴏᴘᴇʀ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs</i></blockquote>"
                        )
                        return await user_reply.reply(text=text.format(channel_id), reply_markup=ReplyKeyboardRemove())
                    await db.del_stored_reqLink(channel_id)
                    return await user_reply.reply(
                        f"<b><blockquote><code>{channel_id}</code> Cʜᴀɴɴᴇʟs Lɪɴᴋ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            elif user_reply.text == 'DELETE ALL REQUEST LINKS':
                try:
                    result = ""
                    for CHNL in REQFSUB_CHNLS:
                        channel_id = int(CHNL)
                        try:
                            await client.revoke_chat_invite_link(channel_id, await db.get_stored_reqLink(channel_id))
                        except Exception:
                            result += (
                                f"<blockquote expandable><b><code>{channel_id}</code> Uɴᴀʙʟᴇ ᴛᴏ Rᴇᴠᴏᴋᴇ ❌</b>\n"
                                "<i>Eɪᴛʜᴇʀ ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏᴛ ɪɴ ᴀʙᴏᴠᴇ ᴄʜᴀɴɴᴇʟ Oʀ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘʀᴏᴘᴇʀ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.</i></blockquote>\n"
                            )
                            continue
                        await db.del_stored_reqLink(channel_id)
                        result += f"<blockquote><b><code>{channel_id}</code> IDs Lɪɴᴋ Dᴇʟᴇᴛᴇᴅ ✅</b></blockquote>\n"
                    return await user_reply.reply(
                        f"<b>⁉️ Oᴘᴇʀᴀᴛɪᴏɴ Rᴇsᴜʟᴛ:</b>\n{result.strip()}",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(
                        f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>",
                        reply_markup=ReplyKeyboardRemove()
                    )
            else:
                return await user_reply.reply(
                    f"<b><blockquote>INVALID SELECTIONS</blockquote></b>",
                    reply_markup=ReplyKeyboardRemove()
                )
        except Exception as e:
            print(f"! Error Occurred on callback 'clear_links': {e}")


    elif data == "chng_req":
        await query.answer("♻️ Cʜᴀɴɢɪɴɢ Sᴇᴛᴛɪɴɢ....")
        try:
            current_setting = await db.get_request_forcesub()
            new_setting = not current_setting
            await db.set_request_forcesub(new_setting)
            
            on = off = ""
            if new_setting:
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
            print(f"! Error Occurred on callback data = 'chng_req' : {e}")

    elif data == "req_fsub":
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

    elif data == "buy_prem":
        """Dynamic premium purchase handler"""
        user_id = query.from_user.id
        first_name = query.from_user.first_name or "User"
        username = f"@{query.from_user.username}" if query.from_user.username else first_name
        user_mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
        
        await query.answer("♻️ Lᴏᴀᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs....")
        
        try:
            is_premium = await db.is_premium_user(user_id)
            
            if is_premium:
                premium_users = await db.get_premium_users()
                user_premium_data = next((user for user in premium_users if user['_id'] == user_id), None)
                
                if user_premium_data and user_premium_data.get("expiry_time"):
                    import time
                    from datetime import datetime, timezone
                    
                    current_time = time.time()
                    expiry_time = user_premium_data["expiry_time"]
                    remaining_seconds = expiry_time - current_time
                    
                    if remaining_seconds > 0:
                        days = int(remaining_seconds // 86400)
                        hours = int((remaining_seconds % 86400) // 3600)
                        time_left = f"{days}ᴅ {hours}ʜ" if days > 0 else f"{hours}ʜ"
                        
                        extend_caption = (
                            f"💎 <b>ʜᴇʏ {user_mention}..!</b>\n\n"
                            f"✅ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ!\n"
                            f"⏰ ᴇxᴘɪʀᴇs ɪɴ: {time_left}\n\n"
                            f"🔄 ᴡᴀɴᴛ ᴛᴏ ᴇxᴛᴇɴᴅ? ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ"
                        )
                        
                        extend_buttons = [
                            [InlineKeyboardButton("👤 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"tg://user?id={OWNER_ID}")],
                            [InlineKeyboardButton("📊 ᴍʏ ᴘʟᴀɴ", callback_data="my_plan"),
                             InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close")]
                        ]
                        
                        try:
                            await query.message.edit_text(
                                text=extend_caption,
                                reply_markup=InlineKeyboardMarkup(extend_buttons)
                            )
                        except Exception:
                            await client.send_message(
                                chat_id=query.message.chat.id,
                                text=extend_caption,
                                reply_markup=InlineKeyboardMarkup(extend_buttons)
                            )
                        return
        except Exception as e:
            print(f"Error checking premium status: {e}")
        
        # Dynamic plan buttons (you'll need to define these prices in your config)
        try:
            # Import prices from config if available, otherwise use defaults
            from config import PRICE1, PRICE2, PRICE3, PRICE4, PRICE5, UPI_ID, QR_PIC
        except ImportError:
            # Default prices if not in config
            PRICE1, PRICE2, PRICE3, PRICE4, PRICE5 = "₹10", "₹25", "₹50", "₹90", "₹150"
            UPI_ID = "nyxking@ybl"
            QR_PIC = "https://ibb.co/mVDMPLwW"
        
        plans = [
            {"id": "plan_1", "price": PRICE1, "duration": "7 ᴅᴀʏs", "emoji": "⚡"},
            {"id": "plan_2", "price": PRICE2, "duration": "1 ᴍᴏɴᴛʜ", "emoji": "🔥"},
            {"id": "plan_3", "price": PRICE3, "duration": "3 ᴍᴏɴᴛʜs", "emoji": "💎"},
            {"id": "plan_4", "price": PRICE4, "duration": "6 ᴍᴏɴᴛʜs", "emoji": "👑"},
            {"id": "plan_5", "price": PRICE5, "duration": "1 ʏᴇᴀʀ", "emoji": "🌟"}
        ]
        
        # Create dynamic plan buttons
        plan_buttons = []
        for i in range(0, len(plans), 2):
            row = []
            for j in range(2):
                if i + j < len(plans):
                    plan = plans[i + j]
                    row.append(InlineKeyboardButton(
                        f"• {plan['duration']} •",
                        callback_data=plan['id']
                    ))
            plan_buttons.append(row)
        
        # Add action buttons
        plan_buttons.extend([
            [InlineKeyboardButton("📊 ᴍʏ ᴘʟᴀɴ", callback_data="my_plan"),
             InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close")]
        ])
        
        caption = (
            f"👋 <b>ᴡᴇʟᴄᴏᴍᴇ {user_mention}..!</b>\n\n"
            f"💎 <b>ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ:</b>\n\n"
            f"🎯 <b>ᴀʟʟ ᴘʟᴀɴs ɪɴᴄʟᴜᴅᴇ:</b>\n"
            f"├ ⚡ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅs\n"
            f"├ 🚫 ɴᴏ ᴀᴅs ᴏʀ ᴡᴀɪᴛɪɴɢ\n"
            f"├ ⚡ ғᴀsᴛᴇʀ ᴘʀᴏᴄᴇssɪɴɢ\n\n"
            f"💳 <b>ᴜᴘɪ:</b> <code>{UPI_ID}</code>\n"
            f"📷 <b>Qʀ Cᴏᴅᴇ:</b> <a href='{QR_PIC}'>Cʟɪᴄᴋ ᴛᴏ Vɪᴇᴡ</a>\n\n"
            f"📱 sᴄᴀɴ ǫʀ ᴄᴏᴅᴇ ᴀʙᴏᴠᴇ ᴏʀ ᴄʜᴏᴏsᴇ ᴘʟᴀɴ ʙᴇʟᴏᴡ"
        )
        
        try:
            # Check if QR_PIC exists and is valid
            if QR_PIC and QR_PIC.strip():
                try:
                    # Try to edit with photo if QR code exists
                    await query.message.edit_media(
                        media=InputMediaPhoto(
                            media=QR_PIC,
                            caption=caption
                        ),
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
                except Exception as edit_error:
                    print(f"Failed to edit message with QR photo: {edit_error}")
                    # Fallback: send new photo message
                    await client.send_photo(
                        chat_id=query.message.chat.id,
                        photo=QR_PIC,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
            else:
                # No QR code pic available, send/edit as text message
                try:
                    await query.message.edit_text(
                        text=caption,
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
                except Exception as edit_error:
                    print(f"Failed to edit message as text: {edit_error}")
                    # Fallback: send new text message
                    await client.send_message(
                        chat_id=query.message.chat.id,
                        text=caption,
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
            
            # Log the premium inquiry for analytics
            print(f"Premium inquiry from user {user_id} ({username})")
            
        except Exception as e:
            print(f"Error sending premium purchase message: {e}")
            
            # Final fallback: send simple text message
            try:
                await client.send_message(
                    chat_id=query.message.chat.id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(plan_buttons)
                )
            except Exception as e2:
                print(f"All fallback methods failed: {e2}")
                await query.answer("❌ Eʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ!", show_alert=True)

    elif data.startswith("plan_"):
        """Handle individual plan details"""
        plan_id = query.data
        user_id = query.from_user.id
        username = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name or "ᴜsᴇʀ"
        
        await query.answer("♻️ Lᴏᴀᴅɪɴɢ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs....")
        
        try:
            # Import prices from config
            from config import PRICE1, PRICE2, PRICE3, PRICE4, PRICE5, UPI_ID
        except ImportError:
            # Default prices if not in config
            PRICE1, PRICE2, PRICE3, PRICE4, PRICE5 = "₹10", "₹25", "₹50", "₹90", "₹150"
            UPI_ID = "nyxking@ybl"
        
        # Plan details mapping
        plan_details = {
            "plan_1": {
                "price": PRICE1, "duration": "7 ᴅᴀʏs", "emoji": "⚡",
                "benefits": ["ᴘᴇʀғᴇᴄᴛ ғᴏʀ ᴛʀɪᴀʟ", "ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅs", "ɴᴏ ᴀᴅs"]
            },
            "plan_2": {
                "price": PRICE2, "duration": "1 ᴍᴏɴᴛʜ", "emoji": "🔥",
                "benefits": ["ᴍᴏsᴛ ᴘᴏᴘᴜʟᴀʀ", "ʙᴇsᴛ ᴠᴀʟᴜᴇ", "ғᴜʟʟ ғᴇᴀᴛᴜʀᴇs", "ᴘʀɪᴏʀɪᴛʏ sᴜᴘᴘᴏʀᴛ"]
            },
            "plan_3": {
                "price": PRICE3, "duration": "3 ᴍᴏɴᴛʜs", "emoji": "💎",
                "benefits": ["25% sᴀᴠɪɴɢs", "ᴇxᴛᴇɴᴅᴇᴅ ᴀᴄᴄᴇss", "ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs"]
            },
            "plan_4": {
                "price": PRICE4, "duration": "6 ᴍᴏɴᴛʜs", "emoji": "👑",
                "benefits": ["40% sᴀᴠɪɴɢs", "ʟᴏɴɢ ᴛᴇʀᴍ ᴠᴀʟᴜᴇ", "ᴘʀɪᴏʀɪᴛʏ sᴜᴘᴘᴏʀᴛ"]
            },
            "plan_5": {
                "price": PRICE5, "duration": "1 ʏᴇᴀʀ", "emoji": "🌟",
                "benefits": ["ᴍᴀxɪᴍᴜᴍ sᴀᴠɪɴɢs", "ʙᴇsᴛ ᴅᴇᴀʟ", "ᴠɪᴘ sᴜᴘᴘᴏʀᴛ", "ᴀʟʟ ғᴜᴛᴜʀᴇ ᴜᴘᴅᴀᴛᴇs"]
            }
        }
        
        if plan_id not in plan_details:
            await query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ", show_alert=True)
            return
        
        plan = plan_details[plan_id]
        benefits_text = "\n".join([f"├ ✅ {benefit}" for benefit in plan["benefits"]])
        
        plan_text = (
            f"{plan['emoji']} <b>{plan['price']} - {plan['duration']}</b>\n\n"
            f"🎯 <b>ᴛʜɪs ᴘʟᴀɴ ɪɴᴄʟᴜᴅᴇs:</b>\n"
            f"{benefits_text}\n"
            f"└ ⚡ ғᴀsᴛ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ\n\n"
            f"💳 <b>ᴘᴀʏᴍᴇɴᴛ sᴛᴇᴘs:</b>\n"
            f"1️⃣ ᴘᴀʏ <b>{plan['price']}</b> ᴛᴏ ᴜᴘɪ: <code>{UPI_ID}</code>\n"
            f"2️⃣ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴛᴏ ᴀᴅᴍɪɴ\n"
            f"3️⃣ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ! ⚡"
        )
        
        plan_buttons = [
            [InlineKeyboardButton("✅ ᴠᴇʀɪғʏ ᴘᴀʏᴍᴇɴᴛ", callback_data=f"verify_payment_{plan_id}")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴘʟᴀɴs", callback_data="buy_prem"),
             InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close")]
        ]
        
        try:
            # Try to edit as caption first (if it's a photo message)
            try:
                await query.message.edit_caption(
                    caption=plan_text,
                    reply_markup=InlineKeyboardMarkup(plan_buttons)
                )
            except Exception:
                # If caption edit fails, try text edit
                try:
                    await query.message.edit_text(
                        text=plan_text,
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
                except Exception:
                    # If both fail, send new message
                    await client.send_message(
                        chat_id=query.message.chat.id,
                        text=plan_text,
                        reply_markup=InlineKeyboardMarkup(plan_buttons)
                    )
            
            print(f"Plan {plan_id} viewed by user {user_id}")
            
        except Exception as e:
            print(f"Error showing plan details: {e}")
            await query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs", show_alert=True)

    elif data.startswith("verify_payment_"):
        """Show payment verification error with admin contact"""
        user_id = query.from_user.id
        plan_id = query.data.replace("verify_payment_", "")
        
        await query.answer("❌ Server error payment failed to verify contact admin", show_alert=True)
        
        # Show error message with admin contact button
        error_text = (
            f"❌ <b>Server Error</b>\n\n"
            f"Payment verification failed due to server error.\n\n"
            f"Please contact admin for manual verification."
        )
        
        error_buttons = [
            [InlineKeyboardButton("👤 Contact Admin", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("🔙 Back to Plan", callback_data=plan_id),
             InlineKeyboardButton("🔒 Close", callback_data="close")]
        ]
        
        try:
            await query.message.edit_caption(
                caption=error_text,
                reply_markup=InlineKeyboardMarkup(error_buttons)
            )
        except Exception:
            await query.message.edit_text(
                text=error_text,
                reply_markup=InlineKeyboardMarkup(error_buttons)
            )

    elif data == "my_plan":
        """Show user's current premium plan status"""
        user_id = query.from_user.id
        await query.answer("📊 ʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ᴘʟᴀɴ...", show_alert=False)
        
        try:
            # Check if user has premium
            premium_info = await get_premium_user_info(user_id)
            
            if premium_info:
                from datetime import datetime
                import pytz
                
                ist = pytz.timezone("Asia/Kolkata")
                
                # Calculate expiry date
                expiry_time = datetime.fromtimestamp(premium_info["expiry_time"], ist)
                expiry_date = expiry_time.strftime('%d %b %Y, %I:%M %p')
                
                # Calculate days remaining
                current_time = time.time()
                days_remaining = max(0, int((premium_info["expiry_time"] - current_time) / (24 * 60 * 60)))
                
                # Calculate added date
                if premium_info.get("added_time"):
                    added_time = datetime.fromtimestamp(premium_info["added_time"], ist)
                    added_date = added_time.strftime('%d %b %Y, %I:%M %p')
                else:
                    added_date = "ᴜɴᴋɴᴏᴡɴ"
                
                plan_text = (
                    f"💎 <b>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ</b>\n\n"
                    f"✅ <b>sᴛᴀᴛᴜs:</b> ᴀᴄᴛɪᴠᴇ\n"
                    f"📅 <b>ᴇxᴘɪʀᴇs ᴏɴ:</b> {expiry_date}\n"
                    f"⏰ <b>ᴅᴀʏs ʟᴇғᴛ:</b> {days_remaining} ᴅᴀʏs\n"
                    f"🗓 <b>ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴏɴ:</b> {added_date}\n\n"
                    f"🚀 <b>ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇғɪᴛs:</b>\n"
                    f"├ ⚡ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅ\n"
                    f"├ 🚫 ɴᴏ ᴀᴅs\n"
                    f"├ 🔓 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss\n"
                    f"└ 🎯 ᴘʀɪᴏʀɪᴛʏ sᴜᴘᴘᴏʀᴛ\n\n"
                    f"💖 <i>ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ sᴜᴘᴘᴏʀᴛɪɴɢ ᴜs!</i>"
                )
                
                plan_buttons = [
                    [InlineKeyboardButton("🔄 ᴇxᴛᴇɴᴅ ᴘʟᴀɴ", callback_data="buy_prem")],
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start"),
                     InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close")]
                ]
                
            else:
                plan_text = (
                    f"❌ <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ</b>\n\n"
                    f"🔒 <b>ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs:</b> ғʀᴇᴇ ᴜsᴇʀ\n\n"
                    f"💡 <b>ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ:</b>\n"
                    f"├ ⚡ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅ\n"
                    f"├ 🚫 ɴᴏ ᴀᴅs\n"
                    f"├ 🔓 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss\n"
                    f"└ 🎯 ᴘʀɪᴏʀɪᴛʏ sᴜᴘᴘᴏʀᴛ\n\n"
                    f"🎯 <i>ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ɴᴏᴡ ᴀɴᴅ ᴇɴᴊᴏʏ ғᴜʟʟ sᴘᴇᴇᴅ!</i>"
                )
                
                plan_buttons = [
                    [InlineKeyboardButton("💎 ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ", callback_data="buy_prem")],
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start"),
                     InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close")]
                ]
            
            try:
                await query.message.edit_caption(
                    caption=plan_text,
                    reply_markup=InlineKeyboardMarkup(plan_buttons)
                )
            except Exception:
                await query.message.edit_text(
                    text=plan_text,
                    reply_markup=InlineKeyboardMarkup(plan_buttons)
                )
                
        except Exception as e:
            print(f"Error in my_plan handler: {e}")
            await query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʟᴀɴ ɪɴғᴏ", show_alert=True)

    elif data == "refresh_token_settings":
        """Refresh token settings display"""
        if await authoUser(query, query.from_user.id, owner_only=True):
            try:
                await query.message.edit_text("🔄 <b>ʀᴇᴛʀɪᴇᴠɪɴɢ sᴇᴛᴛɪɴɢs...</b>\n\n<i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>")
                
                # Small delay for better UX
                import asyncio
                await asyncio.sleep(1)
                
                # Get current settings
                from database.database import get_token_settings
                from helper_func import get_exp_time
                
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
                    [InlineKeyboardButton("• sᴇᴛ ᴜʀʟ •", callback_data="set_token_url"),
                     InlineKeyboardButton("• sᴇᴛ ᴋᴇʏ •", callback_data="set_token_key")],
                    [InlineKeyboardButton("• sᴇᴛ ᴇxᴘɪʀᴇ •", callback_data="set_token_expire")],
                    [InlineKeyboardButton("• ʀᴇғʀᴇsʜ •", callback_data="refresh_token_settings")],
                    [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
                ]
                
                await query.message.edit_text(
                    text=token_text,
                    reply_markup=InlineKeyboardMarkup(token_buttons),
                    parse_mode=ParseMode.HTML
                )
                
            except Exception as e:
                print(f"Error refreshing token settings: {e}")
                await query.answer("❌ ᴇʀʀᴏʀ ʀᴇғʀᴇsʜɪɴɢ sᴇᴛᴛɪɴɢs", show_alert=True)

    elif data == "set_token_url":
        """Set shortlink URL"""
        user_id = query.from_user.id
        if await authoUser(query, user_id, owner_only=True):
            try:
                from database.database import get_token_settings
                current_settings = await get_token_settings()
                current_url = current_settings.get('shortlink_url', '') or "ɴᴏᴛ sᴇᴛ"
                
                set_msg = await client.ask(
                    chat_id=user_id,
                    text=(
                        f"🔗 <b>sᴇᴛ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ</b>\n\n"
                        f"📋 <b>ᴄᴜʀʀᴇɴᴛ:</b> <code>{current_url}</code>\n"
                        f"💡 <b>ɴᴇᴡ ᴜʀʟ ᴇxᴀᴍᴘʟᴇ:</b> <code>vplink.in</code>\n"
                        f"⏰ <i>ᴛɪᴍᴇᴏᴜᴛ: 60 sᴇᴄᴏɴᴅs</i>"
                    ),
                    timeout=60,
                    parse_mode=ParseMode.HTML
                )
                
                new_url = set_msg.text.strip()
                
                if not new_url or len(new_url) < 3:
                    return await set_msg.reply(
                        "❌ <b>ɪɴᴠᴀʟɪᴅ ᴜʀʟ</b>\n\n"
                        "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ᴛʀʏ ᴀɢᴀɪɴ •", callback_data="set_token_url")]
                        ])
                    )
                
                # Remove protocol if present
                new_url = new_url.replace('https://', '').replace('http://', '')
                
                from database.database import set_shortlink_url
                success = await set_shortlink_url(new_url)
                
                if success:
                    await set_msg.reply(
                        f"✅ <b>ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                        f"🔗 <b>ɴᴇᴡ ᴜʀʟ:</b>\n"
                        f"<blockquote><code>{new_url}</code></blockquote>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs •", callback_data="refresh_token_settings")]
                        ])
                    )
                else:
                    await set_msg.reply("❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴜʀʟ</b>")
                
            except Exception as e:
                try:
                    await set_msg.reply(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
                except:
                    await client.send_message(user_id, "⏰ <b>ᴛɪᴍᴇᴏᴜᴛ!</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

    elif data == "set_token_key":
        """Set shortlink API key"""
        user_id = query.from_user.id
        if await authoUser(query, user_id, owner_only=True):
            try:
                from database.database import get_token_settings
                current_settings = await get_token_settings()
                current_key = current_settings.get('shortlink_key', '') or "ɴᴏᴛ sᴇᴛ"
                
                # Mask current key
                if current_key != "ɴᴏᴛ sᴇᴛ" and len(current_key) > 8:
                    masked_key = current_key[:4] + "*" * (len(current_key) - 8) + current_key[-4:]
                else:
                    masked_key = current_key
                
                set_msg = await client.ask(
                    chat_id=user_id,
                    text=(
                        f"🔑 <b>sᴇᴛ ᴀᴘɪ ᴋᴇʏ</b>\n"
                        f"📋 <b>ᴄᴜʀʀᴇɴᴛ:</b> <code>{masked_key}</code>\n"
                        f"💡 <b>ɴᴇᴡ ᴋᴇʏ ᴇxᴀᴍᴘʟᴇ:</b> <code>8fa658d2ae...</code>\n"
                        f"⚠️ <i>ᴋᴇᴇᴘ ɪᴛ sᴀғᴇ • ᴛɪᴍᴇᴏᴜᴛ: 60s</i>"
                    ),
                    timeout=60,
                    parse_mode=ParseMode.HTML
                )
                
                new_key = set_msg.text.strip()
                
                if not new_key or len(new_key) < 10:
                    return await set_msg.reply(
                        "❌ <b>ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ</b>\n\n"
                        "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ (ᴀᴛ ʟᴇᴀsᴛ 10 ᴄʜᴀʀᴀᴄᴛᴇʀs).",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ᴛʀʏ ᴀɢᴀɪɴ •", callback_data="set_token_key")]
                        ])
                    )
                
                from database.database import set_shortlink_key
                success = await set_shortlink_key(new_key)
                
                if success:
                    # Mask new key for display
                    display_key = new_key[:4] + "*" * (len(new_key) - 8) + new_key[-4:]
                    
                    await set_msg.reply(
                        f"✅ <b>ᴀᴘɪ ᴋᴇʏ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                        f"🔑 <b>ɴᴇᴡ ᴋᴇʏ:</b>\n"
                        f"<blockquote><code>{display_key}</code></blockquote>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs •", callback_data="refresh_token_settings")]
                        ])
                    )
                else:
                    await set_msg.reply("❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴀᴘɪ ᴋᴇʏ</b>")
                
            except Exception as e:
                try:
                    await set_msg.reply(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
                except:
                    await client.send_message(user_id, "⏰ <b>ᴛɪᴍᴇᴏᴜᴛ!</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

    elif data == "set_token_expire":
        """Set verification expiry time"""
        user_id = query.from_user.id
        if await authoUser(query, user_id, owner_only=True):
            try:
                from database.database import get_token_settings
                from helper_func import get_exp_time
                
                current_settings = await get_token_settings()
                current_expire = current_settings.get('verify_expire', 86400)
                current_expire_text = get_exp_time(current_expire)
                
                set_msg = await client.ask(
                    chat_id=user_id,
                    text=(
                        f"⏰ <b>sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴇxᴘɪʀʏ</b>\n"
                        f"📋 <b>ᴄᴜʀʀᴇɴᴛ ᴇxᴘɪʀʏ:</b>\n"
                        f"📋 <b>ᴄᴜʀʀᴇɴᴛ:</b> {current_expire_text}\n"
                        f"💡 <b>ɴᴇᴡ ᴛɪᴍᴇ (ɪɴ sᴇᴄᴏɴᴅs):</b>\n"
                        f"<code>3600</code> = 1 ʜ\n"
                        f"<code>86400</code> = 24ʜ\n"
                        f"<code>604800</code> = 7ᴅ\n"
                        f"⏰ <i>ᴛɪᴍᴇᴏᴜᴛ: 60s</i>"
                    ),
                    timeout=60,
                    parse_mode=ParseMode.HTML
                )
                
                try:
                    new_expire = int(set_msg.text.strip())
                except ValueError:
                    return await set_msg.reply(
                        "❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ</b>\n\n"
                        "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɪɴ sᴇᴄᴏɴᴅs.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ᴛʀʏ ᴀɢᴀɪɴ •", callback_data="set_token_expire")]
                        ])
                    )
                
                if new_expire < 60 or new_expire > 2592000:  # 1 minute to 30 days
                    return await set_msg.reply(
                        "❌ <b>ɪɴᴠᴀʟɪᴅ ʀᴀɴɢᴇ</b>\n\n"
                        "ᴇxᴘɪʀʏ ᴛɪᴍᴇ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 60 sᴇᴄᴏɴᴅs (1 ᴍɪɴ) ᴀɴᴅ 2592000 sᴇᴄᴏɴᴅs (30 ᴅᴀʏs).",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ᴛʀʏ ᴀɢᴀɪɴ •", callback_data="set_token_expire")]
                        ])
                    )
                
                from database.database import set_verify_expire
                success = await set_verify_expire(new_expire)
                
                if success:
                    new_expire_text = get_exp_time(new_expire)
                    await set_msg.reply(
                        f"✅ <b>ᴇxᴘɪʀʏ ᴛɪᴍᴇ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                        f"⏰ <b>ɴᴇᴡ ᴇxᴘɪʀʏ:</b>\n"
                        f"<blockquote>{new_expire_text}</blockquote>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs •", callback_data="refresh_token_settings")]
                        ])
                    )
                else:
                    await set_msg.reply("❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴇxᴘɪʀʏ ᴛɪᴍᴇ</b>")
                
            except Exception as e:
                try:
                    await set_msg.reply(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
                except:
                    await client.send_message(user_id, "⏰ <b>ᴛɪᴍᴇᴏᴜᴛ!</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

    elif data == "new_verify_link":
        """Generate new verification link for user"""
        user_id = query.from_user.id
        await query.answer("🔄 ɢᴇɴᴇʀᴀᴛɪɴɢ ɴᴇᴡ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ...", show_alert=False)
        
        try:
            from helper_func import create_verification_link, get_exp_time
            from database.database import get_token_settings
            
            # Get bot username
            bot_username = client.me.username
            base_url = f"https://t.me/{bot_username}"
            
            # Get token settings for expiry time
            token_settings = await get_token_settings()
            verify_expire = token_settings.get('verify_expire', 86400)
            expire_text = get_exp_time(verify_expire)
            
            # Create verification link
            verify_link, verify_token = await create_verification_link(user_id, base_url)
            
            if verify_link:
                link_text = (
                    f"🔗 <b>ɴᴇᴡ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n"
                    f"👋 ʜɪ {query.from_user.first_name}, ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ғʀᴇᴇ <b>{expire_text}</b> ᴀᴄᴄᴇss.\n\n"
                    f"✅ <b>ᴄʟɪᴄᴋ ᴛᴏ ᴠᴇʀɪғʏ & ɢᴇᴛ ᴀᴄᴄᴇss:</b>\n<code>{verify_link}</code>\n\n"
                    f"📋 <b>ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:</b>\n"
                    f"1. ᴘʀᴇss <b>ᴠᴇʀɪғʏ ɴᴏᴡ</b>\n"
                    f"2. ᴄᴏᴍᴘʟᴇᴛᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ\n"
                    f"3. ᴇɴᴊᴏʏ ᴀᴄᴄᴇss ғᴏʀ <b>{expire_text}</b>\n\n"
                    f"⏰ <i>ʟɪɴᴋ ᴇxᴘɪʀᴇs ɪɴ {expire_text}</i>\n"
                    f"💡 <i>ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss</i>"
                )
                
                link_buttons = [
                    [InlineKeyboardButton("• ᴠᴇʀɪғʏ ɴᴏᴡ •", url=verify_link),
                    InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")],
                    [InlineKeyboardButton("• ɢᴇɴᴇʀᴀᴛᴇ ɴᴇᴡ ʟɪɴᴋ •", callback_data="new_verify_link"),
                    InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
                ]
            else:
                link_text = (
                    f"❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ</b>\n\n"
                    f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ʀɪɢʜᴛ ɴᴏᴡ.\n\n"
                    f"💡 <b>ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ ᴏᴘᴛɪᴏɴs:</b>\n"
                    f"• ᴛʀʏ ᴀɢᴀɪɴ ɪɴ ᴀ ғᴇᴡ ᴍɪɴᴜᴛᴇs\n"
                    f"• ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss\n"
                    f"• ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪғ ɪssᴜᴇ ᴘᴇʀsɪsᴛs"
                )
                
                link_buttons = [
                    [InlineKeyboardButton("• ᴛʀʏ ᴀɢᴀɪɴ •", callback_data="new_verify_link")],
                    [InlineKeyboardButton("• ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")],
                    [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]
                ]
            
            try:
                await query.message.edit_text(
                    text=link_text,
                    reply_markup=InlineKeyboardMarkup(link_buttons),
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                await query.message.edit_caption(
                    caption=link_text,
                    reply_markup=InlineKeyboardMarkup(link_buttons),
                    parse_mode=ParseMode.HTML
                )
                
        except Exception as e:
            print(f"Error generating new verify link: {e}")
            await query.answer("❌ ᴇʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ. ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)

    elif data.startswith("like_") or data.startswith("dislike_"):
        """Handle like/dislike reactions"""
        user_id = query.from_user.id
        
        # Extract message ID and reaction type
        if data.startswith("like_"):
            message_id = int(data.replace("like_", ""))
            reaction_type = "like"
            reaction_emoji = "❤️"
        else:
            message_id = int(data.replace("dislike_", ""))
            reaction_type = "dislike"
            reaction_emoji = "💔"
        
        try:
            from database.database import add_reaction, get_message_stats, get_user_reaction
            
            # Check if user already reacted
            current_reaction = await get_user_reaction(message_id, user_id)
            
            if current_reaction == reaction_type:
                await query.answer(f"ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ {reaction_type}ᴅ ᴛʜɪs!", show_alert=True)
                return
            
            # Add/update reaction
            success = await add_reaction(message_id, user_id, reaction_type)
            
            if success:
                # Get updated stats
                likes, dislikes = await get_message_stats(message_id)

                is_admin = user_id == OWNER_ID or await admin_exist(user_id)

                if is_admin:
                    updated_buttons = [
                        [
                            InlineKeyboardButton(f"❤️ {likes}", callback_data=f"like_{message_id}"),
                            InlineKeyboardButton(f"💔 {dislikes}", callback_data=f"dislike_{message_id}"),
                            InlineKeyboardButton("📊 Sᴛᴀᴛs", callback_data=f"stats_{message_id}")
                        ]
                    ]
                else:
                    updated_buttons = [
                        [
                            InlineKeyboardButton(f"❤️  {likes}", callback_data=f"like_{message_id}"),
                            InlineKeyboardButton(f"💔 {dislikes}", callback_data=f"dislike_{message_id}")
                    ]
                ]
                
                try:
                    await query.edit_message_reply_markup(
                        reply_markup=InlineKeyboardMarkup(updated_buttons)
                    )
                    await query.answer(f"{reaction_emoji} ʀᴇᴀᴄᴛɪᴏɴ ᴀᴅᴅᴇᴅ!")
                except Exception as e:
                    await query.answer(f"{reaction_emoji} ʀᴇᴀᴄᴛɪᴏɴ ᴀᴅᴅᴇᴅ!")
            else:
                await query.answer("❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ʀᴇᴀᴄᴛɪᴏɴ", show_alert=True)
                
        except Exception as e:
            print(f"Error handling reaction: {e}")
            await query.answer("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ʀᴇᴀᴄᴛɪᴏɴ", show_alert=True)

    elif data.startswith("stats_"):
        """Show detailed stats for message reactions"""
        message_id = int(data.replace("stats_", ""))
        
        try:
            from database.database import get_message_stats
            likes, dislikes = await get_message_stats(message_id)
            
            total_reactions = likes + dislikes
            like_percentage = (likes / total_reactions * 100) if total_reactions > 0 else 0
            dislike_percentage = (dislikes / total_reactions * 100) if total_reactions > 0 else 0
            
            stats_text = (
                f"📊 ᴍᴇssᴀɢᴇ ʀᴇᴀᴄᴛɪᴏɴ sᴛᴀᴛs\n\n"
                f"👍 ʟɪᴋᴇs:  {likes} ({like_percentage:.1f}%)\n"
                f"👎 ᴅɪsʟɪᴋᴇs:  {dislikes} ({dislike_percentage:.1f}%)\n"
                f"📈 ᴛᴏᴛᴀʟ: {total_reactions} ʀᴇᴀᴄᴛɪᴏɴs\n\n"
                f"{'🔥 ᴘᴏsɪᴛɪᴠᴇ ʀᴇsᴘᴏɴsᴇ!' if likes > dislikes else '😐 ᴍɪxᴇᴅ ʀᴇsᴘᴏɴsᴇ' if likes == dislikes else '👎 ɴᴇɢᴀᴛɪᴠᴇ ʀᴇsᴘᴏɴsᴇ'}"
            )
            
            await query.answer(stats_text, show_alert=True)
            
        except Exception as e:
            print(f"Error showing stats: {e}")
            await query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ sᴛᴀᴛs", show_alert=True)
