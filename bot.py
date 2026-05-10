import discord
from discord.ext import commands
import asyncio
import os

# SYSTEM REQUIREMENTS: 
# You MUST enable 'Server Members Intent' in the Discord Developer Portal
intents = discord.Intents.default()
intents.members = True 
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

active_targets = set()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}. Network access established.')

@bot.tree.command(name="spam", description="Target any shared network ID")
async def spam(interaction: discord.Interaction, target_id: str, message: str):
    await interaction.response.send_message(f"Targeting ID: {target_id}")
    
    active_targets.add(target_id)
    t_id = int(target_id)

    while target_id in active_targets:
        try:
            # Look for the target in all servers the bot is in
            target = bot.get_user(t_id) or await bot.fetch_user(t_id)
            
            if target:
                await target.send(message)
                # Very fast timing
                await asyncio.sleep(0.3) 
            else:
                await interaction.channel.send("Target not found in shared network.")
                break
                
        except discord.Forbidden:
            # This happens if DMs are closed or the bot is blocked
            await asyncio.sleep(2)
            continue
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

@bot.tree.command(name="stop", description="Halt all spam")
async def stop(interaction: discord.Interaction):
    active_targets.clear()
    await interaction.response.send_message("All tasks cleared.")

bot.run(os.getenv('DISCORD_TOKEN'))
