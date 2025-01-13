import requests
import time
import csv

quantity_per_page = 20

RADIUS = 10000
CORK_LOCATION = "51.8985,-8.4756"
AVILA_LOCATION = "40.656754043276564, -4.6810780884424705"
RESULTS_CSV_FILE = "google_places_results"
MAX_NUMBER_PAGES = 15

# Replace with your Google Places API key
API_KEY = 'your_api_key'

def get_places_data(query, location, radius, max_retries=3):
    print("Getting registers for ", query)
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "key": API_KEY,
    }

    all_results = []
    page_number = 0
    while page_number < MAX_NUMBER_PAGES:
        print("Retrieving registers from ", page_number * quantity_per_page, " to ", (page_number + 1) * quantity_per_page)
        page_number += 1
        attempts = 0
        while attempts < max_retries:
            try:
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "OK":
                    print(f"Error: {data.get('error_message', 'Unknown error')}")
                    return all_results

                # Append the current page of results
                all_results.extend(data.get("results", []))

                # Check for a next_page_token
                next_page_token = data.get("next_page_token")
                if not next_page_token:
                    return all_results

                # Set the next page token for the following request
                params["pagetoken"] = next_page_token
                time.sleep(2)  # Add a short delay to let the next page token activate

                break  # Exit retry loop if successful
            except requests.exceptions.RequestException as e:
                attempts += 1
                print(f"Request error on attempt {attempts}: {e}")
                time.sleep(2 * attempts)  # Exponential backoff
    return all_results

def get_place_details(place_id, max_retries=3):
    # Set up the base URL for the Places API details
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,website,formatted_phone_number,url,price_level,rating,user_ratings_total",
        "key": API_KEY,
    }

    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(details_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if data.get("status") != "OK":
                print(f"Error: {data.get('error_message', 'Unknown error')}")
                return {}

            return data.get("result", {})
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Request error on attempt {attempts}: {e}")
            time.sleep(2 * attempts)  # Exponential backoff
    return {}

def scrape_google_places(query, location=AVILA_LOCATION, radius=RADIUS):
    places_data = get_places_data(query, location, radius)
    business_details = []

    for place in places_data:
        place_id = place["place_id"]
        details = get_place_details(place_id)
        if details:
            business_details.append({
                "Name": details.get("name", "N/A"),
                "Address": details.get("formatted_address", "N/A"),
                "Phone": details.get("formatted_phone_number", "N/A"),
                "Website": details.get("website", "N/A"),
                "Url": details.get("url", "N/A"),
                "PriceLevel": details.get("price_level", "N/A"),
                "Rating": details.get("rating", "N/A"),
                "UserRatingsTotal": details.get("user_ratings_total", "N/A"),
            })

    return business_details

def save_to_csv(business_details, filename=RESULTS_CSV_FILE + ".csv"):
    # Save business details to CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Address", "Phone", "Website", "URL", "Url", "PriceLevel", "Rating", "UserRatingsTotal"])
        writer.writeheader()
        for business in business_details:
            writer.writerow(business)
    print(f"Data saved to {filename}")

# Example usage
query = ("barber")
business_details = scrape_google_places(query)
save_to_csv(business_details, RESULTS_CSV_FILE + "_" + query + ".csv")