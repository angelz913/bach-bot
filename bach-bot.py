import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

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

@bot.tree.command(name="play", description="Play music from a link")
async def play(interaction: discord.Interaction, link: str):
    await interaction.response.send_message(f"Your link was {link}")

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
