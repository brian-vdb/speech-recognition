import os
import sys
from dotenv import load_dotenv
from rev_ai import apiclient, JobStatus

# Get the API key
load_dotenv()
api_key = os.environ.get("API_KEY")

# create your client
client = apiclient.RevAiAPIClient(api_key)

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

    # Handle all of the input files
    filenames = os.listdir(input_folder)
    for filename in filenames:
        # Use os.path.join to create the full path for each file
        path = os.path.join(input_folder, filename)
