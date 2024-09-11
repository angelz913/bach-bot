import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import youtube_dl
import yt_dlp

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Set intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

# Options for streaming music
ytdl_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}
ytdl = youtube_dl.YoutubeDL(ytdl_options)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.tree.command(name="play", description="Play music from an url")
async def play(interaction: discord.Interaction, url: str):
    await interaction.user.voice.channel.connect()
    await interaction.response.defer()
    async with interaction.channel.typing():
        # Get the direct streamable url
        with yt_dlp.YoutubeDL(ytdl_options) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
        audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        interaction.guild.voice_client.play(audio_source)
    await interaction.followup.send(f"Start playing: {url}")

@bot.tree.command(name="resume", description="Resume music")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        vc.resume()
        await interaction.response.send_message("Resumed")

@bot.tree.command(name="pause", description="Pause music")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("Paused")
    else:
        await interaction.response.send_message("Not playing music")

@bot.tree.command(name="stop", description="Stop music")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("Stopped")
    else:
        await interaction.response.send_message("Not playing music")

@bot.tree.command(name="composer", description="Play music by a specific composer")
async def composer(interaction: discord.Interaction, composer: str):
    await interaction.response.send_message(f"Your specified era was {composer}")

era_choices = [
    app_commands.Choice(name="Renaissance", value="renaissance"),
    app_commands.Choice(name="Baroque", value="baroque"),
    app_commands.Choice(name="Classical", value="classical"),
    app_commands.Choice(name="Romantic", value="romantic"),
    app_commands.Choice(name="20th Century", value="20th_century")
]

@bot.tree.command(name="era", description="Play music from a specific era")
async def era(interaction: discord.Interaction, choice: str):
    await interaction.response.send_message(f"Your specified era was {choice}")

@era.autocomplete("choice")
async def autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=choice.name, value=choice.value)
        for choice in era_choices if current.lower() in choice.name.lower()
    ]

# Start the bot
bot.run(BOT_TOKEN)
