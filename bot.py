import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from pathlib import Path
import json
from datetime import datetime

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Storage directories
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Global state management
class BotState:
    def __init__(self):
        self.voice_clients = {}  # {guild_id: voice_client}
        
state = BotState()

# Create a silent audio source to keep connection alive
class SilenceSource(discord.AudioSource):
    """Plays silence to keep voice connection active"""
    def read(self):
        return b'\xF8\xFF\xFE' * 960  # PCM silence

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server(s)')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="vc", description="Make the bot join your voice channel")
async def join_vc(interaction: discord.Interaction):
    """Join the user's voice channel and stay connected"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You need to be in a voice channel first!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    guild_id = interaction.guild.id
    
    # Respond immediately to avoid timeout
    await interaction.response.defer()
    
    try:
        # Clean up any existing connection
        if guild_id in state.voice_clients:
            try:
                old_vc = state.voice_clients[guild_id]
                if old_vc.is_connected():
                    old_vc.stop()
                    await old_vc.disconnect(force=True)
                await asyncio.sleep(1)
            except:
                pass
            del state.voice_clients[guild_id]
        
        # Connect to voice channel
        voice_client = await channel.connect(timeout=20.0, reconnect=True)
        state.voice_clients[guild_id] = voice_client
        
        # Play silence to keep connection alive
        silence = SilenceSource()
        voice_client.play(discord.PCMVolumeTransformer(silence), after=lambda e: print(f'Silence ended: {e}'))
        
        await interaction.followup.send(
            f"✅ **Connected to {channel.name}!**\n"
            f"I'm now playing silence to stay connected.\n"
            f"Use `/speak <text>` to make me talk!"
        )
        
    except asyncio.TimeoutError:
        await interaction.followup.send(
            "❌ Connection timed out. Railway voice can be unstable. Try again!",
            ephemeral=True
        )
    except discord.ClientException as e:
        await interaction.followup.send(
            f"⚠️ Already connected somewhere. Use `/leave` first!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"❌ Connection failed: {e}\n"
            f"Railway has limited voice support.",
            ephemeral=True
        )

@bot.tree.command(name="speak", description="Make the bot speak in voice channel")
@app_commands.describe(text="What should I say?")
async def speak(interaction: discord.Interaction, text: str):
    """Generate and play text-to-speech"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients:
        await interaction.response.send_message(
            "❌ I'm not in a voice channel! Use `/vc` first.",
            ephemeral=True
        )
        return
    
    voice_client = state.voice_clients[guild_id]
    
    if not voice_client.is_connected():
        await interaction.response.send_message(
            "❌ Lost connection to voice. Use `/vc` to reconnect!",
            ephemeral=True
        )
        del state.voice_clients[guild_id]
        return
    
    if len(text) > 200:
        await interaction.response.send_message(
            "❌ Text too long! Keep it under 200 characters.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        # Generate TTS
        output_path = TEMP_DIR / f"tts_{guild_id}_{datetime.now().timestamp()}.mp3"
        
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(output_path))
        except Exception as e:
            await interaction.followup.send(
                f"❌ TTS generation failed: {e}",
                ephemeral=True
            )
            return
        
        # Stop current audio and play TTS
        if voice_client.is_playing():
            voice_client.stop()
        
        # Play TTS
        def after_playing(error):
            if error:
                print(f"Error playing audio: {error}")
            # Resume silence after TTS
            try:
                if voice_client.is_connected() and not voice_client.is_playing():
                    silence = SilenceSource()
                    voice_client.play(discord.PCMVolumeTransformer(silence))
            except:
                pass
            # Clean up file
            try:
                if output_path.exists():
                    os.remove(output_path)
            except:
                pass
        
        audio_source = discord.FFmpegPCMAudio(str(output_path))
        voice_client.play(audio_source, after=after_playing)
        
        await interaction.followup.send(f"🔊 Speaking: *\"{text[:50]}{'...' if len(text) > 50 else ''}\"*")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

@bot.tree.command(name="leave", description="Make the bot leave the voice channel")
async def leave_vc(interaction: discord.Interaction):
    """Leave the voice channel"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients:
        await interaction.response.send_message(
            "❌ I'm not in a voice channel!",
            ephemeral=True
        )
        return
    
    try:
        voice_client = state.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.stop()
        
        await voice_client.disconnect(force=True)
        del state.voice_clients[guild_id]
        
        await interaction.response.send_message("👋 Left the voice channel!")
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error leaving: {e}",
            ephemeral=True
        )
        # Clean up anyway
        if guild_id in state.voice_clients:
            del state.voice_clients[guild_id]

@bot.tree.command(name="status", description="Check bot voice connection status")
async def status_check(interaction: discord.Interaction):
    """Check if bot is connected to voice"""
    guild_id = interaction.guild.id
    
    if guild_id in state.voice_clients:
        vc = state.voice_clients[guild_id]
        if vc.is_connected():
            channel = vc.channel
            playing_status = "🔊 Playing audio" if vc.is_playing() else "🔇 Silent"
            await interaction.response.send_message(
                f"✅ **Status: Connected**\n"
                f"📍 **Channel:** {channel.name}\n"
                f"👥 **Users:** {len(channel.members)}\n"
                f"🎵 **Audio:** {playing_status}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ Connection lost. Use `/vc` to reconnect!",
                ephemeral=True
            )
            del state.voice_clients[guild_id]
    else:
        await interaction.response.send_message(
            "❌ Not connected to voice. Use `/vc` to join!",
            ephemeral=True
        )

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    help_text = """
**🎙️ Railway Voice Bot - Commands**

**Voice Commands:**
• `/vc` - Join your voice channel
• `/speak <text>` - Make the bot speak
• `/status` - Check connection status
• `/leave` - Leave voice channel

**Examples:**
```
/vc
/speak Hello everyone!
/speak This bot works on Railway!
```

**⚠️ Railway Limitations:**
- Voice recording not available (Railway limitation)
- Bot plays silence to stay connected
- TTS works great!

**💡 Tips:**
- Use `/status` to check if I'm still connected
- If I disconnect, just use `/vc` again
- Keep messages under 200 characters for TTS
"""
    await interaction.response.send_message(help_text, ephemeral=True)

# Error handling for voice
@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state changes"""
    # If bot gets disconnected, clean up state
    if member == bot.user and before.channel and not after.channel:
        for guild_id, vc in list(state.voice_clients.items()):
            if vc.guild == member.guild:
                if guild_id in state.voice_clients:
                    del state.voice_clients[guild_id]
                print(f"Cleaned up disconnected voice client for guild {guild_id}")

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Set your bot token in Railway environment variables.")
        exit(1)
    
    print("Starting Railway-optimized voice bot...")
    print("This version plays silence to maintain voice connections.")
    bot.run(TOKEN)
