import os
import discord
import youtube_dl
from youtube_search import YoutubeSearch

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
YOUTUBE_WATCH = "https://www.youtube.com/watch?v="

queue = []
vc = None
is_playing = False

# set intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# initialize
client = discord.Client(intents=intents)

def play_next(e):
    global queue, vc
    queue.pop()
    if len(queue) > 0:
        url = f"{YOUTUBE_WATCH}{queue[0]['id']}"
        vc.play(discord.FFmpegPCMAudio(url))

def download(url, id):
    opts = {'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                'outtmpl': id}
    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])

# when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    print(client.user.id)

# when the bot gets a message
@client.event
async def on_message(message):
    global queue, vc, is_playing

    if message.author == client.user:
        return

    tokens = message.content.split(' ')
    print(tokens)

    # ignore other messages
    if tokens[0] != 'bwv' and tokens[0] != 'js':
        return

    print(message.author.voice)

    if tokens[1].isnumeric():
        # join the voice channel
        if message.author.voice:
            try:
                channel = message.author.voice.channel
                vc = await channel.connect()
            except:
                print("Already in voice channel")
        else:
            await message.channel.send("❌ Not connected to a voice channel")
        # search for music
        results = YoutubeSearch(f'bwv {tokens[1]}', max_results=10).to_dict()
        print(results[0])
        # play or queue
        queue.append(results[0])
        if is_playing:
            await message.channel.send(f"✅ Added '{results[0]['title']}' to the queue")
        else:
            url = f"{YOUTUBE_WATCH}{queue[0]['id']}"
            # download(url, queue[0]['id'])
            vc.play(discord.FFmpegPCMAudio(source="test.mp3",
                                           executable='../../ffmpeg/bin/ffmpeg.exe'),
                    after=play_next)
            await message.channel.send(f"▶️ Playing {url}")
            is_playing = True

    elif tokens[1] == 'pause':
        if vc and vc.is_playing():
            vc.pause()
            await message.channel.send("⏸️ Paused")
        else:
            await message.channel.send("❌ Not playing anything")

    elif tokens[1] == 'resume':
        if vc and vc.is_paused():
            vc.resume()
            await message.channel.send("⏯️ Resumed")

    elif tokens[1] == 'skip':
        if vc and vc.is_playing:
            vc.stop()
            queue.pop()
        else:
            await message.channel.send("❌ Not playing anything")

    elif tokens[1] == 'stop':
        if vc:
            await message.channel.disconnect()
            queue = []

# start the bot
client.run(BOT_TOKEN)