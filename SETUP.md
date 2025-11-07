# Quick Start Guide

## Initial Setup

### 1. Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID
1. Start a chat with your bot or add it to a group
2. Send any message to the bot
3. Visit in your browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find the `"chat":{"id":...}` value
5. Copy the ID (will be negative for groups, e.g., `-1001234567890`)

### 3. Set Up GitHub Actions
1. Push this repository to GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID` = your chat ID

### 4. Test It
1. Go to **Actions** tab
2. Select **Daily Tvangsauktioner Scraper**
3. Click **Run workflow** → **Run workflow**

Done! The script will now run automatically every day at 07:00 UTC.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env with your credentials
# Then run:
python TvangsauktionerListings.py
```

## Scheduling Locally (Optional)

If you prefer to run on your own machine instead of GitHub Actions:

```bash
crontab -e
```

Add this line (adjust path):
```
0 8 * * * cd /Users/simon.thiesen/Repos/TvangsauktionerListings && /Users/simon.thiesen/Repos/TvangsauktionerListings/.venv/bin/python TvangsauktionerListings.py >> scraper.log 2>&1
```
