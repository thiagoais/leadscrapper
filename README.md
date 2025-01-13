# leadscrapper
Applications to scrappe B2B customers online

## Running the Project with PyCharm

1. Clone the project folder
2. Create a virtual environment using Python:
python -m venv .venv
(or `python3 -m venv .venv` depending on your Python version)
3. Open the project in PyCharm
4. In PyCharm's terminal, install the required packages:
pip install -r requirements.txt

## API Key Configuration

The project requires API keys to function properly:

1. Both (Google and Yelp) scrappers need a corresponding API key to work
# Google
- Register with google and get a free maps-api key (https://console.cloud.google.com/google/maps-apis/credentials)

# Yelp
- Create an account on developer Yelp and get a free api-key (https://www.yelp.com/developers)

Replace `"YOUR_API_KEY"` with your actual API key before running.
