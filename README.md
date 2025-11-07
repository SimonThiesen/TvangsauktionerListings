# TvangsauktionerListings

Automated daily scraper for forced auction (tvangsauktion) property listings in Kolding from Boligsiden. It detects new listings and sends notifications to Slack and/or Telegram.

## Features
* Scrapes listings from `https://www.boligsiden.dk/tvangsauktioner/kommune/kolding`
* Persists previously seen listings in `seen_listings.json`
* Sends a message to Slack via Incoming Webhook (optional)
* Sends a message to Telegram via bot (optional)
* Can be scheduled (cron locally or GitHub Actions)

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
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL (optional) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) |
| `TELEGRAM_CHAT_ID` | Telegram chat/group/channel ID (optional) |
| `USER_AGENT` | Override default User-Agent string (optional) |

If neither Slack nor Telegram variables are set, the script will just print new listings.

Example `.env` file:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=-1001234567890
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X) ListingsBot/1.0
```

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

## GitHub Actions (Optional)
Create `.github/workflows/daily.yml`:
```yaml
name: Daily Listings Check
on:
	schedule:
		- cron: '0 7 * * *'
	workflow_dispatch: {}
jobs:
	scrape:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-python@v5
				with:
					python-version: '3.11'
			- run: pip install -r requirements.txt
			- env:
					SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
					TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
					TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
				run: python TvangsauktionerListings.py
			- name: Upload seen file artifact
				uses: actions/upload-artifact@v4
				with:
					name: seen-listings
					path: seen_listings.json
```

You can persist `seen_listings.json` using artifacts or move to an external store if reliability is critical.

## Development Notes
* Scraping selectors may need adjustment if Boligsiden changes layout.
* Add retry/backoff & logging improvements for production use.
* Extend to additional municipalities by parameterizing the URL.

## License
MIT (if desired; currently unspecified).
