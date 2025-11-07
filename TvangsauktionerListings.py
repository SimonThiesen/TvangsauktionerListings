"""Script to fetch forced auction (tvangsauktion) listings for Kolding and
notify via Slack and Telegram if new listings appear.

Persistence: stores seen listing IDs/URLs in a local JSON file.
Configuration: environment variables (can be loaded via a .env file).

Environment variables used:
  SLACK_WEBHOOK_URL   - Incoming webhook URL for Slack (optional)
  TELEGRAM_BOT_TOKEN  - Telegram bot token (optional)
  TELEGRAM_CHAT_ID    - Telegram chat/group ID (optional)
  USER_AGENT          - Override default User-Agent header (optional)

If neither Slack nor Telegram config is provided, script will just print new listings.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Set, List, Tuple

import requests
from bs4 import BeautifulSoup
try:  # optional; if python-dotenv installed
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Constants
BASE_URL = 'https://www.boligsiden.dk'
LISTINGS_URL = f'{BASE_URL}/tvangsauktioner/kommune/kolding'
SEEN_FILE = 'seen_listings.json'
REQUEST_TIMEOUT = 20
HEADERS = {
    'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (compatible; ListingsBot/1.0; +https://github.com/SimonThiesen/TvangsauktionerListings)')
}

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


@dataclass(frozen=True)
class Listing:
    id: str      # unique identifier (slug or numeric id)
    title: str   # display title
    url: str     # absolute URL to listing

    def serialize(self) -> dict:
        return {'id': self.id, 'title': self.title, 'url': self.url}


def fetch_html(url: str) -> str:
    """Fetch HTML content with basic retry logic."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"Fetch attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url} after 3 attempts")


def parse_listings(html: str) -> List[Listing]:
    """Parse listing entries from page HTML.

    NOTE: This relies on current structure; may need adjustment if site changes.
    We look for anchor tags inside article/card containers that represent listings.
    """
    soup = BeautifulSoup(html, 'html.parser')

    listings: List[Listing] = []
    # Heuristic selectors - adjust if necessary:
    # Example pattern: <a class="card" href="/tvangsauktioner/bolig/..."> ... </a>
    for a in soup.select('a.card, a[data-test="card"], div.card__content a'):
        href = a.get('href') or ''
        title = ' '.join(a.get_text(strip=True).split())
        if not href or not title:
            continue
        # Normalize URL & ID
        if href.startswith('/'):
            full_url = BASE_URL + href
        else:
            full_url = href
        # Derive ID from last path segment
        listing_id = full_url.rstrip('/').split('/')[-1]
        listings.append(Listing(id=listing_id, title=title, url=full_url))

    # Fallback selector if above yields nothing (site structure changed)
    if not listings:
        for div in soup.select('div.card__info'):
            title = ' '.join(div.get_text(strip=True).split())
            parent_link = div.find_parent('a')
            if not parent_link:
                continue
            href = parent_link.get('href') or ''
            if href.startswith('/'):
                full_url = BASE_URL + href
            else:
                full_url = href
            listing_id = full_url.rstrip('/').split('/')[-1]
            listings.append(Listing(id=listing_id, title=title, url=full_url))

    return listings


def load_seen() -> Set[str]:
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {item['id'] if isinstance(item, dict) else item for item in data}
    except Exception as e:
        print(f"Failed to load seen file: {e}")
        return set()


def save_seen(listings: List[Listing]) -> None:
    try:
        with open(SEEN_FILE, 'w', encoding='utf-8') as f:
            json.dump([l.serialize() for l in listings], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save seen listings: {e}")


def notify_slack(new_listings: List[Listing]) -> None:
    if not SLACK_WEBHOOK_URL:
        return
    text_lines = ["Nye tvangsauktioner i Kolding:"] + [f"• {l.title}\n{l.url}" for l in new_listings]
    payload = {"text": "\n".join(text_lines)}
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
        if resp.status_code >= 300:
            print(f"Slack notification failed: {resp.status_code} {resp.text}")
        else:
            print("Slack notification sent.")
    except Exception as e:
        print(f"Slack notification exception: {e}")


def notify_telegram(new_listings: List[Listing]) -> None:
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return
    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    text_lines = ["Nye tvangsauktioner i Kolding:"] + [f"• {l.title}\n{l.url}" for l in new_listings]
    message = "\n\n".join(text_lines)
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'disable_web_page_preview': True,
    }
    try:
        resp = requests.post(base, data=payload, timeout=15)
        if resp.status_code >= 300:
            print(f"Telegram notification failed: {resp.status_code} {resp.text}")
        else:
            print("Telegram notification sent.")
    except Exception as e:
        print(f"Telegram notification exception: {e}")


def diff_new_listings(all_listings: List[Listing], seen_ids: Set[str]) -> Tuple[List[Listing], List[Listing]]:
    new = [l for l in all_listings if l.id not in seen_ids]
    return new, all_listings


def main() -> None:
    print("Fetching listings page...")
    html = fetch_html(LISTINGS_URL)
    all_listings = parse_listings(html)
    print(f"Total listings found: {len(all_listings)}")

    seen_ids = load_seen()
    print(f"Previously seen count: {len(seen_ids)}")

    new_listings, full_set = diff_new_listings(all_listings, seen_ids)
    if new_listings:
        print(f"New listings detected: {len(new_listings)}")
        for l in new_listings:
            print(f"NEW: {l.title} -> {l.url}")
        notify_slack(new_listings)
        notify_telegram(new_listings)
        save_seen(full_set)  # persist full current set
    else:
        print("No new listings today.")

    # For CI observability
    print(f"CURRENT_IDS={','.join(l.id for l in all_listings)}")


if __name__ == '__main__':
    main()
