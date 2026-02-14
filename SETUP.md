# Complete Setup Guide - Start to Finish

Follow this guide to get your Discord voice bot running from scratch!

---

## Part 1: Download the Bot Files

### Option A: Download from Claude
You already have all the files! Just extract them to a folder like:
- `C:\Users\YourName\discord-bot\` (Windows)
- `/Users/YourName/discord-bot/` (Mac)
- `/home/yourname/discord-bot/` (Linux)

### Option B: From GitHub (if you uploaded them)
```bash
git clone https://github.com/YOUR_USERNAME/your-repo-name.git
cd your-repo-name
```

---

## Part 2: Create Your Discord Bot

### Step 1: Go to Discord Developer Portal
1. Open: https://discord.com/developers/applications
2. Log in with your Discord account

### Step 2: Create Application
1. Click **"New Application"** (top right)
2. Name it (e.g., "Voice Recorder Bot")
3. Click **"Create"**

### Step 3: Create Bot User
1. Click **"Bot"** in left sidebar
2. Click **"Add Bot"** → **"Yes, do it!"**
3. Under "Token" section, click **"Reset Token"** → **"Yes, do it!"**
4. Click **"Copy"** to copy your bot token
5. **⚠️ SAVE THIS TOKEN SOMEWHERE SAFE!** You'll need it in a moment

### Step 4: Enable Intents (IMPORTANT!)
Still on the Bot page, scroll down to **"Privileged Gateway Intents"**:

✅ Check these boxes:
- ✅ **Presence Intent**
- ✅ **Server Members Intent**  
- ✅ **Message Content Intent**

Click **"Save Changes"** at the bottom!

### Step 5: Invite Bot to Your Server
1. Click **"OAuth2"** in left sidebar
2. Click **"URL Generator"**
3. Under **"Scopes"**, check:
   - ✅ `bot`
   - ✅ `applications.commands`
4. Under **"Bot Permissions"**, check:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
5. Scroll down and **copy the generated URL**
6. Paste URL in your browser and select your server
7. Click **"Authorize"**

Your bot should now appear **offline** in your Discord server!

---

## Part 3: Install Requirements

### Install Python
1. Go to https://python.org/downloads/
2. Download Python 3.11 or newer
3. **⚠️ IMPORTANT**: Check "Add Python to PATH" during installation!
4. Verify installation:
```bash
python --version
# Should show: Python 3.11.x or higher
```

### Install FFmpeg (Required for Audio)

**Windows:**
1. Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`
   - Click OK
4. **Restart Command Prompt** and test:
```bash
ffmpeg -version
```

**Mac:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Verify
ffmpeg -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

---

## Part 4: Create .env File

### Step 1: Open Your Bot Folder
Navigate to where you saved the bot files.

### Step 2: Create .env File

**Windows (Easy Way):**
1. Open Notepad
2. Paste this (replace with YOUR token):
```
DISCORD_BOT_TOKEN=paste_your_actual_token_here
```
3. Save As: `.env` (with the dot!)
4. Change "Save as type" to **"All Files"**
5. Save in your bot folder

**Mac/Linux:**
```bash
cd /path/to/your/bot/folder
nano .env
```
Paste this (replace with YOUR token):
```
DISCORD_BOT_TOKEN=paste_your_actual_token_here
```
Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 3: Verify .env File

Your .env file should look EXACTLY like this:
```
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAuAbCdEf.GhIjKlMnOpQrStUvWxYz1234567890
```

**⚠️ Common Mistakes:**
- ❌ Extra spaces: `DISCORD_BOT_TOKEN = your_token` (WRONG)
- ❌ Quotes: `DISCORD_BOT_TOKEN="your_token"` (WRONG)
- ✅ Correct: `DISCORD_BOT_TOKEN=your_token` (RIGHT!)

---

## Part 5: Install Python Packages

Open terminal/command prompt in your bot folder:

**Windows:**
1. Hold Shift + Right-click in bot folder
2. Click "Open PowerShell window here"

**Mac/Linux:**
```bash
cd /path/to/your/bot/folder
```

**Then run:**
```bash
# Install packages
pip install -r requirements.txt

# This will install:
# - discord.py (Discord API)
# - PyNaCl (Voice support)
# - pydub (Audio processing)
# - gTTS (Text-to-speech)
# - and more...
```

Wait 1-2 minutes for installation to complete.

---

## Part 6: Run the Bot!

### Start the Bot

```bash
python bot.py
```

### What You Should See

```
<Your Bot Name> has connected to Discord!
Synced 9 command(s)
```

### Check Discord
Your bot should now show as **🟢 Online** in your server!

---

## Part 7: Test the Bot

### Join a Voice Channel
Go to Discord and join any voice channel in your server.

### Test Commands

1. **Make bot join:**
```
/vc
```
Bot should join your voice channel!

2. **Record someone:**
```
/record @YourFriend
```
(Have them talk for 10-15 seconds)

3. **Stop recording:**
```
/stop
```

4. **Play recording:**
```
/play
```

5. **Save voice:**
```
/save my_voice
```

6. **Use text-to-speech:**
```
/texttospeech my_voice Hello, this is a test!
```

---

## Troubleshooting

### Bot Won't Start

**Error: "DISCORD_BOT_TOKEN not found"**
- Check that `.env` file exists in bot folder
- Verify file is named `.env` (not `.env.txt`)
- Check token has no spaces or quotes

**Error: "Improper token"**
- Go back to Discord Developer Portal
- Reset token and get a new one
- Update `.env` file with new token

**Error: "No module named 'discord'"**
```bash
pip install discord.py[voice]
```

### Bot Joins But Won't Record

**Make sure:**
- You enabled all 3 intents in Developer Portal
- Bot has "Connect" and "Speak" permissions
- The person you're recording is unmuted
- FFmpeg is installed correctly: `ffmpeg -version`

### Commands Don't Appear

1. Wait 5 minutes (Discord caches commands)
2. Restart Discord app
3. Try in a different server
4. Check bot has "applications.commands" scope

### FFmpeg Not Found

**Windows:**
```bash
# Check if in PATH
where ffmpeg

# If not found, add C:\ffmpeg\bin to PATH
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

---

## Your Setup Checklist

Before running bot:
- [ ] Python 3.11+ installed
- [ ] FFmpeg installed and working
- [ ] All files in one folder
- [ ] `.env` file created with your token
- [ ] Bot created in Discord Developer Portal
- [ ] All 3 intents enabled
- [ ] Bot invited to your server
- [ ] Packages installed: `pip install -r requirements.txt`

Ready to run:
- [ ] Open terminal in bot folder
- [ ] Run: `python bot.py`
- [ ] Bot shows online in Discord
- [ ] Commands work: `/vc`, `/record`, etc.

---

## What's Next?

### Run 24/7 on Railway
See **RAILWAY.md** for deploying to cloud hosting.

### Improve Voice Quality
Install better TTS:
```bash
pip install TTS torch torchaudio
```

### Customize Settings
Edit `audio_processor.py` to change silence detection sensitivity.

---

## Need Help?

1. Check the error message carefully
2. Google the exact error
3. Review this guide step-by-step
4. Check Discord Developer Portal settings
5. Verify `.env` file format

## Quick Command Reference

```bash
# Check Python
python --version

# Check FFmpeg  
ffmpeg -version

# Install packages
pip install -r requirements.txt

# Run bot
python bot.py

# Stop bot
Ctrl+C
```

---

## Important Notes

⚠️ **Security:**
- NEVER share your bot token
- NEVER commit .env to GitHub
- Keep your token private

✅ **Best Practices:**
- Ask permission before recording
- Test in a private server first
- Monitor bot for errors
- Keep dependencies updated

---

You're all set! Run `python bot.py` and start using your voice bot! 🎉
