# bot.py

#? Required libaries
import os
import discord
from dotenv import load_dotenv


#? Loading the Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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


#? Gets executed every time a message is send
@client.event
async def on_message(message):
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

    if command == f'{prefix}test':
        print(client.user.name)
    
    if command == f'{prefix}msg':
        await channel.send(message_length_check(commandtext))



client.run(TOKEN)