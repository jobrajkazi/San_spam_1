import discord
from discord.ext import commands
import asyncio
import os

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.dm_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Global variables to track attacks
user_attacks = {}
server_attacks = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Bot is ready to execute commands!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="attack_user", description="Spam attack a Discord user with DMs")
async def attack_user(interaction: discord.Interaction, user_id: str, message: str):
    try:
        # Convert user_id to integer
        target_id = int(user_id)
        target_user = await bot.fetch_user(target_id)
        
        if not target_user:
            await interaction.response.send_message("User not found!")
            return
            
        # Check if attack is already running on this user
        if str(target_id) in user_attacks and user_attacks[str(target_id)]:
            await interaction.response.send_message("Attack already in progress on this user!")
            return
            
        # Start the attack
        user_attacks[str(target_id)] = True
        await interaction.response.send_message(f"Attack started on {target_user.name}! Use /stop01 to stop.")
        
        # Send messages until stopped
        while user_attacks.get(str(target_id), False):
            try:
                await target_user.send(message)
                await asyncio.sleep(0.5)  # Small delay to prevent rate limiting
            except discord.Forbidden:
                await interaction.channel.send(f"Failed to DM {target_user.name}. User might have DMs disabled or blocked the bot.")
                break
            except Exception as e:
                print(f"Error sending DM: {e}")
                await asyncio.sleep(5)  # Wait longer if there's an error
                
    except ValueError:
        await interaction.response.send_message("Invalid user ID! Please provide a valid numeric user ID.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")

@bot.tree.command(name="attack_server", description="Spam attack a Discord server with messages")
async def attack_server(interaction: discord.Interaction, server_id: str, message: str):
    try:
        # Convert server_id to integer
        target_id = int(server_id)
        target_guild = bot.get_guild(target_id)
        
        if not target_guild:
            await interaction.response.send_message("Server not found! Make sure the bot is in the server.")
            return
            
        # Check if attack is already running on this server
        if str(target_id) in server_attacks and server_attacks[str(target_id)]:
            await interaction.response.send_message("Attack already in progress on this server!")
            return
            
        # Start the attack
        server_attacks[str(target_id)] = True
        await interaction.response.send_message(f"Attack started on {target_guild.name}! Use /stop01 to stop.")
        
        # Find a channel to spam
        channel = None
        for ch in target_guild.text_channels:
            if ch.permissions_for(target_guild.me).send_messages:
                channel = ch
                break
                
        if not channel:
            await interaction.channel.send("No channels available to send messages in!")
            server_attacks[str(target_id)] = False
            return
            
        # Send messages until stopped
        while server_attacks.get(str(target_id), False):
            try:
                await channel.send(message)
                await asyncio.sleep(0.5)  # Small delay to prevent rate limiting
            except discord.Forbidden:
                await interaction.channel.send(f"Failed to send messages in {target_guild.name}. Missing permissions.")
                break
            except Exception as e:
                print(f"Error sending message: {e}")
                await asyncio.sleep(5)  # Wait longer if there's an error
                
    except ValueError:
        await interaction.response.send_message("Invalid server ID! Please provide a valid numeric server ID.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")

@bot.tree.command(name="stop01", description="Stop all active attacks")
async def stop_attacks(interaction: discord.Interaction):
    # Stop all user attacks
    for user_id in list(user_attacks.keys()):
        user_attacks[user_id] = False
        
    # Stop all server attacks
    for server_id in list(server_attacks.keys()):
        server_attacks[server_id] = False
        
    await interaction.response.send_message("All attacks have been stopped!")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
