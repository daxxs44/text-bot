# Discord Voice Recording & TTS Bot

A Discord bot that records voice chat audio from specific users, processes it to remove long pauses, and can generate text-to-speech using the recorded voices.

## Features

- 🎤 **Voice Recording**: Record audio from specific users in voice channels
- ✂️ **Audio Processing**: Automatically removes long pauses between speech
- 🔊 **Playback**: Play back recorded audio in voice channels
- 💾 **Voice Saving**: Save recordings as "voices" for later use
- 🗣️ **Text-to-Speech**: Generate speech using saved voice recordings
- 🎯 **User-Specific Recording**: Choose exactly which person to record

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/vc` | Make the bot join your voice channel | `/vc` |
| `/record @user` | Start recording a specific user's audio | `/record @JohnDoe` |
| `/stop` | Stop the current recording | `/stop` |
| `/play` | Play the most recent recording | `/play` |
| `/save <name>` | Save the current recording as a voice | `/save johns_voice` |
| `/delete` | Delete the current recording | `/delete` |
| `/voices` | List all saved voices | `/voices` |
| `/texttospeech <voice> <text>` | Generate speech using a saved voice | `/texttospeech johns_voice Hello everyone!` |
| `/leave` | Make the bot leave the voice channel | `/leave` |

## Workflow Example

1. **Join voice chat**: `/vc`
2. **Start recording**: `/record @FriendName`
3. *(Friend talks in voice channel)*
4. **Stop recording**: `/stop`
5. **Listen to recording**: `/play`
6. **Save the voice**: `/save friends_voice`
7. **Generate TTS**: `/texttospeech friends_voice Hey, this is pretty cool!`

## Installation

### Deploy to Railway (Recommended for 24/7 Hosting)

Want to host your bot online 24/7? Check out **[RAILWAY.md](RAILWAY.md)** for a complete step-by-step guide to deploy on Railway!

### Local Installation

#### Prerequisites

1. **Python 3.8+** installed
2. **FFmpeg** installed (required for audio processing)
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Step 1: Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Copy your bot token (you'll need this later)

### Step 2: Invite Bot to Your Server

1. Go to "OAuth2" > "URL Generator"
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
4. Copy the generated URL and open it in your browser to invite the bot

### Step 3: Install the Bot

```bash
# Clone or download this repository
cd discord-voice-bot

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_token_here
   ```

### Step 5: Run the Bot

```bash
python bot.py
```

You should see:
```
<BotName> has connected to Discord!
Synced X command(s)
```

## TTS Options

The bot supports multiple TTS engines. By default, it uses gTTS (Google Text-to-Speech).

### Option 1: gTTS (Default)
- ✅ Already included in requirements.txt
- ✅ Easy to use
- ✅ Good quality
- ⚠️ Requires internet
- ⚠️ Basic voice cloning (doesn't truly replicate voice)

### Option 2: Coqui TTS (Recommended for Voice Cloning)
- ✅ High-quality voice cloning
- ✅ Works offline
- ✅ Open source
- ⚠️ Requires more setup
- ⚠️ GPU recommended for fast inference

To use Coqui TTS:

```bash
# Install Coqui TTS
pip install TTS torch torchaudio

# The bot will automatically use it if available
```

### Option 3: Commercial APIs
For production quality, consider:
- **ElevenLabs**: Excellent voice cloning, paid API
- **OpenAI TTS**: Good quality, simple to use
- **Play.ht**: High quality with voice cloning

## Directory Structure

```
discord-voice-bot/
├── bot.py                 # Main bot file
├── audio_processor.py     # Audio processing utilities
├── voice_cloner.py        # TTS and voice cloning
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (create this)
├── .env.example           # Example configuration
├── recordings/            # Stored recordings (auto-created)
├── saved_voices/          # Saved voice models (auto-created)
└── temp/                  # Temporary files (auto-created)
```

## Troubleshooting

### Bot doesn't join voice channel
- Make sure the bot has "Connect" and "Speak" permissions
- Ensure FFmpeg is installed correctly
- Check that PyNaCl is installed: `pip install PyNaCl`

### No audio is recorded
- Verify the user is speaking in the voice channel
- Check that the user hasn't muted themselves
- Ensure the bot has proper voice permissions

### Audio quality is poor
- The default gTTS doesn't truly clone voices
- Install Coqui TTS for better voice cloning
- Ensure recordings are at least 10-15 seconds for better models

### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### FFmpeg not found
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows - Download from ffmpeg.org and add to PATH
```

## Advanced Configuration

### Adjusting Silence Detection

Edit `audio_processor.py` to tune silence removal:

```python
audio_processor = AudioProcessor(
    silence_thresh=-40,      # dBFS threshold (lower = more sensitive)
    min_silence_len=1000,    # Min pause length in ms
    padding=200              # Silence padding in ms
)
```

### Using Better TTS Models

For Coqui TTS, you can change the model in `voice_cloner.py`:

```python
# Use different XTTS models
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# Or other models
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
```

## Privacy & Ethics

⚠️ **Important**: Only record users who have given explicit permission. Recording without consent may violate:
- Discord Terms of Service
- Local privacy laws
- Wiretapping regulations

**Best Practices**:
1. Get written/verbal consent before recording
2. Inform all participants that recording is active
3. Don't share recordings without permission
4. Respect voice data - use responsibly

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational purposes.

## Support

If you encounter issues:
1. Check the Troubleshooting section
2. Ensure all dependencies are installed
3. Verify FFmpeg is working: `ffmpeg -version`
4. Check bot permissions in Discord

## Credits

Built with:
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [pydub](https://github.com/jiaaro/pydub) - Audio processing
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Text-to-Speech (optional)
