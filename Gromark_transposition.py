import itertools
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from typing import List, Tuple, Dict
import multiprocessing
import numpy as np
import subprocess  # For running external scripts
import re
from collections import Counter

RED = '\033[38;5;88m'
YELLOW = '\033[38;5;3m'
GREY = '\033[38;5;238m'
RESET = '\033[0m'

def create_keyed_alphabet(keyword: str, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
    # Use the provided alphabet
    keyword = ''.join(dict.fromkeys(keyword.upper()))
    remaining = ''.join(c for c in alphabet if c not in keyword)
    base = keyword + remaining

    cols = len(keyword)
    rows = (len(base) + cols - 1) // cols
    block = [['' for _ in range(cols)] for _ in range(rows)]

    idx = 0
    for i in range(rows):
        for j in range(cols):
            if idx < len(base):
                block[i][j] = base[idx]
                idx += 1

    sorted_chars = sorted(keyword)
    order = []
    for char in keyword:
        order.append(sorted_chars.index(char) + 1)
        sorted_chars[sorted_chars.index(char)] = None

    col_order = [p[0] for p in sorted(enumerate(order), key=lambda x: x[1])]

    return ''.join(
        block[row][col]
        for col in col_order
        for row in range(rows)
        if row < len(block) and block[row][col]
    )


def batch_primers(start: int = 10000, end: int = 99999, batch_size: int = 1000) -> List[List[int]]:
    """Create optimized batches of primers"""
    all_primers = list(range(start, end + 1))
    return [all_primers[i:i + batch_size] for i in range(0, len(all_primers), batch_size)]

def generate_running_key(primer: str, length: int) -> str:
    """Generate running key using numpy for speed"""
    key = np.array([int(d) for d in primer], dtype=np.int8)
    result = np.zeros(length, dtype=np.int8)
    result[:len(key)] = key
    
    for i in range(len(key), length):
        result[i] = (result[i-5] + result[i-4]) % 10
        
    return ''.join(map(str, result))

def decrypt_gromark(ciphertext: str, mixed_alphabet: str, running_key: str, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
    result = []

    for i, char in enumerate(ciphertext):
        if char in mixed_alphabet and i < len(running_key):
            mixed_pos = mixed_alphabet.index(char)
            straight_letter = alphabet[mixed_pos] # Use provided alphabet
            shift = int(running_key[i])
            orig_pos = (alphabet.index(straight_letter) - shift) % len(alphabet) # Use len(alphabet) for modulo
            result.append(alphabet[orig_pos].lower()) # Use provided alphabet
        else:
            result.append(char.lower())

    return ''.join(result)

def try_decrypt_batch(args: Tuple) -> List[Dict]:
    keyword, primers, ciphertext, required_words, alphabet = args # Add alphabet
    results = []
    mixed_alphabet = create_keyed_alphabet(keyword, alphabet) # Pass alphabet

    for primer in primers:
        try:
            primer_str = str(primer)
            running_key = generate_running_key(primer_str, len(ciphertext))
            decrypted = decrypt_gromark(ciphertext, mixed_alphabet, running_key, alphabet) # Pass alphabet

            if all(can_form_word(word, decrypted) for word in required_words):
                results.append({
                    'keyword': keyword,
                    'primer': primer_str,
                    'running_key': running_key,
                    'decrypted': decrypted
                })

        except Exception:
            continue

    return results

def validate_keyword(keyword: str, known_segments: List[Tuple], alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> bool: # Add alphabet
    try:
        mixed_alphabet = create_keyed_alphabet(keyword, alphabet) # Pass alphabet
        
        for _, cipher_segment, plain_segment in known_segments:
            for c, p in zip(cipher_segment, plain_segment):
                mixed_pos = mixed_alphabet.index(c)
                straight_letter = alphabet[mixed_pos] # Use provided alphabet
                plain_pos = alphabet.index(p.upper()) # Use provided alphabet
                straight_pos = alphabet.index(straight_letter) # Use provided alphabet

                if (straight_pos - plain_pos) % len(alphabet) > 9: # Use len(alphabet) for modulo
                    return False

        return True

    except Exception:
        return False

def parallel_process_keywords(valid_keywords: List[str], ciphertext: str, required_words: List[str], alphabet: str, batch_size: int = 1000) -> List[Dict]: # Add alphabet
    all_results = []
    num_processes = max(1, os.cpu_count() - 1)
    primer_batches = batch_primers(batch_size=batch_size)

    total_batches = len(valid_keywords) * len(primer_batches)

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [
            executor.submit(try_decrypt_batch, (keyword, batch, ciphertext, required_words, alphabet)) # Add alphabet
            for keyword in valid_keywords
            for batch in primer_batches
        ]

        with tqdm(total=total_batches, desc="Processing batches",  colour="yellow") as pbar:
            for future in as_completed(futures):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    pbar.update(1)
                except Exception as e:
                    print(f"Batch processing error: {e}")
                    continue

    return all_results

def can_form_word(word: str, text: str) -> bool:
    """Checks if a word can be formed from a text, allowing interspersed characters."""
    word = word.upper()
    text = text.upper()
    word_ptr = 0
    for text_char in text:
        if word_ptr < len(word) and text_char == word[word_ptr]:
            word_ptr += 1
    return word_ptr == len(word)

def save_results_to_file(results: List[Dict], filename: str):
    """Saves the results to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:  # Use utf-8 encoding
            for result in results:
                f.write("-" * 50 + "\n")
                f.write(f"Keyword: {result['keyword']}\n")
                f.write(f"Primer: {result['primer']}\n")
                f.write(f"Running Key: {result['running_key']}\n")  # Added running key
                f.write(f"Decrypted: {result['decrypted']}\n")
                f.write("-" * 50 + "\n")
                f.write("\n")  # Add an extra newline for spacing

        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving results to file: {e}")

def analyze_frequency(text):
    """
    Analyze character frequency in the plaintext and display results.
    
    Args:
        text (str): The plaintext to analyze
    """
    print(f"\n{YELLOW}Frequency Analysis{RESET}")
    print(f"{GREY}-{RESET}" * 50)
    
    # Ensure text is uppercase for consistency
    text = text.upper()
    
    # Count letter frequencies
    letter_count = {}
    total_letters = 0
    
    for char in text:
        if char.isalpha():
            letter_count[char] = letter_count.get(char, 0) + 1
            total_letters += 1
    
    # Calculate frequencies and sort by frequency (descending)
    frequencies = [(char, count, count/total_letters*100) for char, count in letter_count.items()]
    frequencies.sort(key=lambda x: x[1], reverse=True)
    
    # Display results
    print(f"{'Character':<10}{'Count':<10}{'Frequency %':<15}{'Bar Chart'}")
    print(f"{GREY}-{RESET}" * 50)
    
    for char, count, percentage in frequencies:
        bar_length = int(percentage) * 2  # Scale for better visualization
        bar = "█" * bar_length
        print(f"{char:<10}{count:<10}{percentage:.2f}%{'':<10}{RED}{bar}{RESET}")
    
    # Add some statistical analysis
    print(f"{GREY}-{RESET}" * 50)
    print(f"Total letters analyzed: {YELLOW}{total_letters}{RESET}")
    
    # Compare with English language frequency
    english_freq = {
        'E': 12.02, 'T': 9.10, 'A': 8.12, 'O': 7.68, 'I': 7.31, 'N': 6.95,
        'S': 6.28, 'R': 6.02, 'H': 5.92, 'D': 4.32, 'L': 3.98, 'U': 2.88,
        'C': 2.71, 'M': 2.61, 'F': 2.30, 'Y': 2.11, 'W': 2.09, 'G': 2.03,
        'P': 1.82, 'B': 1.49, 'V': 1.11, 'K': 0.69, 'X': 0.17, 'Q': 0.11,
        'J': 0.10, 'Z': 0.07
    }
    
    # Calculate deviation from English frequency
    print(f"\n{YELLOW}Deviation from Standard English{RESET}")
    print(f"{'Character':<10}{'Text %':<15}{'English %':<15}{'Deviation'}")
    print(f"{GREY}-{RESET}" * 50)
    
    # Convert frequencies to a dict for easier lookup
    text_freq = {char: percentage for char, _, percentage in frequencies}
    
    for char in sorted(english_freq.keys()):
        text_percentage = text_freq.get(char, 0)
        eng_percentage = english_freq[char]
        deviation = text_percentage - eng_percentage
        
        # Highlight significant deviations
        if abs(deviation) > 3:
            color = RED
        elif abs(deviation) > 1.5:
            color = YELLOW
        else:
            color = RESET
            
        print(f"{char:<10}{text_percentage:.2f}%{'':<10}{eng_percentage:.2f}%{'':<10}{color}{deviation:+.2f}%{RESET}")
    
    # Look for recurring patterns (potential key length indicators)
    print(f"\n{YELLOW}Common Bigrams and Trigrams{RESET}")
    
    # Analyze bigrams
    bigrams = {}
    for i in range(len(text) - 1):
        if text[i].isalpha() and text[i+1].isalpha():
            bigram = text[i:i+2]
            bigrams[bigram] = bigrams.get(bigram, 0) + 1
    
    # Analyze trigrams
    trigrams = {}
    for i in range(len(text) - 2):
        if text[i].isalpha() and text[i+1].isalpha() and text[i+2].isalpha():
            trigram = text[i:i+3]
            trigrams[trigram] = trigrams.get(trigram, 0) + 1
    
    # Show top bigrams
    top_bigrams = sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:8]
    print(f"Top Bigrams: ", end="")
    print(", ".join([f"{RED}{b}{RESET}({c})" for b, c in top_bigrams]))
    
    # Show top trigrams
    top_trigrams = sorted(trigrams.items(), key=lambda x: x[1], reverse=True)[:8]
    print(f"Top Trigrams: ", end="")
    print(", ".join([f"{RED}{t}{RESET}({c})" for t, c in top_trigrams]))
    
    print(f"\n{GREY}Analysis complete.{RESET}")

def run():
    print(f"""{GREY} 
██████  ██████  ███████ 
██       ██   ██ ██      
██   ███ ██████  █████   
██    ██ ██   ██ ██      
 ██████  ██████  ██      
                        {RESET}""")
    print(f"{RED}G{RESET}romark {RED}B{RESET}rute {RED}F{RESET}rocer")
    print(f"{GREY}-{RESET}" * 50)

    use_test = input(f"Use test case? ({YELLOW}Y/N{RESET}): ").upper() == 'Y'

    if use_test:
        ciphertext = "OHRERPHTMNUQDPUYQTGQHABASQXPTHPYSIXJUFVKNGNDRRIOMAEJGZKHCBNDBIWLDGVWDDVLXCSCZS"
        words_list = ["GRONSFELD", "TESTING", "GRONSFE"]
        required_words = ["ONLYTWOTHINGS"]  # Test case uses ONLYTWO
        expected = {
            'keyword': "GRONSFELD",  # Added 'keyword'
            'primer': "32941",
            'plaintext': "onlytwothingsareinfinitetheuniverseandhumanstupidityandimnotsureabouttheformer"
        }
        print(f"\n{GREY}----------------------")
        print(f"Running a test case...")
        print(f"----------------------{RESET}")
    else:
        ciphertext = input("Enter ciphertext: ").upper()

        required_words_input = input(f"Enter known plaintext words (comma-separated, press Enter for defaults: {RED}BERLINCLOCK, EASTNORTHEAST{RESET}): ").upper()
        if required_words_input:
            required_words = [word.strip() for word in required_words_input.split(",")]
        else:
            required_words = ["BERLINCLOCK", "EASTNORTHEAST"]

        try:
            with open('words_alpha.txt', 'r') as f:
                words_list = [word.strip().upper() for word in f if 1 <= len(word.strip()) <= 15]
        except FileNotFoundError:
            print(f"{RED}Error: words_alpha.txt not found{RESET}")
            return

    # --- KEYWORD ITERATION AND VALIDATION ---

    alphabets_to_test = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOSABCDEFGHIJLMNQUVWXZ"]
    all_results = []

    for alphabet in alphabets_to_test:
        print(f"\nTesting with alphabet: {RED}{alphabet}{RESET}")

        print(f"\n{YELLOW}Filtering keywords based on constraints...{RESET}")
        valid_keywords = [
            keyword for keyword in tqdm(words_list)
            if validate_keyword(keyword, [(0, ciphertext[0:13], "ONLYTWOTHINGS") if use_test else (63, ciphertext[63:74], "BERLINCLOCK")], alphabet)  # Pass alphabet to validate_keyword
        ]

        print(f"\nFiltered from {YELLOW}{len(words_list)}{RESET} to {RED}{len(valid_keywords)}{RESET} possible keywords")

        results = parallel_process_keywords(valid_keywords, ciphertext, required_words, alphabet)  # Pass alphabet to parallel_process_keywords
        all_results.extend(results)

    if all_results:
        test_passed = False

        for result in all_results:
            print(f"{GREY}-{RESET}" * 50)
            print(f"Keyword: {YELLOW}{result['keyword']}{RESET}")
            print(f"Primer: {YELLOW}{result['primer']}{RESET}")
            print(f"Decrypted: {RED}{result['decrypted']}{RESET}")

            if use_test:
                matches = can_form_word("ONLYTWO", result['decrypted'])
                if matches:
                    test_passed = True
        if use_test:
            print(f"\n{YELLOW}TEST CASE {'PASSED' if test_passed else 'FAILED'}{RESET}")

        save_filename = input("Enter filename to save results (or press Enter to skip): ")
        
        if save_filename:
            save_filename = save_filename + ".txt" if not save_filename.endswith(".txt") else save_filename
            save_results_to_file(all_results, save_filename)  # Save all results

        # Option to run frequency analysis
        if all_results:
            analyze_option = input(f"Run frequency analysis on best match? ({YELLOW}Y/N{RESET}): ").upper()
            if analyze_option == 'Y':
                # Fix: Change 'plaintext' to 'decrypted' to match your results dictionary
                analyze_frequency(all_results[0]['decrypted'])
        
    else:
        print(f"\n{RED}NO SOLUTIONS FOUND{RESET}")
        
    print(f"\n{GREY}Program complete.{RESET}")


if __name__ == "__main__":
    run()
