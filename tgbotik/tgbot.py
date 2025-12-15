import os
import base64
from telebot import types
import requests
import asyncio
import tempfile
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TGTOKEN", "empty")
if(token=="empty"):
    print("Send tg bot token")
    token = input()
storage = StateMemoryStorage()
bot = AsyncTeleBot(token, state_storage=storage)




class StMana(StatesGroup):
    hello = State()
    lang = State()
    anls = State()
    memanls = State()
    datalang = State()
    saver = State()
    filter = State()
    wfm = State()


langs = {
    "english", "spanish", "french", "german", 
    "italian", "portuguese", "russian", "ukranian", "polish", "czech"
}

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.set_state(message.from_user.id, StMana.hello, message.chat.id)
    await get_started(message)




async def send_base64_photo(bot, chat_id,base64_string, caption=None):
    try:
        image_data = base64.b64decode(base64_string)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(image_data)
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as photo_file:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption
                )
        finally:
            os.unlink(tmp_file_path)
            
        return True
        
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
        return False

# Использование в вашем коде: (я искал как кинуть фотку в сооб но в итоге оставил ток эти 4 строки тк оно как оказалось не умеет писать бота и вот пришлось дать еще 1 коммит)
@bot.message_handler(commands=['sendmeme'])
async def send_meme(message):
    await bot.send_message(message.chat.id, 'send the id of the meme')
    await bot.set_state(message.from_user.id, StMana.wfm, message.chat.id)
    


@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    if(current_state == StMana.memanls.name):
        print("working")
        if(message.caption):
            source = message.caption
        else:
            source = ''
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        encoded_image = base64.b64encode(downloaded_file).decode('utf-8')
        try:
            files = {'image': encoded_image, "source": source}
            response = requests.post('http://talker:3456/memmer', 
                                    json=files, timeout=100)

            if response.status_code == 200:
                result = response.json().get("summary", "fail1")
                async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["ans"] = result
                    data["image"] = encoded_image
                await bot.send_message(message.chat.id, result)
                keyboard = types.InlineKeyboardMarkup()
                key_yes = types.InlineKeyboardButton(text='yes', callback_data='Y')
                keyboard.add(key_yes)
                key_no= types.InlineKeyboardButton(text='no', callback_data='N')
                keyboard.add(key_no)
                question = "Save?"
                await bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            else:
                await bot.send_message(message.chat.id, "serverror")
                await bot.delete_state(message.from_user.id, message.chat.id)
        
        except Exception as e:
            await bot.send_message(message.chat.id, f"Ошибка {e}")
            await bot.delete_state(message.from_user.id, message.chat.id)
        



@bot.message_handler(content_types=['text'])
async def translate(message):
    if(message.text == "ok"):
        await get_started(message)
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    print(current_state)
    if current_state == StMana.datalang.name:
        print("Still")
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            lang = data['trans']['lang']
            print(lang)
            text = message.text
            
            print(lang, text)
            response = requests.post("http://talker:3456/translator", json={
                "data": text, 
                "lang": lang
            }, timeout=20)
            print(lang, text)
            if response.status_code == 200:
                translation = response.json().get('Translation', ' ') + " " + response.json().get('translation', ' ')
                await bot.send_message(message.chat.id, f"Перевод ({lang}): {translation}")
            else:
                await bot.send_message(message.chat.id, "Ошибка при переводе")
        
        await bot.delete_state(message.from_user.id, message.chat.id)

    if current_state == StMana.anls.name:
        print("Still")
        text = message.text
        print(text)
        response = requests.post("http://talker:3456/summer", json={
            "data": text
        }, timeout=20)
        if response.status_code == 200:
            translation = response.json().get('summary', 'Summary error')
            await bot.send_message(message.chat.id, f"Summary: {translation}")
        else:
            await bot.send_message(message.chat.id, "Ошибка при работе")
        
        await bot.delete_state(message.from_user.id, message.chat.id)
    

    if current_state == StMana.memanls.name:
        name = message.text
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            tags = data.get("ans", "||||").lower().split("|")[1:4]
            response = requests.post("http://dbworker:3434/addmeme", json={"name":name, "data":data.get("image", " "), "tags":tags }, timeout=40)
            if response.status_code == 200:
                await bot.send_message(message.chat.id, f"saved!")
            else:
                await bot.send_message(message.chat.id, "error")
        await bot.delete_state(message.from_user.id, message.chat.id)
    
    if current_state == StMana.filter.name:
        print("trying to filter")
        by = message.text
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            tags = data.get("filter", "")
            print(tags)
            response = requests.get(f"http://dbworker:3434/{tags}/{by}", timeout=40)
            if response.status_code == 200:
                print(response.json().get("items", []))
                await bot.send_message(message.chat.id, "write /sendmeme to get one\n" + "id, name, tags\n" + "\n".join([" ".join(map(str,x)) for x in response.json().get("items", [])]))
            else:
                 await bot.send_message(message.chat.id, "error")

        await bot.delete_state(message.from_user.id, message.chat.id)
    
    if current_state == StMana.wfm.name:
        response = requests.get(f"http://dbworker:3434/id/{message.text}", timeout=40)
        if response.status_code == 200:
            info = response.json().get('items', [])
            print(info)
            if(len(info) >0):
                await send_base64_photo(bot, message.chat.id, info[0][1], info[0][0])
            else:
                await bot.send_message(message.chat.id, "no such meme")



async def get_started(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='О чем текст', callback_data='1')
    keyboard.add(key_yes)
    key_no= types.InlineKeyboardButton(text='Перевод', callback_data='2')
    keyboard.add(key_no)
    key_ho= types.InlineKeyboardButton(text='Mem-analys', callback_data='3')
    keyboard.add(key_ho)
    key_hot= types.InlineKeyboardButton(text='Saved memes', callback_data='4')
    keyboard.add(key_hot)
    question = "Что ты хочешь получить (если захочешь вернуться к этому окну напиши ok)"
    await bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

  


@bot.callback_query_handler(func=lambda call: True)
async def callback_worker(call):
    await bot.answer_callback_query(call.id)
    lang = ''
    match call.data:
        case "1": 
            await bot.send_message(call.message.chat.id, 'ок, send the data')
            await bot.set_state(call.from_user.id, StMana.anls, call.message.chat.id)
            current_state = await bot.get_state(call.from_user.id, call.message.chat.id)
            print(f"Current state after setting: {current_state}")
            print("waiting for data")

            
        case "2":
            await bot.send_message(call.message.chat.id, 'пон')
            await bot.set_state(call.from_user.id, StMana.lang, call.message.chat.id)
            keyboard = types.InlineKeyboardMarkup()
            for el in langs:
                key_is = types.InlineKeyboardButton(text=el, callback_data=el)
                keyboard.add(key_is)
            question = "Choose Language"
            await bot.send_message(call.message.chat.id, text=question, reply_markup=keyboard)

        case "3": 
            await bot.send_message(call.message.chat.id, 'ок, send the image with the info from what sphere it is')
            await bot.set_state(call.from_user.id, StMana.memanls, call.message.chat.id)
            current_state = await bot.get_state(call.from_user.id, call.message.chat.id)
            print(f"Current state after setting: {current_state}")
            print("waiting for data")
        
        case "4": 
            keyboard = types.InlineKeyboardMarkup()
            key_no= types.InlineKeyboardButton(text='Send all', callback_data='all')
            keyboard.add(key_no)
            key_ho= types.InlineKeyboardButton(text='Send by name', callback_data='name')
            keyboard.add(key_ho)
            key_hot= types.InlineKeyboardButton(text='Send by tag', callback_data='tag')
            keyboard.add(key_hot)
            question = "How Much"
            await bot.send_message(call.from_user.id, text=question, reply_markup=keyboard)

        case "all":
            response = requests.get("http://dbworker:3434/items", timeout=40)
            if response.status_code == 200:
                print(response.json().get("items", []))
                await bot.send_message(call.message.chat.id,"write /sendmeme to get one\n" +"id, name, tags\n" + "\n".join([" ".join(map(str,x)) for x in response.json().get("items", [])]))
            else:
                 await bot.send_message(call.message.chat.id, "error")

            await bot.delete_state(call.message.from_user.id, call.chat.id)
            

        case x if x in ("name", "tag"):
            await bot.send_message(call.message.chat.id, 'send the ' + call.data)
            await bot.set_state(call.from_user.id, StMana.filter, call.message.chat.id)
            async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data['filter'] = call.data
                
            current_state = await bot.get_state(call.from_user.id, call.message.chat.id)
            print(f"Current state after setting: {current_state}")
            print("waiting for data")

        case lang if lang in langs: 
            await bot.send_message(call.message.chat.id, call.data + ', send the data')
            lang = call.data
            await bot.set_state(call.from_user.id, StMana.datalang, call.message.chat.id)
            async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            
                data['trans'] = {
                    'lang': call.data
                }
                
            current_state = await bot.get_state(call.from_user.id, call.message.chat.id)
            print(f"Current state after setting: {current_state}")
            print("waiting for data")

        case "Y":
            await bot.send_message(call.message.chat.id, "send the name of the meme")







async def main():
    await bot.polling(none_stop=True)

if __name__ == '__main__':
    asyncio.run(main())