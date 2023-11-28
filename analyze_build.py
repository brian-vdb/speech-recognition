import json

# Path to the transcript json file
transcript_file_path = 'build/transcript_output.json'

# Open the file in read mode
with open(transcript_file_path, 'r') as file:
    # Load the JSON data from the file
    transcript_data = json.load(file)

# Path to the audio json file
audio_file_path = 'build/audio_output.json'

# Open the file in read mode
with open(audio_file_path, 'r') as file:
    # Load the JSON data from the file
    audio_data = json.load(file)

# Create a dictionary to store 'filename' -> 'text' mapping for the audio data
audio_mapping = {item['filename']: item['text'] for item in audio_data}

# Iterate through the transcript data
for transcript_entry in transcript_data:
    filename = transcript_entry['filename']
    transcript_text = transcript_entry['text']

    # Check if the filename exists in the audio mapping
    if filename in audio_mapping:
        audio_text = audio_mapping[filename]

        # Handle the text from the instances of the same filename
        print(f'{transcript_text}\n')
        print(f'{audio_text}')
