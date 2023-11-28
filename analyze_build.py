import json

# Function to load in a json file
def load_json(file_path: str) -> any:
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to create a mapping from json data
def create_mapping(data: any):
    return {item['filename']: item['text'] for item in data}

# Function to compare matching texts according to filenames
def compare_matching_texts(transcript_data, audio_mapping):
    for transcript_entry in transcript_data:
        filename = transcript_entry['filename']
        transcript_text = transcript_entry['text']

        # Check if the filename exists in the audio mapping
        if filename in audio_mapping:
            audio_text = audio_mapping[filename]

            # Handle the text from the instances of the same filename
            print(f'Transcript Text: {transcript_text}\n')
            print(f'Audio Text: {audio_text}\n')
        else:
            print(f"No matching entry in audio data for filename: {filename}\n")

def main():
    # Path to the transcript json file
    transcript_file_path = 'build/transcript_output.json'

    # Path to the audio json file
    audio_file_path = 'build/audio_output.json'

    # Load JSON data
    transcript_data = load_json(transcript_file_path)
    audio_data = load_json(audio_file_path)

    # Create a dictionary to store 'filename' -> 'text' mapping for the audio data
    audio_mapping = create_audio_mapping(audio_data)

    # Print matching texts
    compare_matching_texts(transcript_data, audio_mapping)

if __name__ == "__main__":
    main()
