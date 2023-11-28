import json
import numpy as np
import string
from typing import List, Dict, Any

# Function to load in a json file
def load_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to create a mapping from json data
def create_mapping(data: List[Dict[str, str]]) -> Dict[str, str]:
    return {item['filename']: item['text'] for item in data}

# Removes punctuation and converts to lowercase
def preprocess_text(text: str) -> list[str]:
    text_without_punctuation = text.translate(str.maketrans('', '', string.punctuation))
    text_lowercase =  text_without_punctuation.lower()
    return text_lowercase.split()

# Calculates the levenshtein distance matrix
def levenshtein_distance(ref_words: list[str], hyp_words: list[str]) -> np.ndarray[float, float]:
    # Initialize a matrix with size |ref_words|+1 x |hyp_words|+1
    # The extra row and column are for the case when one of the strings is empty
    ld = np.zeros((len(ref_words) + 1, len(hyp_words) + 1))

    # Base cases: number of operations for an empty hypothesis/reference
    ld[:, 0] = np.arange(len(ref_words) + 1)
    ld[0, :] = np.arange(len(hyp_words) + 1)

    # Iterate over the words in the reference and hypothesis
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            # If the current words are the same, no operation is needed
            if ref_words[i - 1] == hyp_words[j - 1]:
                ld[i, j] = ld[i - 1, j - 1]
            else:
                # If the words are different, consider three operations:
                # substitution, insertion, and deletion, take the minimum
                ld[i, j] = min(ld[i - 1, j - 1] + 1, ld[i, j - 1] + 1, ld[i - 1, j] + 1)

    return ld

# Function to find correct allignments using the levenshtein distance matrix
def find_aligning_values(ld: np.ndarray[float, float]) -> list[int]:
    # Create an array of the same length as ld and initialize it as None
    value_alignments = [None] * (len(ld) - 1)

    # Go through the entire array and find instances where words match
    for i in range(1, len(ld)):
        minimum = min(ld[i])
        for j in range(len(ld[i])):
            value = ld[i, j]

            # Only process important values
            if value == minimum:
                # Get the surrounding check tiles
                lowest_surrounding = min(ld[i - 1, j - 1], ld[i, j - 1], ld[i - 1, j])

                # Check if all the conditions meet for a matching value
                if value == ld[i - 1, j - 1] and value == lowest_surrounding:
                    value_alignments[i - 1] = j - 1
    
    return value_alignments

# Function to compare matching texts according to filenames
def compare_texts(transcript_text: str, audio_text: str) -> None:
    # Preprocess the text strings to normalized word arrays
    transcript_words = preprocess_text(transcript_text)
    audio_words = preprocess_text(audio_text)

    # Log the word arrays for debugging
    print(f'Transcript Words: [range=0-{len(transcript_words) - 1}]')
    print(f'{transcript_words}\n')
    print(f'Audio Words: [range=0-{len(audio_words) - 1}]')
    print(f'{audio_words}\n')


    # Get the levenshtein distance
    ld = levenshtein_distance(transcript_words, audio_words)

    # Allign the words in the levenshtein distance array
    value_alignments = find_aligning_values(ld)

    # Log the allignments for debugging
    print(f'Mapping of word allignments from transcript to audio:')
    print(f'{value_alignments}')

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

    # Loop through each of the transcript entries
    for transcript_entry in transcript_data:
        filename = transcript_entry['filename']
        transcript_text = transcript_entry['text']

        # Fetch an audio text with matching filenames
        if filename in audio_mapping:
            audio_text = audio_mapping[filename]

            # compare the transcript and audio text
            compare_texts(transcript_text, audio_text)
        else:
            print(f"No matching entry in audio data for filename: {filename}\n")

if __name__ == "__main__":
    main()
