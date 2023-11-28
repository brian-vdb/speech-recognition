import json
from typing import List, Dict, Any

# Function to load in a json file
def load_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to create a mapping from json data
def create_mapping(data: List[Dict[str, str]]) -> Dict[str, str]:
    return {item['filename']: item['text'] for item in data}

# Function to compare matching texts according to filenames
def compare_matching_texts(transcript_data: List[Dict[str, str]], audio_mapping: Dict[str, str]) -> None:
    for transcript_entry in transcript_data:
        filename = transcript_entry['filename']
        transcript_text = transcript_entry['text']

        # Check if the filename exists in the audio mapping
        if filename in audio_mapping:
            audio_text = audio_mapping[filename]

            # Remove punctuation
            transcript_text = preprocess_text(transcript_text)
            audio_text = preprocess_text(audio_text)

            # Handle the text from the instances of the same filename
            print(f'{transcript_text}\n')
            print(f'{audio_text}\n')

            wer_value, substitution, insertion, deletion  = calculate_wer(transcript_text, audio_text)
            print(f'The WER Value: {wer_value}')
            print(f'Substituted: {substitution}')
            print(f'Inserted: {insertion}')
            print(f'Deleted: {deletion}')
        else:
            print(f"No matching entry in audio data for filename: {filename}\n")

def main() -> None:
    # Path to the transcript json file
    transcript_file_path = 'build/transcript_output.json'

    # Path to the audio json file
    audio_file_path = 'build/audio_output.json'

    # Load JSON data
    transcript_data = load_json(transcript_file_path)
    audio_data = load_json(audio_file_path)

    # Create a dictionary to store 'filename' -> 'text' mapping for the audio data
    audio_mapping = create_mapping(audio_data)

    # Print matching texts
    compare_matching_texts(transcript_data, audio_mapping)

if __name__ == "__main__":
    main()
