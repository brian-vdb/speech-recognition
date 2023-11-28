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
def preprocess_text(text: str) -> str:
    text_without_punctuation = text.translate(str.maketrans('', '', string.punctuation))
    return text_without_punctuation.lower()

# Calculates the word error rate by comparing two strings
def calculate_wer(reference, hypothesis):
    # Split the reference and hypothesis sentences into words
    ref_words = reference.split()
    hyp_words = hypothesis.split()

    # Initialize a matrix with size |ref_words|+1 x |hyp_words|+1
    # The extra row and column are for the case when one of the strings is empty
    d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1))

    # The number of operations for an empty hypothesis to become the reference
    # is just the number of words in the reference (i.e., deleting all words)
    for i in range(len(ref_words) + 1):
        d[i, 0] = i

    # The number of operations for an empty reference to become the hypothesis
    # is just the number of words in the hypothesis (i.e., inserting all words)
    for j in range(len(hyp_words) + 1):
        d[0, j] = j

    # Iterate over the words in the reference and hypothesis
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            # If the current words are the same, no operation is needed
            # So we just take the previous minimum number of operations
            if ref_words[i - 1] == hyp_words[j - 1]:
                d[i, j] = d[i - 1, j - 1]
            else:
                # If the words are different, we consider three operations:
                # substitution, insertion, and deletion
                # And we take the minimum of these three possibilities
                substitution = d[i - 1, j - 1] + 1
                insertion = d[i, j - 1] + 1
                deletion = d[i - 1, j] + 1
                d[i, j] = min(substitution, insertion, deletion)

    # The minimum number of operations to transform the hypothesis into the reference
    # is in the bottom-right cell of the matrix
    # We divide this by the number of words in the reference to get the WER
    wer = d[len(ref_words), len(hyp_words)] / len(ref_words)
    return wer

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

            # Get the WER
            wer_value = calculate_wer(transcript_text, audio_text)
            print(f'The WER Value: {wer_value}')
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
