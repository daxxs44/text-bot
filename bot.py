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
        self.audio_sinks = {}       # {guild_id: sink}
        self.latest_recording = {}  # {guild_id: filepath}
        self.temp_recordings = {}   # {guild_id: filepath}
        
state = BotState()
audio_processor = AudioProcessor()
voice_cloner = VoiceCloner()

# Custom audio sink for recording specific users
class UserAudioSink(discord.sinks.MP3Sink):
    def __init__(self, target_user_id):
        super().__init__()
        self.target_user_id = target_user_id
        self.recorded_audio = []
        
    def write(self, data, user):
        if user and user.id == self.target_user_id:
            self.recorded_audio.append(data)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
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
    
    # Disconnect if already in a voice channel
    if guild_id in state.voice_clients and state.voice_clients[guild_id].is_connected():
        await state.voice_clients[guild_id].disconnect()
    
    try:
        voice_client = await channel.connect()
        state.voice_clients[guild_id] = voice_client
        await interaction.response.send_message(f"✅ Joined {channel.name}!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to join voice channel: {e}", ephemeral=True)

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
    
    # Start recording
    await interaction.response.defer()
    
    try:
        voice_client = state.voice_clients[guild_id]
        
        # Stop any existing recording
        if voice_client.is_listening():
            voice_client.stop_listening()
        
        # Create new sink for this user
        sink = UserAudioSink(user.id)
        state.audio_sinks[guild_id] = sink
        state.recording_users[guild_id] = user.id
        
        # Start listening
        voice_client.start_listening(sink)
        
        await interaction.followup.send(f"🔴 Recording {user.mention}'s audio... Use `/stop` when done!")
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to start recording: {e}", ephemeral=True)

@bot.tree.command(name="stop", description="Stop the current recording")
async def stop_recording(interaction: discord.Interaction):
    """Stop recording and process the audio"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_listening():
        await interaction.response.send_message("❌ Not currently recording!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        voice_client = state.voice_clients[guild_id]
        sink = state.audio_sinks[guild_id]
        
        # Stop recording
        voice_client.stop_listening()
        
        # Save raw recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = TEMP_DIR / f"raw_{guild_id}_{timestamp}.mp3"
        
        # Write audio data to file
        await asyncio.sleep(1)  # Give time for buffer to flush
        
        if sink.recorded_audio:
            with open(raw_path, 'wb') as f:
                for data in sink.recorded_audio:
                    f.write(data)
            
            # Process audio (remove silences)
            processed_path = TEMP_DIR / f"processed_{guild_id}_{timestamp}.mp3"
            audio_processor.remove_long_pauses(str(raw_path), str(processed_path))
            
            # Store as latest recording
            state.latest_recording[guild_id] = str(processed_path)
            state.temp_recordings[guild_id] = str(processed_path)
            
            await interaction.followup.send("✅ Recording stopped and processed! Use `/play` to listen.")
        else:
            await interaction.followup.send("❌ No audio was recorded. Make sure the user was speaking!", ephemeral=True)
            
        # Clean up
        if raw_path.exists():
            os.remove(raw_path)
            
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to process recording: {e}", ephemeral=True)

@bot.tree.command(name="play", description="Play the most recent recording")
async def play(interaction: discord.Interaction):
    """Play the most recent recording"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.latest_recording:
        await interaction.response.send_message("❌ No recording available!", ephemeral=True)
        return
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        voice_client = state.voice_clients[guild_id]
        
        # Stop any current audio
        if voice_client.is_playing():
            voice_client.stop()
        
        recording_path = state.latest_recording[guild_id]
        
        # Play the recording
        audio_source = discord.FFmpegPCMAudio(recording_path)
        voice_client.play(audio_source)
        
        await interaction.followup.send("▶️ Playing recording...")
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to play recording: {e}", ephemeral=True)

@bot.tree.command(name="save", description="Save the current recording as a voice")
@app_commands.describe(voice_name="Name for this voice")
async def save_recording(interaction: discord.Interaction, voice_name: str):
    """Save the current recording for voice cloning"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.temp_recordings:
        await interaction.response.send_message("❌ No recording to save!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        temp_path = state.temp_recordings[guild_id]
        
        # Create voice directory
        voice_dir = VOICES_DIR / f"{guild_id}_{voice_name}"
        voice_dir.mkdir(exist_ok=True)
        
        # Save the recording
        saved_path = voice_dir / "recording.mp3"
        
        # Copy file
        import shutil
        shutil.copy(temp_path, saved_path)
        
        # Save metadata
        metadata = {
            "name": voice_name,
            "created": datetime.now().isoformat(),
            "guild_id": guild_id,
            "user_id": state.recording_users.get(guild_id)
        }
        
        with open(voice_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Train voice model
        await interaction.followup.send("⏳ Training voice model... This may take a moment.")
        
        model_path = voice_cloner.train_voice(str(saved_path), str(voice_dir / "model"))
        
        if model_path:
            await interaction.followup.send(f"✅ Voice '{voice_name}' saved successfully! Use `/texttospeech` to use it.")
        else:
            await interaction.followup.send("⚠️ Voice saved but model training failed. You can still use the recording.", ephemeral=True)
        
        # Clean up temp
        if guild_id in state.temp_recordings:
            del state.temp_recordings[guild_id]
            
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to save recording: {e}", ephemeral=True)

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

@bot.tree.command(name="texttospeech", description="Generate speech using a saved voice")
@app_commands.describe(
    voice_name="The voice to use",
    text="The text to speak"
)
async def text_to_speech(interaction: discord.Interaction, voice_name: str, text: str):
    """Generate and play TTS using a saved voice"""
    guild_id = interaction.guild.id
    
    if guild_id not in state.voice_clients or not state.voice_clients[guild_id].is_connected():
        await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
        return
    
    # Find voice directory
    voice_dir = VOICES_DIR / f"{guild_id}_{voice_name}"
    if not voice_dir.exists():
        await interaction.response.send_message(f"❌ Voice '{voice_name}' not found! Use `/voices` to see available voices.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Generate TTS
        output_path = TEMP_DIR / f"tts_{guild_id}_{datetime.now().timestamp()}.mp3"
        
        voice_cloner.generate_speech(
            text,
            str(voice_dir / "model"),
            str(output_path)
        )
        
        # Play the generated audio
        voice_client = state.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.stop()
        
        audio_source = discord.FFmpegPCMAudio(str(output_path))
        voice_client.play(audio_source, after=lambda e: os.remove(output_path) if output_path.exists() else None)
        
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

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
        exit(1)
    
    bot.run(TOKEN)
