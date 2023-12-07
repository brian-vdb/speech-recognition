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

# Function to map value allignments using the levenshtein distance matrix
def map_aligning_values(ld: np.ndarray[float, float]) -> list[int]:
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

# Function to append none for missing values
def add_none_for_missing(result_array: list[str], target_size: int) -> list[str]:
    # Append None values for insertions
    while len(result_array) < target_size:
        result_array.append(None)
    return result_array

# Function to align two word arrays with an alignment array based on the levenshtein distance
def align_word_arrays(value_alignments: list[int], transcript_words: list[str], audio_words: list[str]) -> tuple[list[str], list[str]]:
    # Arrays Indices
    transcript_index = 0
    audio_index = 0
    result_index = 0

    # Result Arrays
    aligned_transcript = []
    aligned_audio = []

    # Loop through the correct allignments
    for i, allignment in enumerate(value_alignments):
        # Skips to the next iteration
        if allignment == None:
            continue
        
        # Find errors in the transcript array
        transcript_errors = 0
        while transcript_index < i:
            # Keep track of errors for result allignment
            transcript_errors += 1

            # Append the error incrementing the result index
            aligned_transcript.append(transcript_words[transcript_index])
            transcript_index += 1
            result_index += 1

        # Find errors in the audio array
        while audio_index < allignment:
            # Append the error
            aligned_audio.append(audio_words[audio_index])
            audio_index += 1

            # Only start increasing the result index after matching the transcript errors
            if transcript_errors > 0:
                transcript_errors -= 1
            else:
                result_index += 1

        # Append None values for missing values
        aligned_transcript = add_none_for_missing(aligned_transcript, result_index)
        aligned_audio = add_none_for_missing(aligned_audio, result_index)

        # Append the correctly alligned words
        aligned_transcript.append(transcript_words[transcript_index])
        aligned_audio.append(audio_words[audio_index])

        # increment the indices for each correct allignment
        transcript_index += 1
        audio_index += 1
        result_index += 1
    
    # Find trailing errors for the transcript words
    transcript_errors = 0
    while transcript_index < len(transcript_words):
        # Keep track of errors for result allignment
        transcript_errors += 1

        # Append the error incrementing the result index
        aligned_transcript.append(transcript_words[transcript_index])
        transcript_index += 1
        result_index += 1

    # Find trailing errors for the audio words
    while audio_index < len(audio_words):
        # Append the error
        aligned_audio.append(audio_words[audio_index])
        audio_index += 1

        # Only start increasing the result index after matching the transcript errors
        if transcript_errors > 0:
            transcript_errors -= 1
        else:
            result_index += 1
    
    # Append None values for missing values
    aligned_transcript = add_none_for_missing(aligned_transcript, result_index)
    aligned_audio = add_none_for_missing(aligned_audio, result_index)

    return aligned_transcript, aligned_audio

# Function to analyze aligned text
def analyze_aligned_texts(reference: list[str], recognized: list[str]) -> tuple[int, int, int, int]:
    substitutions = 0
    deletions = 0
    insertions = 0
    corrects = 0

    # Loop through the aligned arrays to detect cases
    for i, value in enumerate(reference):
        if value == None:
            insertions += 1
        elif recognized[i] == None:
            deletions += 1
        elif value == recognized[i]:
            corrects += 1
        else:
            substitutions += 1

    return substitutions, deletions, insertions, corrects

# Function to calculate the Word Error Rate
def calc_wer(S: int, D: int, I: int, N: int) -> float:
    return (S + D + I) / N

# Function to calculate the Word Recognition Rate
def calc_wrr(S: int, D: int, I: int, N: int) -> float:
    return ((N - (S + D)) - I) / N

def calc_wcr(C: int, N: int) -> float:
    return C / N

# Function to compare matching texts according to filenames
def compare_texts(transcript_text: str, audio_text: str) -> None:
    # Preprocess the text strings to normalized word arrays
    transcript_words = preprocess_text(transcript_text)
    audio_words = preprocess_text(audio_text)

    # Get the levenshtein distance
    ld = levenshtein_distance(transcript_words, audio_words)

    # Allign the words in the levenshtein distance array
    value_alignments = map_aligning_values(ld)

    # Allign the two word arrays
    aligned_transcript, aligned_audio = align_word_arrays(value_alignments, transcript_words, audio_words)

    # Get all of the information needed to calculate errors for audio recognition
    S, D, I, C = analyze_aligned_texts(aligned_transcript, aligned_audio)
    N = len(aligned_transcript)

    # Get the WER
    WER = calc_wer(S, D, I, N)
    print(f'WER: {WER}')

    # Get the WRR
    WRR = calc_wrr(S, D, I, N)
    print(f'WRR {WRR}')

    # Get the WCR
    WCR = calc_wcr(C, N)
    print(f'WCR {WCR}')

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
