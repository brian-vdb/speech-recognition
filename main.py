import os
import sys
from dotenv import load_dotenv
from rev_ai import apiclient, JobStatus
import json
import time

# Get the API key
load_dotenv()
api_key = os.environ.get("API_KEY")

# create your client
client = apiclient.RevAiAPIClient(api_key)

# Function to save data in a json file
def save_data_as_json(output_path: str, data: list[dict[str, str]]) -> None:
    # Convert the data list to a JSON string
    json_data = json.dumps(data, indent=2)

    # Save the JSON string to a file
    with open(output_path, 'w') as output_file:
        output_file.write(json_data)

# Function to convert the transcript file to JSON
def convert_transcript_to_json(input_path: str, output_path: str) -> None:
    with open(input_path, 'r') as input_file:
        input_text = input_file.read()

    # Split the input text into lines
    lines = input_text.split('\n')

    # Process each line and create the JSON structure
    stringBuilder = ""
    data = []
    for line in lines:
        if(line == "" and stringBuilder != ""):
            try:
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
            except:
                print("Error: Unable save dialogue")
        else:
            stringBuilder += line + '\n'

    # Save the output in a .json file
    save_data_as_json(output_path, data)

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

# Function to extract and concatenate values labeled as 'text' and 'punct'
def get_text_from_json(json_data: any) -> str:
    result_string = ""
    for monologue in json_data['monologues']:
        for element in monologue['elements']:
            if element['type'] in ('text', 'punct'):
                result_string += element['value']
    return result_string

# Function to process a job by retrieving transcript JSON using the client and extracting relevant information.
def process_job(filename: str, job_id: any) -> dict[str, str]:
    # Retrieve transcript JSON for the given job_id using the client
    json = client.get_transcript_json(job_id)
    
    # Return a dictionary containing information for the current job, including the filename and extracted text
    return {"filename": filename, "text": get_text_from_json(json)}

if __name__ == "__main__":
    # Define the input folder from args when available
    input_folder = sys.argv[1] if len(sys.argv) >= 2 else 'input'
    filenames = os.listdir(input_folder)

    # Filter filenames to include only .txt files
    txt_filenames = [filename for filename in filenames if filename.endswith('.txt')]

    # Ensure the 'build' directory exists
    build_dir = 'build'
    os.makedirs(build_dir, exist_ok=True)

    # Clean the txt files
    for txt_filename in txt_filenames:
        input_path = os.path.join(input_folder, txt_filename)
        output_path = os.path.join('build', 'transcript_output.json')
        convert_transcript_to_json(input_path, output_path)
    
    # Filter for common media formats using FFmpeg
    media_formats = ['.m4a', '.mp1', '.mp2', '.mp3', '.wav', '.mp4', '.flac', '.rso', '.ape'] # Add more formats as needed
    audio_filenames = [filename for filename in filenames if any(filename.endswith(format) for format in media_formats)]

    # Handle all of the input files
    data = []
    for audio_filename in audio_filenames:
        # Use os.path.join to create the full path for each file
        path = os.path.join(input_folder, audio_filename)

        # Record the start time
        print(f'Start: [Processing {audio_filename}]')
        start_time = time.time()

        # process the audio
        job_id = process_audio_file(path)

        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time
        print(f'Successfully: [Processed {audio_filename} in {elapsed_time} sec]')
        print(job_id)
        
        # Get the dialogue dictionary
        print(f'Start: [Processing {audio_filename} Dialogue]')
        dialogue = process_job(audio_filename, job_id)
        print(f'Successfully: [Processing {audio_filename} Dialogue]')
        print(dialogue)

        # Append the dialogue to the data array
        data.append(dialogue)
    
    # Save the output in a .json file
    output_path = os.path.join('build', 'audio_output.json')
    save_data_as_json(output_path, data)
