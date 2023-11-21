import os
import sys
from dotenv import load_dotenv
from rev_ai import apiclient, JobStatus

# Get the API key
load_dotenv()
api_key = os.environ.get("API_KEY")

# create your client
client = apiclient.RevAiAPIClient(api_key)

import json

def convert_transcript_to_json(input_path: str, output_path: str) -> None:
    data = []

    # Input text structure
    with open(input_path, 'r') as input_file:
        input_text = input_file.read()

    # Split the input text into lines
    lines = input_text.strip().split('\n')

    # Process each line and create the JSON structure
    stringBuilder = ""
    for line in lines:
        if(line == ""):
            # Appends lines in a dialogue
            cleaned_string = ' '.join(stringBuilder.split())

            # Split the cleaned string into filename and text
            filename, text = cleaned_string.split(':', 1)

            # Remove trailing spaces from text
            text = text.strip()

            # Create a dictionary for the current dialogue
            dialogue = {"filename": filename, "text": text}

            # Add the dialogue dictionary to the data list
            data.append(dialogue)

            # Reset the string builder
            stringBuilder = ""
        else:
            stringBuilder += line + '\n'

    # Convert the data list to a JSON string
    json_data = json.dumps(data, indent=2)

    # Save the JSON string to a file
    with open(output_path, 'w') as output_file:
        output_file.write(json_data)

# Function to process an audio file and get the job id
def process_audio_file(path: str) -> any:
    # send a local file
    job = client.submit_job_local_file(path)

    # check job status
    while(True):
        if(client.get_job_details(job.id).status != JobStatus.IN_PROGRESS):
            break

    # return the job id
    return job.id

if __name__ == "__main__":
    # Define the input folder from args when available
    input_folder = sys.argv[1] if len(sys.argv) >= 2 else 'input'
    filenames = os.listdir(input_folder)

    # Filter filenames to include only .txt files
    txt_filenames = [filename for filename in filenames if filename.endswith('.txt')]

    for txt_filename in txt_filenames:
        input_path = os.path.join(input_folder, txt_filename)
        output_path = os.path.join('build', os.path.splitext(txt_filename)[0] + '_output.json')
        convert_transcript_to_json(input_path, output_path)

    # Handle all of the input files
    for filename in filenames:
        # Use os.path.join to create the full path for each file
        path = os.path.join(input_folder, filename)
