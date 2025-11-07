# TvangsauktionerListings

Automated daily scraper for forced auction (tvangsauktion) property listings in Kolding from Boligsiden. It detects new listings and sends notifications via Telegram and/or Slack.

## Features
* Scrapes listings from `https://www.boligsiden.dk/tvangsauktioner/kommune/kolding`
* Persists previously seen listings in `seen_listings.json`
* Sends messages to Telegram via bot (optional)
* Sends messages to Slack via Incoming Webhook (optional)
* Can be scheduled (cron locally or GitHub Actions) to run once daily

## Requirements
Python 3.9+ recommended.

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Set environment variables (directly or via `.env` file):

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) |
| `TELEGRAM_CHAT_ID` | Telegram chat/group/channel ID (optional) |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL (optional) |
| `USER_AGENT` | Override default User-Agent string (optional) |

If neither Telegram nor Slack variables are set, the script will just print new listings.

Example `.env` file:
```
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=-1001234567890
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X) ListingsBot/1.0
```

### Setting up Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions to create your bot
3. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Start a chat with your bot or add it to a group
5. Send a message to the bot/group
6. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in your browser
7. Find the `chat` object in the response and copy the `id` value (this is your `TELEGRAM_CHAT_ID`)

For groups, the chat ID will be negative (e.g., `-1001234567890`).

### Setting up Slack Webhook (optional)

1. Go to https://api.slack.com/messaging/webhooks
2. Create an Incoming Webhook for your workspace and channel
3. Copy the webhook URL

## Running Manually
```bash
python TvangsauktionerListings.py
```

Output will indicate any newly discovered listings.

## Scheduling (Local Cron)
Edit your crontab:
```bash
crontab -e
```
Add (runs every day at 08:00):
```
0 8 * * * /usr/bin/env bash -c 'cd /path/to/TvangsauktionerListings && /usr/bin/env python TvangsauktionerListings.py >> scraper.log 2>&1'
```

## GitHub Actions (Automated Daily Run)
The repository includes a GitHub Actions workflow (`.github/workflows/daily-scraper.yml`) that runs automatically once per day at 07:00 UTC.

### Setup Instructions

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add tvangsauktioner scraper"
   git push origin main
   ```

2. **Configure GitHub Secrets:**
   - Go to your repository on GitHub
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret** and add:
     - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
     - `TELEGRAM_CHAT_ID` - Your Telegram chat/group ID
     - `SLACK_WEBHOOK_URL` - (Optional) Your Slack webhook URL

3. **Enable GitHub Actions:**
   - Go to the **Actions** tab in your repository
   - If prompted, enable workflows

4. **Manual Test Run:**
   - Go to **Actions** → **Daily Tvangsauktioner Scraper**
   - Click **Run workflow** → **Run workflow** to test immediately

### How It Works
- Runs automatically every day at 07:00 UTC (08:00 CET / 09:00 CEST)
- Downloads the previous `seen_listings.json` from artifacts
- Runs the scraper and sends notifications for new listings
- Uploads the updated `seen_listings.json` as an artifact for the next run
- Artifacts are retained for 90 days

### Note on Persistence
The workflow uses GitHub Actions artifacts to persist `seen_listings.json` between runs. Artifacts are automatically cleaned up after 90 days. For longer-term persistence, consider committing the file back to the repository or using external storage (S3, gist, etc.).## Development Notes
* Scraping selectors may need adjustment if Boligsiden changes layout.
* Add retry/backoff & logging improvements for production use.
* Extend to additional municipalities by parameterizing the URL.

## License
MIT (if desired; currently unspecified).
