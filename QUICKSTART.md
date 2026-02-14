# Quick Start Guide

Get your bot running in 5 minutes!

## 📚 New Here? Start With Full Setup!

**First time?** Check out these detailed guides:
- **[SETUP.md](SETUP.md)** - Complete setup from scratch (Discord bot creation, Python, FFmpeg, everything!)
- **[ENV_GUIDE.md](ENV_GUIDE.md)** - Step-by-step .env file creation with screenshots

---

## 🚀 Option 1: Deploy to Railway (24/7 Hosting)

**Easiest way to run your bot 24/7!**

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → "New Project" → "Deploy from GitHub repo"
3. Add environment variable: `DISCORD_BOT_TOKEN` = your token
4. Done! Bot runs 24/7 automatically

**Full guide**: See [RAILWAY.md](RAILWAY.md)

---

## 💻 Option 2: Run Locally

### Step 1: Install FFmpeg (Required)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

## Step 2: Get Discord Bot Token

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" tab → "Add Bot"
4. Enable these intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Copy the token

## Step 3: Invite Bot to Server

1. Go to OAuth2 → URL Generator
2. Check: `bot` and `applications.commands`
3. Bot Permissions: Check all voice/message permissions
4. Copy URL and open in browser

## Step 4: Setup & Run

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and paste your bot token
# Then run:
python bot.py
```

## Step 5: Use the Bot!

In Discord:
1. Join a voice channel
2. `/vc` - Bot joins
3. `/record @username` - Start recording
4. *(Let them talk for 10-15 seconds)*
5. `/stop` - Stop recording
6. `/play` - Hear the recording
7. `/save my_voice` - Save the voice
8. `/texttospeech my_voice Hello world!` - Test TTS

## Common Issues

**"Bot token is incorrect"**
- Make sure you copied the entire token from Discord Developer Portal
- Check for extra spaces in .env file

**"Cannot connect to voice channel"**
- Bot needs "Connect" and "Speak" permissions
- Make sure you're in the voice channel when using `/vc`

**"No audio recorded"**
- User must be actively speaking
- Check their mic isn't muted in Discord
- Recording needs 2-3+ seconds of audio

**"FFmpeg not found"**
- FFmpeg must be installed and in your system PATH
- Test with: `ffmpeg -version`

## Tips for Best Results

1. **Recording Quality**
   - Record in a quiet environment
   - Have the person speak for 15-30 seconds
   - Include varied speech (questions, statements, different emotions)

2. **Voice Cloning**
   - Install Coqui TTS for better results: `pip install TTS`
   - Longer recordings = better voice models
   - Clear, consistent audio works best

3. **Multiple Voices**
   - You can save multiple voices per server
   - Use descriptive names: `/save johns_excited_voice`

## Need Help?

Check the full README.md for detailed documentation!
