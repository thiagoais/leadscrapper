import requests
import csv
from bs4 import BeautifulSoup
import urllib.parse
import time

API_KEY = 'YOUR_API_KEY'
headers = {'Authorization': f'Bearer {API_KEY}'}
url = 'https://api.yelp.com/v3/businesses/search'
search_term = 'barber'

params = {
    'location': 'Cork',  # Change to your location
    'term': search_term,   # Or any type of business
    'limit': 50,             # Number of results
    'offset': 0              # Pagination support
}

response = requests.get(url, headers=headers, params=params)
businesses = response.json().get('businesses', [])

def extract_website_link(yelp_redirect_url):
    # Parse the URL to extract query parameters
    parsed_url = urllib.parse.urlparse(yelp_redirect_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # Get the 'url' parameter and decode it
    website_link = query_params.get('url', [None])[0]
    if website_link:
        # Decode URL encoding (e.g., %3A becomes :)
        website_link = urllib.parse.unquote(website_link)
        return website_link
    return 'N/A'  # Return 'N/A' if no valid link is found

# Function to scrape the website from the Yelp business page
def scrape_website(yelp_url, max_retries=10, delay=2):
    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(yelp_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the paragraph or tag that contains "Business Website"
            business_website_section = soup.find(string="Business website")

            if business_website_section:
                # Find the next <a> tag after "Business Website"
                website_link = business_website_section.find_next('a')
                if website_link and 'href' in website_link.attrs:
                    return extract_website_link(website_link['href'].strip())  # Return the link if found

            return 'N/A'
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Attempt {attempts}: {e}")
            time.sleep(delay)
            delay = 2  # Exponentially increase the delay
            if attempts == max_retries:
                print("Max retries reached. Returning 'N/A'.")
                return 'Conn. Error'
        except Exception as e:
            attempts += 1
            print(f"Error on attempt {attempts}: {e}")
            time.sleep(delay)  # Wait before retrying
            if attempts == max_retries:
                print("Max retries reached. Returning 'N/A'.")
                return 'Conn. Error'


# Specify the CSV file name
csv_file = 'yelp_businesses_' + search_term + '.csv'

# Create and write to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write header row with all relevant fields
    writer.writerow([
        'Name', 'ID', 'Website', 'Alias', 'URL', 'Phone', 'Price', 'Rating',
        'Review Count', 'Is Closed', 'Address', 'City', 'State',
        'Zip Code', 'Country', 'Latitude', 'Longitude'
    ])

    # Write business data to CSV
    count = 1
    for business in businesses:
        # Extracting relevant fields from the API response
        name = business.get('name')
        business_id = business.get('id')
        alias = business.get('alias')
        url = business.get('url')
        yelp_url = business.get('url')
        phone = business.get('display_phone')
        price = business.get('price', 'N/A')
        rating = business.get('rating')
        review_count = business.get('review_count')
        is_closed = business.get('is_closed')
        address = ', '.join(business['location'].get('display_address', []))
        city = business['location'].get('city')
        state = business['location'].get('state')
        zip_code = business['location'].get('zip_code')
        country = business['location'].get('country')
        latitude = business['coordinates']['latitude']
        longitude = business['coordinates']['longitude']

        # Scrape the business website from the Yelp page
        clean_url = url.replace("'", "").strip() #clean the url
        website = scrape_website(clean_url)

        # Write the row with the business data
        writer.writerow([
            name, business_id, website, alias, url, phone, price, rating,
            review_count, is_closed, address, city, state, zip_code,
            country, latitude, longitude
        ])
        print(count, " - Lead Gathered: ", name)
        count += 1

print(f"Data saved to {csv_file}")
