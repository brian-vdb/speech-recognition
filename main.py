import os
import sys
from dotenv import load_dotenv
from rev_ai import apiclient

# Get the API key
load_dotenv()
api_key = os.environ.get("API_KEY")

# create your client
client = apiclient.RevAiAPIClient(api_key)

# Define the input folder from args when available
input_folder = sys.argv[1] if len(sys.argv) >= 2 else 'input'

# Handle all of the input files
filenames = os.listdir(input_folder)
for filename in filenames:
    print(filenames)