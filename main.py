import os
from dotenv import load_dotenv
from rev_ai import apiclient

# Get the API key
load_dotenv()
api_key = os.environ.get("API_KEY")

# create your client
client = apiclient.RevAiAPIClient(api_key)
