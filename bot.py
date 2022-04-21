# bot.py
#by DarkVIC -> https://github.com/DarkVIC/2wnty1ne-Discord-Bot

#? Required libaries
import os
import discord
import requests
import random
import ast
import time
from datetime import datetime
from dotenv import load_dotenv
from datetime import date
from PIL import Image


#? Loading the Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
NASA_API_KEY = os.getenv('NASA_API_KEY')
NASA_URL = f'https://api.nasa.gov/planetary/apod?api_key={str(NASA_API_KEY)}&thumbs=True&hd=True'

#? Bot client configuration
intents = discord.Intents.all()
prefix = "!"
client = discord.Client(intents=intents, activity=discord.Game(name=f'prefix: {prefix}'))


#? Gets executed when the bot starts
@client.event
async def on_ready():
    guilds = client.guilds
    print(f"{client.user} is ready\nConnected to {len(guilds)} Server\n")


#? Function to prevent error from empty messages (e.g pictures)
def message_length_check(testobject, switch):
    #TODO Need to fix the usage of the switch
    if not testobject:
        if switch:
            print(f"""ERROR: Text after this command can't be empty\nFor help type "{prefix}help" """)
        return (0, "empty message")
    elif len(str(testobject)) > 2000:
        if switch:
            print(f"""ERROR: Text after this command has to be less then 2000 characters\n The message you are trying to send has {len(str(testobject))} characters.""")
        return (0, "long message")
    else:
        return (1, testobject)


#? Function to send embeded message
async def send_message(m_title = None, m_description = None, m_image_url = None, m_video_url = None, switch = "server", dmrecipient=None, message=None):
    em_title = message_length_check(m_title, 0)
    em_description = message_length_check(m_description, 0)
    em_image_url = message_length_check(m_image_url, 0)
    em_video_url = message_length_check(m_video_url, 0)
    em_part_description = ""

    current_time = datetime.utcnow()
    embeded_response = discord.Embed(timestamp=current_time, color=discord.Color.random())
    if not em_title[0] and not em_description[0] and not em_image_url[0]:
        print("Error: Title and description empty")
        return
    if em_title[0]:
        embeded_response.title = em_title[1]
    if em_description[0]:
        if em_video_url[0]:
            em_part_description = em_part_description + f'\nVideo url: {em_video_url[1]}'
        embeded_response.description = em_description[1] + em_part_description
    if em_image_url[0]:
        embeded_response.set_image(url = em_image_url[1])

        #TODO Didnt get it to work, still need to use the stream below
        #embeded_image_resolution = f'{embeded_response.image.width}x{embeded_response.image.height}'


    if switch == "server":
        channel = client.get_channel(message.channel.id)
        await channel.send(embed=embeded_response)
    elif switch == "dm":
        dmrecipient.create_dm
        await dmrecipient.send(embed=embeded_response)


#? Data from NASA APOD data
def nasa_adop_data(modified_nasa_url, nasa_apod_dict = {}):
    nasa_apod_response_dict = ast.literal_eval(requests.get(modified_nasa_url).text)
    if "title" in nasa_apod_response_dict:
        nasa_apod_dict["title"] = nasa_apod_response_dict["title"]
        nasa_apod_dict["date"] = nasa_apod_response_dict["date"]
        nasa_apod_dict["explanation"] = nasa_apod_response_dict["explanation"]
    else:
        return (0, f"Use right date formating (YYYY-MM-DD). For example 2008-10-26, used with command it would look like this: {prefix}apod date 2008-10-26.")

    if nasa_apod_response_dict["media_type"] == "video":
        nasa_apod_dict["picture_url"] = [nasa_apod_response_dict["thumbnail_url"], nasa_apod_response_dict["url"]]
    else:
        if "hdurl" in nasa_apod_response_dict:
            nasa_apod_dict["picture_url"] = nasa_apod_response_dict["hdurl"]
        else:
            nasa_apod_dict["picture_url"] = nasa_apod_response_dict["url"]
    return [1, nasa_apod_dict]



nasa_apod_picture_list=[]
#? Stores last picture for every channel a picture was send in
def nasa_apod_last_picture(operator, channel_id, nasa_apod_dict_input=0):
    global nasa_apod_picture_list
    nasa_adop_to_pop = None
    if operator == "write":
        if nasa_apod_picture_list:
            for i, nasa_apod_picture_list_value in enumerate(nasa_apod_picture_list):
                if nasa_apod_picture_list_value[0] == channel_id:
                    nasa_adop_to_pop = i + 1
                    break
            if nasa_adop_to_pop:
                nasa_apod_picture_list.pop(nasa_adop_to_pop - 1)
            nasa_apod_picture_list.append((channel_id, nasa_apod_dict_input))
        else:
            nasa_apod_picture_list.append((channel_id, nasa_apod_dict_input))
        return 1
    elif operator == "read":
        if nasa_apod_picture_list:
            nasa_adop_current_save = [nasa_apod_server_touple for nasa_apod_server_touple in nasa_apod_picture_list if nasa_apod_server_touple[0] == channel_id]
            if nasa_adop_current_save:
                return (1, nasa_adop_current_save[0][1])
        return (0 ,f'You need to request a picture in this channel to get a description.\nUse either "{prefix}apod" to get the picture of today,\n"{prefix}apod random" to get a picture from a random day or\n"{prefix}apod date YYYY-MM-DD" to get a picture from a specific day.')


#? Output random date
def random_dates(start, end=str(date.today()), time_format='%Y-%m-%d'):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + random.random() * (etime-stime)
    return time.strftime(time_format, time.localtime(ptime))

#? Gets executed every time a message is send
@client.event
async def on_message(message):
    global nasa_apod_picture_list
    global NASA_URL

    guild = message.guild
    channel = client.get_channel(message.channel.id)
    messagerid = message.author.id

    if messagerid == client.user.id:
        return None

    voice_chat_list = []
    for vc in guild.voice_channels:
        voice_chat_list.append(vc)


    commandmessage = message_length_check(message.content, 1)[1]
    commandlist = commandmessage.split()
    command = commandlist[0]
    commandlist.pop(0)
    commandtext = " ".join(commandlist)



    if command == f'{prefix}ping':
        await send_message(m_title="Pong!", message=message)
    

    if command == f'{prefix}rpt':
        #TODO better message if input is empty
        await send_message(m_title=commandtext, m_description=f'From: {message.author.nick}', message=message)


    if command == f'{prefix}latency':
        await send_message("Latency: ", f'{str(client.latency)} ms', message=message)


    if command == f'{prefix}apod':
        if not commandtext:
            modified_nasa_url = f'{NASA_URL}'

        elif commandlist[0] == "random": 
            random_date = random_dates("1995-06-26")
            modified_nasa_url = f'{NASA_URL}&date={random_date}'

        elif commandlist[0] == "date":
            picture_date = commandlist[1]
            modified_nasa_url = f'{NASA_URL}&date={picture_date}'

        elif commandlist[0] == "description":
            nasa_apod_last_picture_response = nasa_apod_last_picture("read", message.channel.id)
            if nasa_apod_last_picture_response[0]:
                nasa_apod_picture_dict = ast.literal_eval(nasa_apod_last_picture_response[1])

                nasa_apod_opened_image_size = Image.open(requests.get(nasa_apod_picture_dict["picture_url"], stream=True).raw).size

                embeded_response_title = nasa_apod_picture_dict["title"]
                embeded_response_date = f'From: {nasa_apod_picture_dict["date"]}'
                embeded_response_resolution = f'Resolution: {nasa_apod_opened_image_size[0]}x{nasa_apod_opened_image_size[1]}'
                embeded_response_description = f'From: {embeded_response_date}\nResolution: {embeded_response_resolution}\nDescription:\n{nasa_apod_picture_dict["explanation"]}'
                await send_message(m_title=embeded_response_title, m_description=embeded_response_description, message=message)
                return 1
            else:
                await send_message(m_title="Warning", m_description=nasa_apod_last_picture_response[1], message=message)
                return 0 

        else:
            await send_message(m_title=f'Unknown command', message=message)
            return 0

        nasa_adop_data_final_tuple = nasa_adop_data(modified_nasa_url)
        if not nasa_adop_data_final_tuple[0]:
            await channel.send(nasa_adop_data_final_tuple[1])
            return 0


        nasa_adop_data_final = nasa_adop_data_final_tuple[1]
        nasa_apod_last_picture("write", message.channel.id, str(nasa_adop_data_final))
        
        if isinstance(nasa_adop_data_final["picture_url"], list):
            embeded_response_image = nasa_adop_data_final["picture_url"][0]
            embeded_response_video_url = nasa_adop_data_final["picture_url"][1]
        else:
            embeded_response_image = nasa_adop_data_final["picture_url"]
            embeded_response_video_url = None

        embeded_response_title = nasa_adop_data_final["title"]
        embeded_response_description = nasa_adop_data_final["date"]
        await send_message(m_title=embeded_response_title, m_description=embeded_response_description, m_image_url=embeded_response_image, m_video_url = embeded_response_video_url, message=message)



client.run(TOKEN)