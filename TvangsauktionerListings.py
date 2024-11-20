import requests
from bs4 import BeautifulSoup
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Constants
URL = 'https://www.boligsiden.dk/tvangsauktioner/kommune/kolding'
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
RECIPIENT_EMAIL = 'simon-thiesen@hotmail.com'

def get_listings():
    """Fetch current listings from the website."""
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Adjust to the actual structure of the website
    listings = soup.find_all('div', class_='card__info')
    return {listing.text.strip() for listing in listings}

def send_email(subject, body, recipient):
    """Send an email using SendGrid."""
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email='simon-thiesen@hotmail.com',
        to_emails=recipient,
        subject=subject,
        plain_text_content=body
    )
    response = sg.send(message)
    print("Email sent with status:", response.status_code)

def main():
    # Load previous listings from environment variable
    previous_listings = set(os.getenv('PREVIOUS_LISTINGS', '').split(','))
    print("Previous Listings:", previous_listings)

    # Fetch current listings
    current_listings = get_listings()
    print("Current Listings:", current_listings)

    # Determine new listings
    new_listings = current_listings - previous_listings
    print("New Listings:", new_listings)

    # If there are new listings, send an email
    if new_listings:
        subject = "New Tvangsauktion Listings in Kolding"
        body = "The following new listings have been added:\n\n" + "\n".join(new_listings)
        send_email(subject, body, RECIPIENT_EMAIL)
        print("Email sent for new listings.")

    # Print current listings for GitHub Actions to pass to the next run
    print(f"::set-output name=current_listings::{','.join(current_listings)}")

if __name__ == "__main__":
    main()
