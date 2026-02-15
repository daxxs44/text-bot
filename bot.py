import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from pathlib import Path
import json
from datetime import datetime
from audio_processor import AudioProcessor
from voice_cloner import VoiceCloner

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Storage directories
RECORDINGS_DIR = Path("recordings")
TEMP_DIR = Path("temp")
VOICES_DIR = Path("saved_voices")

for directory in [RECORDINGS_DIR, TEMP_DIR, VOICES_DIR]:
    directory.mkdir(exist_ok=True)

# Global state management
class BotState:
    def __init__(self):
        self.recording_users = {}  # {guild_id: user_id}
        self.voice_clients = {}     # {guild_id: voice_client}
        self.latest_recording = {}  # {guild_id: filepath}
        self.temp_recordings = {}   # {guild_id: filepath}
        self.recording_tasks = {}   # {guild_id: task}
        
state = BotState()
audio_processor = AudioProcessor()
voice_cloner = VoiceCloner()

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
    """Join the user's voice channel"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You need to be in a voice channel first!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    guild_id = interaction.guild.id
    
    # Respond immediately to avoid timeout
    await interaction.response.defer()
    
    try:
        # Disconnect if already in a voice channel
        if guild_id in state.voice_clients:
            try:
                if state.voice_clients[guild_id].is_connected():
                    await state.voice_clients[guild_id].disconnect()
            except:
                pass
            del state.voice_clients[guild_id]
        
        # Connect to voice
        voice_client = await channel.connect(timeout=10.0, reconnect=True)
        state.voice_clients[guild_id] = voice_client
        
        await interaction.followup.send(f"✅ Joined {channel.name}!")
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Connection timed out. Please try again!", ephemeral=True)
    except discord.ClientException as e:
        await interaction.followup.send(f"❌ Already connected or connection error: {e}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to join voice channel: {e}", ephemeral=True)

@bot.tree.command(name="record", description="Start recording a specific user's audio")
@app_commands.describe(user="The user to record")
async def record(interaction: discord.Interaction, user: discord.Member):
    """Start recording a specific user"""
    guild_id = interaction.guild.id
    
    # Check if bot is in voice channel
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel! Use `/vc` first.", ephemeral=True)
        return
    
    # Check if target user is in voice
    if not user.voice or user.voice.channel != state.voice_clients[guild_id].channel:
        await interaction.response.send_message(f"❌ {user.mention} is not in the voice channel!", ephemeral=True)
        return
    
    await interaction.response.send_message(
        f"⚠️ **Note:** Full voice recording requires additional setup.\n"
        f"For now, recording {user.mention} is simulated.\n"
        f"Use `/stop` when done, then `/play` to hear a test audio.",
        ephemeral=False
    )
    
    state.recording_users[guild_id] = user.id

@bot.tree.command(name="stop", description="Stop the current recording")
async def stop_recording(interaction: discord.Interaction):
    """Stop recording and create a test recording"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.recording_users:
        await interaction.response.send_message("❌ Not currently recording!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Create a test recording file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_path = TEMP_DIR / f"recording_{guild_id}_{timestamp}.txt"
        
        # Save metadata
        with open(recording_path, 'w') as f:
            f.write(f"Recording for user {state.recording_users[guild_id]}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("Note: This is a placeholder. Full voice recording requires additional setup.\n")
        
        # Store as latest recording
        state.latest_recording[guild_id] = str(recording_path)
        state.temp_recordings[guild_id] = str(recording_path)
        
        await interaction.followup.send(
            "✅ Recording stopped!\n"
            "⚠️ Note: Full voice recording is not yet implemented in this deployment.\n"
            "The bot can still do TTS with `/texttospeech` using pre-made voices!"
        )
            
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to process recording: {e}", ephemeral=True)

@bot.tree.command(name="play", description="Play test audio (voice recording not fully implemented)")
async def play(interaction: discord.Interaction):
    """Inform user about recording limitations"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
        return
    
    await interaction.response.send_message(
        "⚠️ **Voice recording playback is not yet available in this deployment.**\n\n"
        "**What works:**\n"
        "✅ Bot can join voice channels (`/vc`)\n"
        "✅ Text-to-speech (`/texttospeech`)\n"
        "✅ Playing audio files\n\n"
        "**What needs setup:**\n"
        "⚠️ Recording user audio (requires discord.py voice receive setup)\n\n"
        "For full voice recording, you'll need to run the bot locally with additional audio dependencies.",
        ephemeral=True
    )

@bot.tree.command(name="save", description="Save the current recording metadata")
@app_commands.describe(voice_name="Name for this voice")
async def save_recording(interaction: discord.Interaction, voice_name: str):
    """Save recording metadata"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.temp_recordings:
        await interaction.response.send_message("❌ No recording to save!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Create voice directory
        voice_dir = VOICES_DIR / f"{guild_id}_{voice_name}"
        voice_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata = {
            "name": voice_name,
            "created": datetime.now().isoformat(),
            "guild_id": guild_id,
            "user_id": state.recording_users.get(guild_id),
            "note": "Placeholder - full voice cloning requires local setup"
        }
        
        with open(voice_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        await interaction.followup.send(
            f"✅ Voice '{voice_name}' metadata saved!\n"
            f"⚠️ Note: For full voice cloning, run the bot locally with TTS packages installed."
        )
        
        # Clean up temp
        if guild_id in state.temp_recordings:
            del state.temp_recordings[guild_id]
            
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to save: {e}", ephemeral=True)

@bot.tree.command(name="delete", description="Delete the current recording")
async def delete_recording(interaction: discord.Interaction):
    """Delete the current temporary recording"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.temp_recordings:
        await interaction.response.send_message("❌ No recording to delete!", ephemeral=True)
        return
    
    try:
        temp_path = state.temp_recordings[guild_id]
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        del state.temp_recordings[guild_id]
        if guild_id in state.latest_recording:
            del state.latest_recording[guild_id]
        
        await interaction.response.send_message("🗑️ Recording deleted!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to delete recording: {e}", ephemeral=True)

@bot.tree.command(name="voices", description="List all saved voices")
async def list_voices(interaction: discord.Interaction):
    """List all available voices for this server"""
    guild_id = interaction.guild.id
    
    voices = []
    for voice_dir in VOICES_DIR.iterdir():
        if voice_dir.is_dir() and voice_dir.name.startswith(f"{guild_id}_"):
            metadata_path = voice_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    voices.append(metadata['name'])
    
    if voices:
        voice_list = "\n".join([f"• {voice}" for voice in voices])
        await interaction.response.send_message(f"**Available Voices:**\n{voice_list}")
    else:
        await interaction.response.send_message("No saved voices yet! Use `/save` after recording.", ephemeral=True)

@bot.tree.command(name="texttospeech", description="Generate speech using text-to-speech")
@app_commands.describe(text="The text to speak")
async def text_to_speech(interaction: discord.Interaction, text: str):
    """Generate and play TTS"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel! Use `/vc` first.", ephemeral=True)
        return
    
    if len(text) > 200:
        await interaction.response.send_message("❌ Text too long! Keep it under 200 characters.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Generate TTS using gTTS
        output_path = TEMP_DIR / f"tts_{guild_id}_{datetime.now().timestamp()}.mp3"
        
        # Use basic TTS
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(output_path))
        except Exception as e:
            await interaction.followup.send(f"❌ TTS generation failed: {e}\nMake sure gTTS is installed.", ephemeral=True)
            return
        
        # Play the generated audio
        voice_client = state.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.stop()
        
        def cleanup(error):
            if output_path.exists():
                try:
                    os.remove(output_path)
                except:
                    pass
        
        audio_source = discord.FFmpegPCMAudio(str(output_path))
        voice_client.play(audio_source, after=cleanup)
        
        await interaction.followup.send(f"🔊 Speaking: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to generate speech: {e}", ephemeral=True)

@bot.tree.command(name="leave", description="Make the bot leave the voice channel")
async def leave_vc(interaction: discord.Interaction):
    """Leave the voice channel"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
        return
    
    try:
        await state.voice_clients[guild_id].disconnect()
        del state.voice_clients[guild_id]
        
        await interaction.response.send_message("👋 Left the voice channel!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to leave: {e}", ephemeral=True)

@bot.tree.command(name="status", description="Check bot voice connection status")
async def status_check(interaction: discord.Interaction):
    """Check if bot is connected to voice"""
    guild_id = interaction.guild.id
    
    if guild_id in state.voice_clients:
        vc = state.voice_clients[guild_id]
        if vc.is_connected():
            channel = vc.channel
            await interaction.response.send_message(
                f"✅ **Connected to:** {channel.name}\n"
                f"**Channel ID:** {channel.id}\n"
                f"**Users in channel:** {len(channel.members)}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ Bot has a voice client but is not connected. Try `/vc` again.",
                ephemeral=True
            )
            # Clean up disconnected client
            del state.voice_clients[guild_id]
    else:
        await interaction.response.send_message(
            "❌ Bot is not in a voice channel. Use `/vc` to make it join!",
            ephemeral=True
        )

@bot.tree.command(name="help", description="Show bot commands and limitations")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    help_text = """
**Discord Voice Bot - Commands**

**✅ Working Commands:**
• `/vc` - Bot joins your voice channel
• `/status` - Check bot's voice connection status
• `/texttospeech <text>` - Generate speech from text
• `/leave` - Bot leaves voice channel
• `/voices` - List saved voice metadata
• `/help` - Show this message

**⚠️ Limited Commands (Railway):**
• `/record @user` - Records metadata only (not actual audio)
• `/stop` - Stops recording simulation
• `/save <name>` - Saves recording metadata
• `/delete` - Deletes recording metadata

**Note:** Full voice recording requires running the bot locally with additional audio libraries. On Railway, the bot can join voice channels and do text-to-speech, but cannot record user audio.

**For full functionality:** Download the bot code and run it locally with all dependencies installed.
"""
    await interaction.response.send_message(help_text, ephemeral=True)

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please set your bot token in Railway environment variables.")
        exit(1)
    
    print("Starting bot...")
    print("Note: Voice recording is limited on Railway deployment.")
    print("For full features, run locally with all dependencies.")
    bot.run(TOKEN)
