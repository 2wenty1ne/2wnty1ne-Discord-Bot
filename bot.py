# bot.py

#? Required libaries
import os
import discord
import requests
import random
import time
import ast
from dotenv import load_dotenv
from datetime import date
from PIL import Image


#? Loading the Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
NASA_API_KEY = os.getenv('NASA_API_KEY')
NASA_URL = f'https://api.nasa.gov/planetary/apod?api_key={str(NASA_API_KEY)}'

#? Bot client configuration
intents = discord.Intents.all()
prefix = "%"
client = discord.Client(intents=intents, activity=discord.Game(name=f'prefix: {prefix}'))


#? Gets executed when the bot starts
@client.event
async def on_ready():
    guilds = client.guilds
    print(f"{client.user} is ready\nConnected to {len(guilds)} Server\n")


#? Function to prevent error from empty messages (e.g pictures)
def message_length_check(testobject):
    if not testobject:
        print("empty message")
        return f"""ERROR: Text after this command can't be empty\nFor help type "{prefix}help" """
    elif len(str(testobject)) > 2000:
        print("long message")
        return f"""ERROR: Text after this command has to be less then 2000 characters\n The message you are trying to send has {len(str(testobject))} characters."""
    else:
        return testobject


#? Data from NASA APOD data
def nasa_adop_data(modified_nasa_url, nasa_apod_dict = {}):
    nasa_apod_response_dict = ast.literal_eval(requests.get(modified_nasa_url).text)
    try:
        if "hdurl" in nasa_apod_response_dict:
            nasa_apod_dict["picture_url"] = nasa_apod_response_dict["hdurl"]
        else:
            nasa_apod_dict["picture_url"] = nasa_apod_response_dict["url"]
        nasa_apod_dict["title"] = nasa_apod_response_dict["title"]
        nasa_apod_dict["date"] = nasa_apod_response_dict["date"]
        nasa_apod_dict["explanation"] = nasa_apod_response_dict["explanation"]
        return (1, nasa_apod_dict)
    except KeyError:
        return (0, f"Use right date formating (YYYY-MM-DD). For example 2008-10-26, used with command it would look like this: {prefix}apod date 2008-10-26.")

#? Remembers last APOD
def nasa_apod_last_picture(operator, nasa_apod_dict_input=0, nasa_apod_picture_list=[]):
    if operator == "write":
        if not nasa_apod_picture_list:
            nasa_apod_picture_list.append(nasa_apod_dict_input)
            return (1, f'{nasa_apod_picture_list[0]}') 
        nasa_apod_picture_list[0] = nasa_apod_dict_input
        return (1, f'{nasa_apod_picture_list[0]}') 
    elif operator == "read":
        if nasa_apod_picture_list:
            return (1, nasa_apod_picture_list[0])
        else:
            return (0 ,f'You need to request a picture to get a description.\nUse either "{prefix}apod" to get the picture of today,\n"{prefix}apod random" to get a picture from a random day or\n"{prefix}apod date YYYY-MM-DD" to get a picture from a specific day.')


#? Output random date
def random_dates(start, end=str(date.today()), time_format='%Y-%m-%d'):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + random.random() * (etime-stime)
    return time.strftime(time_format, time.localtime(ptime))

#? Gets executed every time a message is send
@client.event
async def on_message(message):
    global NASA_URL

    guild = message.guild
    channel = client.get_channel(message.channel.id)
    messagerid = message.author.id

    if messagerid == client.user.id:
        return None

    voice_chat_list = []
    for vc in guild.voice_channels:
        voice_chat_list.append(vc)
    

    commandmessage = message_length_check(message.content)
    commandlist = commandmessage.split()
    command = commandlist[0]
    commandlist.pop(0)
    commandtext = " ".join(commandlist)


    if command == f'{prefix}ping':
        await channel.send("Pong!")
    
    
    if command == f'{prefix}rpt':
        await channel.send(message_length_check(commandtext))


    if command == f'{prefix}latency':
        await channel.send(f'Latency: {client.latency}')


    if command == f'{prefix}apod':
        if not commandtext:
            modified_nasa_url = f'{NASA_URL}&concept_tags=True&hd=True'

        elif commandlist[0] == "random": 
            random_date = random_dates("1995-06-26")
            modified_nasa_url = f'{NASA_URL}&concept_tags=True&hd=True&date={random_date}'

        elif commandlist[0] == "date":
            picture_date = commandlist[1]
            modified_nasa_url = f'{NASA_URL}&concept_tags=True&hd=True&date={picture_date}' 

        elif commandlist[0] == "description":
            nasa_apod_picture_tuple = nasa_apod_last_picture("read")
            print(nasa_apod_picture_tuple)
            if not nasa_apod_picture_tuple[0]:
                await channel.send(nasa_apod_picture_tuple[1])
                return 0

            nasa_apod_opened_image = Image.open(requests.get(nasa_apod_picture_tuple[1]["picture_url"], stream=True).raw)
            #await channel.send(f'{nasa_apod_picture_tuple[1]["picture_url"]}')
            await channel.send(f'Title: {nasa_apod_picture_tuple[1]["title"]}\nFrom: {nasa_apod_picture_tuple[1]["date"]}\nResolution: {nasa_apod_opened_image.size}\nDiscription:\n{nasa_apod_picture_tuple[1]["explanation"]}')
            return 1

        else:
            await channel.send(f'Unknown command')
            return 0

        nasa_adop_data_final_tuple = nasa_adop_data(modified_nasa_url)
        if not nasa_adop_data_final_tuple[0]:
            await channel.send(nasa_adop_data_final_tuple[1])
            return 0

        nasa_adop_data_final = nasa_adop_data_final_tuple[1]
        nasa_apod_last_picture("write", nasa_adop_data_final)
        #testimage = Image.open(requests.get(nasa_adop_data_final["picture_url"], stream=True).raw)
        #print(dir(testimage))
        #print(testimage.size)
        await channel.send(f'{nasa_adop_data_final["picture_url"]}')
        await channel.send(f'Title: {nasa_adop_data_final["title"]}\nFrom: {nasa_adop_data_final["date"]}')




client.run(TOKEN)