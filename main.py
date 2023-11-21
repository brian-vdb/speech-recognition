import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

# Get the API key
api_key = os.environ.get("API_KEY")