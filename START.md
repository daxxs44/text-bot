# ⚡ Ultra Quick Start - One Page

## 🎯 Absolute Essentials

### 1. Get Bot Token (2 minutes)
1. https://discord.com/developers/applications → "New Application"
2. Bot tab → "Add Bot" → "Reset Token" → **Copy Token**
3. Enable all 3 intents (Presence, Server Members, Message Content)
4. OAuth2 → URL Generator → Check `bot` + `applications.commands`
5. Copy URL → Invite to server

### 2. Create .env File (30 seconds)
Create a file named `.env` in your bot folder:
```
DISCORD_BOT_TOKEN=paste_your_token_here
```
**No spaces, no quotes!**

### 3. Install & Run (2 minutes)
```bash
# Install Python 3.11+ from python.org
# Install FFmpeg (see SETUP.md for your OS)

# Then:
pip install -r requirements.txt
python bot.py
```

---

## 📋 Files You Need

Download these from Claude:
- `bot.py` - Main bot
- `audio_processor.py` - Audio processing
- `voice_cloner.py` - TTS
- `requirements.txt` - Dependencies
- `.env.example` - Template (rename to `.env`)

---

## 🎮 Commands

| Command | What it does |
|---------|-------------|
| `/vc` | Bot joins your voice channel |
| `/record @user` | Start recording someone |
| `/stop` | Stop recording |
| `/play` | Playback recording |
| `/save name` | Save voice for TTS |
| `/texttospeech name text` | Generate speech |
| `/delete` | Delete recording |
| `/leave` | Bot leaves channel |

---

## 🆘 Help!

**"Bot token not found"** → Check `.env` file exists and has no typos

**"FFmpeg not found"** → Install FFmpeg for your OS (see SETUP.md)

**"Commands don't show"** → Wait 5 min, restart Discord, check bot has `applications.commands` scope

**Need detailed help?** → Read **SETUP.md** for complete guide!

---

## 📖 Full Documentation

- **SETUP.md** - Complete setup from zero
- **ENV_GUIDE.md** - How to create .env file
- **RAILWAY.md** - Deploy to cloud (24/7 hosting)
- **README.md** - Full documentation

---

That's it! You're ready to go! 🚀
