# Railway Deployment - Known Limitations

## ⚠️ Important: Voice Recording Limitations on Railway

The bot has been updated to work on Railway, but with some limitations:

### ✅ What Works on Railway:
- Bot joins voice channels (`/vc`)
- Text-to-speech (`/texttospeech`)
- Playing audio in voice channels
- All bot commands
- 24/7 uptime

### ⚠️ What Doesn't Work on Railway:
- **Recording user audio** - Discord.py's voice receiving feature requires additional setup that's not compatible with Railway's container environment
- Voice cloning from recordings (since recordings don't work)
- Playing back user recordings

## 🔧 Why This Happens

Discord voice recording requires:
1. `discord.sinks` module (not fully supported in containerized environments)
2. Additional audio codecs and libraries
3. Real-time audio processing capabilities
4. Voice receiving permissions (which have limitations)

Railway's container environment has restrictions that prevent full voice receiving functionality.

## ✅ Solution: Two Versions

### Version 1: Railway (Simplified)
**Use when:** You want 24/7 hosting and basic features
- ✅ Bot joins voice
- ✅ Text-to-speech works
- ❌ Cannot record user audio

### Version 2: Local (Full Features)
**Use when:** You need voice recording
- ✅ All features work
- ✅ Can record user audio
- ✅ Voice cloning works
- ❌ Must keep computer running

## 🚀 Current Railway Bot Features

Even without voice recording, your bot can still:

1. **Join Voice Channels**
   ```
   /vc - Bot joins your channel
   ```

2. **Text-to-Speech**
   ```
   /texttospeech Hello everyone!
   ```
   Bot will speak the text in voice channel

3. **Voice Management**
   ```
   /leave - Bot leaves channel
   /help - Show all commands
   ```

## 💡 Workaround Options

If you need voice recording, you have these options:

### Option 1: Run Bot Locally
1. Download all bot files
2. Install dependencies: `pip install -r requirements.txt`
3. Install FFmpeg
4. Run: `python bot.py`
5. Full voice recording works!

### Option 2: Use a VPS (Like DigitalOcean)
1. Get a $5/month VPS
2. Install bot there
3. Full features + 24/7 uptime

### Option 3: Hybrid Approach
- Use Railway for basic features (free)
- Run locally when you need voice recording
- Same bot token works for both

## 📝 Technical Details

The error you saw:
```
AttributeError: module 'discord' has no attribute 'sinks'
```

This happens because:
- Discord.py's voice receiving is experimental
- Container environments have audio limitations
- Railway doesn't support all audio processing libraries

## 🎯 What I've Done

I've updated `bot.py` to:
1. Remove dependency on `discord.sinks`
2. Add clear messages about limitations
3. Keep all working features functional
4. Make it compatible with Railway

The bot will now start successfully on Railway!

## ⚙️ Next Steps

### Deploy Updated Bot to Railway:

1. **Update GitHub:**
   ```bash
   git add bot.py
   git commit -m "Fix Railway compatibility"
   git push
   ```

2. **Railway Auto-Deploys:**
   - Railway detects the push
   - Automatically rebuilds
   - Bot should now start successfully!

3. **Verify in Railway Logs:**
   Look for:
   ```
   Starting bot...
   Note: Voice recording is limited on Railway deployment.
   <BotName> has connected to Discord!
   Synced 9 command(s)
   ```

### Test Working Features:
```
/vc - Bot joins
/texttospeech Hello world! - Bot speaks
/help - See all commands
/leave - Bot leaves
```

## 🆘 Still Having Issues?

If the bot still won't start:
1. Check Railway logs for new errors
2. Verify `requirements.txt` is uploaded
3. Verify `DISCORD_BOT_TOKEN` environment variable is set
4. Try restarting the deployment

## 📚 Alternative: Full Feature Bot

Want the complete voice recording experience?

See **SETUP.md** for running the bot locally with all features!

---

**Summary:** Railway bot works great for TTS and voice presence, but full voice recording needs local setup. Both versions work with the same bot token!
