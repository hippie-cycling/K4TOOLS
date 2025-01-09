import tkinter as tk
from tkinter import ttk
import time
import threading
from functools import lru_cache
import re
from collections import Counter

class CryptoToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("K4 toolkit")
        self.alphabet = None
        self.alphabet_dict = None
        self.create_widgets()

    def create_widgets(self):
        # Input frames
        self.single_input_frame = self.create_labeled_frame("Single Input Operations", 0, 0)
        self.double_input_frame = self.create_labeled_frame("Double Input Operations", 0, 1)
        
        # Single input widgets
        self.input_text = self.create_text_widget(self.single_input_frame, "Input", 1, 0)
        self.alphabet_text = self.create_text_widget(self.single_input_frame, "Alphabet", 4, 0)
        
        self.shift = tk.IntVar()
        self.create_dropdown(self.single_input_frame, "Shift", self.shift, range(1, 27), 6, 0)
        
        # Double input widgets
        self.input1_text = self.create_text_widget(self.double_input_frame, "Input 1", 1, 0)
        self.input2_text = self.create_text_widget(self.double_input_frame, "Input 2", 3, 0)
        
        self.operation = tk.StringVar()
        self.create_dropdown(self.double_input_frame, "Operation", self.operation, 
                            ["AND", "OR", "NOT", "NAND", "NOR", "XOR"], 6, 0)

        # Output frame
        self.output_frame = self.create_labeled_frame("Output", 1, 0, columnspan=4)
        self.output_text = self.create_text_widget(self.output_frame, "", 0, 0, font=("Hack NF", 8), width=150, height=20)

        # Buttons
        self.create_button(self.single_input_frame, "IoC", self.ioc, 2, 0)
        self.create_button(self.single_input_frame, "Reverse", self.reverse, 2, 1)
        self.create_button(self.single_input_frame, "Transpose", self.transposition, 6, 1)
        self.create_button(self.single_input_frame, "Morse", self.get_morse_code, 2, 2)
        self.create_button(self.single_input_frame, "Invert Morse", self.convert_to_opposite_morse, 2, 3)
        self.create_button(self.single_input_frame, "String Matrix", self.process_string, 2, 4)
        self.create_button(self.single_input_frame, "Frequency Analysis", self.analyze_frequency, 2, 5)

        self.setup_text_tags()
        
        self.create_button(self.double_input_frame, "Calculate", self.boolean_operations, 5, 1)
        self.create_button(self.double_input_frame, "Base 5 Addition", self.base5_addition, 5, 2)
        
        self.create_button(self.output_frame, "Clear", self.clear_output, 1, 0)
        
        # New Vigenère Cipher frame with target phrases
        self.vigenere_frame = self.create_labeled_frame("Vigenère Cipher Brute Force", 0, 3)
        self.vigenere_cipher_text = self.create_text_widget(self.vigenere_frame, "Ciphertext", 1, 0)
        self.vigenere_alphabet = self.create_text_widget(self.vigenere_frame, "Alphabet", 3, 0)
        # Add new field for target phrases
        self.target_phrases_text = self.create_text_widget(
            self.vigenere_frame, 
            "Target Plaintext (comma-separated)", 
            5, 
            0, 
            height=2
        )
        # Set default target phrases
        default_phrases = "BERLINCLOCK,EASTNORTH,NORTHEAST,CLOCK,NILREB,TSAEHTRON"
        self.target_phrases_text.insert("1.0", default_phrases)

        self.create_button(self.vigenere_frame, "Attack", self.crack_vigenere, 6, 0)
        self.create_button(self.vigenere_frame, "Attack with IoC", self.crack_vigenere_with_ioc, 6, 1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.vigenere_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        # Add new buttons after the existing Calculate button in double_input_frame
        self.create_button(self.double_input_frame, "XOR Brute Force (IoC)", self.xor_bruteforce_ioc, 5, 3)
        self.create_button(self.double_input_frame, "XOR Brute Force (Freq)", self.xor_bruteforce_freq, 5, 4)
        
        # Add progress bar for brute force operations
        self.bf_progress_var = tk.DoubleVar()
        self.bf_progress_bar = ttk.Progressbar(self.double_input_frame, variable=self.bf_progress_var, maximum=100)
        self.bf_progress_bar.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

    def create_labeled_frame(self, text, row, column, **kwargs):
        frame = ttk.LabelFrame(self.master, text=text)
        frame.grid(row=row, column=column, padx=5, **kwargs)
        return frame

    def create_text_widget(self, parent, label_text, row, column, **kwargs):
        if label_text:
            ttk.Label(parent, text=label_text, font=("Hack NF", 10)).grid(row=row-1, column=column, padx=5)
        
        # Default values
        default_kwargs = {
            'height': 5,  # Increased height
            'width': 50,
            'font': ("Hack NF", 10)  # Increased font size
        }
        # Update default values with any provided kwargs
        default_kwargs.update(kwargs)
        
        text_widget = tk.Text(parent, **default_kwargs)
        text_widget.grid(row=row, column=column, padx=5, columnspan=8, sticky='nsew')
        return text_widget

    def create_dropdown(self, parent, label_text, variable, values, row, column):
        ttk.Label(parent, text=label_text, font=("Cambria", 10)).grid(row=row-1, column=column, padx=5)
        ttk.OptionMenu(parent, variable, values[0], *values).grid(row=row, column=column)

    def create_button(self, parent, text, command, row, column):
        ttk.Button(parent, text=text, command=command).grid(row=row, column=column, pady=5)

    @lru_cache(maxsize=None)
    def get_alphabet(self):
        if self.alphabet is None:
            self.alphabet = self.vigenere_alphabet.get("1.0", 'end-1c').upper()
            self.alphabet_dict = {char: i for i, char in enumerate(self.alphabet)}
        return self.alphabet, self.alphabet_dict

    def decrypt_vigenere(self, ciphertext, key):
        alphabet, alphabet_dict = self.get_alphabet()
        key_length = len(key)
        alphabet_length = len(alphabet)
        
        key_shifts = [alphabet_dict[k] for k in key if k in alphabet_dict]
        if not key_shifts:
            return ciphertext

        plaintext = []
        for i, char in enumerate(ciphertext):
            if char in alphabet_dict:
                shift = key_shifts[i % len(key_shifts)]
                char_index = alphabet_dict[char]
                decrypted_char = alphabet[(char_index - shift) % alphabet_length]
                plaintext.append(decrypted_char)
            else:
                plaintext.append(char)
        
        return ''.join(plaintext)

    def load_dictionary(self, file_path):
        alphabet, _ = self.get_alphabet()
        alphabet_set = set(alphabet)
        with open(file_path, 'r') as file:
            return [word.strip().upper() for word in file 
                    if set(word.strip().upper()).issubset(alphabet_set) and len(word) > 2]
    
    def crack_vigenere(self):
        ciphertext = self.vigenere_cipher_text.get("1.0", 'end-1c').upper()
        
        def crack_thread():
            start_time = time.time()
            attempts = 0
            
            try:
                dictionary = self.load_dictionary("words_alpha.txt")
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: words_alpha.txt not found. Please ensure the file is in the same directory as the script.")
                return

            # Get target phrases from input
            target_phrases_text = self.target_phrases_text.get("1.0", 'end-1c').strip()
            target_phrases = {phrase.strip().upper() for phrase in target_phrases_text.split(',')}
            
            total_words = len(dictionary)

            for i, key in enumerate(dictionary):
                attempts += 1
                plaintext = self.decrypt_vigenere(ciphertext, key)
                
                for phrase in target_phrases:
                    if phrase in plaintext:
                        end_time = time.time()
                        highlighted_plaintext = self.highlight_match(plaintext, phrase)
                        result = f"\nFOund a match! Key: {key}\n"
                        result += f"Attempts: {attempts}\n"
                        result += f"Time taken: {end_time - start_time:.2f} seconds\n"
                        result += f"Found match: {phrase}\n"
                        result += f"Plaintext: {highlighted_plaintext}\n"
                        self.output_text.insert("1.0", result)
                        return
                
                if attempts % 1000 == 0:
                    self.progress_var.set((i / total_words) * 100)
                    self.master.update_idletasks()
            
            end_time = time.time()
            result = f"\nUnable to crack. Attempts: {attempts}\n"
            result += f"Time taken: {end_time - start_time:.2f} seconds\n"
            self.output_text.insert("1.0", result)

        threading.Thread(target=crack_thread).start()

    def highlight_match(self, text, phrase):
        start = text.index(phrase)
        end = start + len(phrase)
        return f"{text[:start]}*{text[start:end]}*{text[end:]}"

    def create_labeled_frame(self, text, row, column, **kwargs):
        frame = ttk.LabelFrame(self.master, text=text)
        frame.grid(row=row, column=column, padx=5, **kwargs)
        return frame

    def create_text_widget(self, parent, label_text, row, column, **kwargs):
        if label_text:
            ttk.Label(parent, text=label_text).grid(row=row-1, column=column, padx=5)
        
        # Default values
        default_kwargs = {
            'height': 3,
            'width': 50,
            'font': ("Cambria", 8)
        }
        # Update default values with any provided kwargs
        default_kwargs.update(kwargs)
        
        text_widget = tk.Text(parent, **default_kwargs)
        text_widget.grid(row=row, column=column, padx=5, columnspan=8, sticky='nsew')
        return text_widget

    def create_dropdown(self, parent, label_text, variable, values, row, column):
        ttk.Label(parent, text=label_text).grid(row=row-1, column=column, padx=5)
        ttk.OptionMenu(parent, variable, values[0], *values).grid(row=row, column=column)

    def create_button(self, parent, text, command, row, column):
        ttk.Button(parent, text=text, command=command).grid(row=row, column=column, pady=5)

    def crack_vigenere_with_ioc(self):
        ciphertext = self.vigenere_cipher_text.get("1.0", 'end-1c').upper()
        
        def calculate_ioc(text):
            char_counts = {}
            for char in text:
                if char.isalpha():
                    char_counts[char] = char_counts.get(char, 0) + 1
            
            n = sum(char_counts.values())
            numerator = sum(count * (count - 1) for count in char_counts.values())
            denominator = n * (n - 1)
            return numerator / denominator if denominator != 0 else 0

        def crack_thread():
            start_time = time.time()
            attempts = 0
            
            try:
                dictionary = self.load_dictionary("words_alpha.txt")
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: words_alpha.txt not found. Please ensure the file is in the same directory as the script.")
                return

            total_words = len(dictionary)
            
            for i, key in enumerate(dictionary):
                attempts += 1
                plaintext = self.decrypt_vigenere(ciphertext, key)
                ioc_value = calculate_ioc(plaintext)
                
                if 0.055 <= ioc_value <= 0.07:
                    end_time = time.time()
                    result = f"\nPotential match found!\n"
                    result += f"Key: {key}\n"
                    result += f"Attempts: {attempts}\n"
                    result += f"Time taken: {end_time - start_time:.2f} seconds\n"
                    result += f"IoC: {ioc_value:.4f}\n"
                    result += f"Plaintext: {plaintext}\n\n"
                    self.output_text.insert("1.0", result)
                
                if attempts % 1000 == 0:
                    self.progress_var.set((i / total_words) * 100)
                    self.master.update_idletasks()
            
            end_time = time.time()
            result = f"\nProcess completed. Total attempts: {attempts}\n"
            result += f"Total time taken: {end_time - start_time:.2f} seconds\n"
            self.output_text.insert("1.0", result)

        threading.Thread(target=crack_thread).start()

    def convert_to_opposite_morse(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..'}

        def invert_morse(code):
            return ''.join('.' if char == '-' else '-' if char == '.' else char for char in code)

        output = ''
        for char in input_text.upper():
            if char in morse_dict:
                inverted_code = invert_morse(morse_dict[char])
                for letter, code in morse_dict.items():
                    if code == inverted_code:
                        output += letter
                        break
                else:
                    output += char  # If no matching inverted code, keep original char
            else:
                output += char  # Keep non-letter characters as is

        self.output_text.insert("1.0", f"\nReversed Morse: {output}")

    def setup_text_tags(self):
        self.output_text.tag_configure("highlight", background="yellow", foreground="black")

    def analyze_frequency(self):
        analyzer = LetterFrequencyAnalyzer()
        input_text = self.input_text.get("1.0", 'end-1c').upper()
        result, is_close_match = analyzer.analyze_text(input_text)
        self.output_text.insert("1.0", result)
        if is_close_match:
            self.output_text.insert("1.0", "\nPOTENTIAL MATCH FOUND!\n", "highlight")
        
    def process_string(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        # Function to get all divisors of a number
        def get_divisors(n):
            return [i for i in range(1, n + 1) if n % i == 0]

        # Function to divide string into n parts
        def divide_string(s, n):
            return [s[i:i+n] for i in range(0, len(s), n)]

        # Function to transpose a list of strings
        def transpose(lst):
            return [''.join(x) for x in zip(*lst)]

        length = len(input_text)
        divisors = get_divisors(length)

        self.output_text.insert("1.0", f"Input string: {input_text}")
        self.output_text.insert("1.0", f"Length: {length}")
        self.output_text.insert("1.0", f"Divisors: {divisors}\n")

        for divisor in divisors:
            divided = divide_string(input_text, length // divisor)
            transposed = transpose(divided)
            result = ''.join(transposed)

            self.output_text.insert("1.0", f"\nDivided into: {divisor}")
            self.output_text.insert("1.0", f"\nTransposed and joined result: {result}")

    def get_morse_code(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',  'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', ' ': ' '
        }
        
        morse_code = ''
        total_dots = total_dashes = 0
        for char in input_text.upper():
            if char in morse_dict:
                code = morse_dict[char]
                morse_code += code + ' '
                total_dots += code.count('.')
                total_dashes += code.count('-')
            else:
                morse_code += 'Invalid character '

        self.output_text.insert("1.0", f"\n{morse_code.strip()}\nDots: {total_dots}, Dashes: {total_dashes}")

    def transposition(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        step = self.shift.get()
        alphabet = self.alphabet_text.get("1.0", 'end-1c').upper()
        
        shifted_str = ""
        for char in input_text:
            if char.isalpha():
                index = alphabet.index(char.upper())
                shifted_index = (index + step) % len(alphabet)
                shifted_str += alphabet[shifted_index].lower() if char.islower() else alphabet[shifted_index]
            else:
                shifted_str += char

        self.output_text.insert("1.0", f"\n{shifted_str}")

    def ioc(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        char_counts = {}
        for char in input_text:
            char_counts[char] = char_counts.get(char, 0) + 1

        n = sum(char_counts.values())
        numerator = sum(count * (count - 1) for count in char_counts.values())
        denominator = n * (n - 1)
        ic = numerator / denominator if denominator != 0 else 0

        self.output_text.insert("1.0", f"\n{input_text}\nIoC (English): {ic:.4f}")

    def reverse(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        reversed_text = input_text[::-1]
        self.output_text.insert("1.0", f"\nReversed output: {reversed_text}")

    def boolean_operations(self):
        op = self.operation.get()
        cypher = self.input1_text.get("1.0", 'end-1c')
        dictionary = self.input2_text.get("1.0", 'end-1c')

        ascii_dict = {
        'A': '00001', 'B': '00010', 'C': '00011', 'D': '00100', 'E': '00101',
        'F': '00110', 'G': '00111', 'H': '01000', 'I': '01001', 'J': '01010',
        'K': '01011', 'L': '01100', 'M': '01101', 'N': '01110', 'O': '01111',
        'P': '10000', 'Q': '10001', 'R': '10010', 'S': '10011', 'T': '10100',
        'U': '10101', 'V': '10110', 'W': '10111', 'X': '11000', 'Y': '11001',
        'Z': '11010', '?': '11111'
    }
        reverse_ascii_dict = {v: k for k, v in ascii_dict.items()}

        # Convert the input strings to binary
        binary1 = ''.join(ascii_dict[char] for char in cypher)
        binary2 = ''.join(ascii_dict[char] for char in dictionary)

        # Perform boolean operations on the binary strings
        if op == "XOR":
            result_binary = ''.join('1' if bit1 != bit2 else '0' for bit1, bit2 in zip(binary1, binary2))
        elif op == "AND":
            result_binary = ''.join('1' if bit1 == '1' and bit2 == '1' else '0' for bit1, bit2 in zip(binary1, binary2))
        elif op == "OR":
            result_binary = ''.join('1' if bit1 == '1' or bit2 == '1' else '0' for bit1, bit2 in zip(binary1, binary2))
        elif op == "NOT":
            result_binary = ''.join('1' if bit == '0' else '0' for bit in binary1)
        elif op == "NOR":
            result_binary = ''.join('0' if bit1 == '1' or bit2 == '1' else '1' for bit1, bit2 in zip(binary1, binary2))
        elif op == "NAND":
            result_binary = ''.join('0' if bit1 == '1' and bit2 == '1' else '1' for bit1, bit2 in zip(binary1, binary2))
        else:
            result_binary = ''

        result_text = ''
        for i in range(0, len(result_binary), 5):
            chunk = result_binary[i:i+5]
            if chunk == '00000' or chunk == "11111":
                result_text += next(key for key, value in ascii_dict.items() if value == binary1[i:i+5])
            elif chunk in ascii_dict.values():
                result_text += next(key for key, value in ascii_dict.items() if value == chunk)
            else:
                result_text += next(key for key, value in ascii_dict.items() if value == binary1[i:i+5])

        self.output_text.insert("1.0", f"\nCalculated {op} output: {result_text}")

    def base5_addition(self):
        cypher = self.input1_text.get("1.0", 'end-1c')
        dictionary = self.input2_text.get("1.0", 'end-1c')

        base5_dict = {chr(65+i): f'{i//5}{i%5}' for i in range(26)}
        base5_dict['X'] = '00'  # Special case for 'W'

        num1 = ''.join(base5_dict[char] for char in cypher.upper() if char in base5_dict)
        num2 = ''.join(base5_dict[char] for char in dictionary.upper() if char in base5_dict)

        result = ''.join(str((int(d1) + int(d2)) % 5) for d1, d2 in zip(num1, num2))

        reverse_base5_dict = {v: k for k, v in base5_dict.items()}
        letters = ''.join(reverse_base5_dict.get(result[i:i+2], '?') for i in range(0, len(result), 2))

        self.output_text.insert("1.0", f"\nBase 5 mod 26 addition: {letters}")

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
    
    #################  Added Brute Forcers  #########################

    def calculate_ioc(self, text):
        char_counts = {}
        for char in text:
            if char.isalpha():
                char_counts[char] = char_counts.get(char, 0) + 1
        
        n = sum(char_counts.values())
        if n <= 1:
            return 0
        
        numerator = sum(count * (count - 1) for count in char_counts.values())
        denominator = n * (n - 1)
        return numerator / denominator if denominator != 0 else 0

    def xor_operation(self, text1, text2):
            ascii_dict = {
                'A': '00001', 'B': '00010', 'C': '00011', 'D': '00100', 'E': '00101',
                'F': '00110', 'G': '00111', 'H': '01000', 'I': '01001', 'J': '01010',
                'K': '01011', 'L': '01100', 'M': '01101', 'N': '01110', 'O': '01111',
                'P': '10000', 'Q': '10001', 'R': '10010', 'S': '10011', 'T': '10100',
                'U': '10101', 'V': '10110', 'W': '10111', 'X': '11000', 'Y': '11001',
                'Z': '11010', '?': '11111'
            }
            reverse_ascii_dict = {v: k for k, v in ascii_dict.items()}

            # Repeat text2 to match the length of text1
            repetitions = (len(text1) + len(text2) - 1) // len(text2)
            repeated_text2 = (text2 * repetitions)[:len(text1)]

            # Convert to binary
            binary1 = ''.join(ascii_dict.get(char, '00000') for char in text1)
            binary2 = ''.join(ascii_dict.get(char, '00000') for char in repeated_text2)

            # Perform XOR
            result_binary = ''.join('1' if bit1 != bit2 else '0' 
                                for bit1, bit2 in zip(binary1, binary2))

            # Convert back to text with special handling for 00000 and 11111
            result_text = ''
            for i in range(0, len(result_binary), 5):
                chunk = result_binary[i:i+5]
                if chunk == '00000' or chunk == '11111':
                    # Use the original character from input1
                    original_chunk = binary1[i:i+5]
                    result_text += next(key for key, value in ascii_dict.items() if value == original_chunk)
                elif chunk in ascii_dict.values():
                    result_text += reverse_ascii_dict[chunk]
                else:
                    # If we get an invalid chunk, use the original character from input1
                    original_chunk = binary1[i:i+5]
                    result_text += next(key for key, value in ascii_dict.items() if value == original_chunk)

            return result_text

    def xor_bruteforce_ioc(self):
        def bruteforce_thread():
            input_text = self.input1_text.get("1.0", 'end-1c').upper()
            
            try:
                with open("words_alpha.txt", 'r') as file:
                    words = [word.strip().upper() for word in file]
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: words_alpha.txt not found!")
                return

            total_words = len(words)
            matches_found = 0
            
            self.output_text.insert("1.0", "\nStarting IoC-based XOR brute force...\n")
            for i, word in enumerate(words):
                if len(word) >= 3:  # Skip very short words
                    # Calculate repeated key correctly
                    repetitions = (len(input_text) + len(word) - 1) // len(word)
                    repeated_key = (word * repetitions)[:len(input_text)]
                    
                    result = self.xor_operation(input_text, word)
                    ioc = self.calculate_ioc(result)
                    
                    if 0.055 <= ioc <= 0.07:
                        matches_found += 1
                        self.output_text.insert("1.0", f"\nMatch found with key: {word}")
                        self.output_text.insert("1.0", f"\nKey repeated: {repeated_key}")
                        self.output_text.insert("1.0", f"\nResult: {result}")
                        self.output_text.insert("1.0", f"\nIoC: {ioc:.4f}\n")
                
                if i % 100 == 0:
                    self.bf_progress_var.set((i / total_words) * 100)
                    self.master.update_idletasks()
            
            self.output_text.insert("1.0", f"\nBrute force completed. Found {matches_found} matches.\n")
            self.bf_progress_var.set(100)

        threading.Thread(target=bruteforce_thread).start()

    def xor_bruteforce_freq(self):
        def bruteforce_thread():
            input_text = self.input1_text.get("1.0", 'end-1c').upper()
            analyzer = LetterFrequencyAnalyzer()
            
            try:
                with open("words_alpha.txt", 'r') as file:
                    words = [word.strip().upper() for word in file]
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: words_alpha.txt not found!")
                return

            total_words = len(words)
            matches_found = 0
            
            self.output_text.insert("1.0", "\nStarting frequency analysis-based XOR brute force...\n")
            for i, word in enumerate(words):
                if len(word) >= 3:  # Skip very short words
                    # Calculate repeated key correctly
                    repetitions = (len(input_text) + len(word) - 1) // len(word)
                    repeated_key = (word * repetitions)[:len(input_text)]
                    
                    result = self.xor_operation(input_text, word)
                    result_analysis, is_close_match = analyzer.analyze_text(result)
                    
                    if is_close_match:
                        matches_found += 1
                        self.output_text.insert("1.0", f"\nMatch found with key: {word}")
                        self.output_text.insert("1.0", f"\nKey repeated: {repeated_key}")
                        self.output_text.insert("1.0", f"\nResult: {result}")
                        self.output_text.insert("1.0", f"\n{result_analysis}\n")
                
                if i % 100 == 0:
                    self.bf_progress_var.set((i / total_words) * 100)
                    self.master.update_idletasks()
            
            self.output_text.insert("1.0", f"\nBrute force completed. Found {matches_found} matches.\n")
            self.bf_progress_var.set(100)

        threading.Thread(target=bruteforce_thread).start()

class LetterFrequencyAnalyzer:
    def __init__(self):
        self.english_freq = {
            'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7, 'S': 6.3, 
            'H': 6.1, 'R': 6.0, 'L': 4.0, 'D': 4.3, 'C': 2.8, 'U': 2.8, 'M': 2.4, 
            'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5, 'V': 1.0, 
            'K': 0.8, 'J': 0.2, 'X': 0.2, 'Q': 0.1, 'Z': 0.1
        }

    def calculate_frequency(self, text):
        text = re.sub(r'[^A-Z]', '', text.upper())
        total_chars = len(text)
        char_counts = Counter(text)
        return {char: (count / total_chars) * 100 for char, count in char_counts.items()}

    def compare_frequency(self, input_freq):
        diff_sum = 0
        for char, freq in self.english_freq.items():
            input_freq_char = input_freq.get(char, 0)
            diff_sum += abs(freq - input_freq_char)
        return diff_sum / len(self.english_freq)

    def analyze_text(self, text, threshold=2.0):
        input_freq = self.calculate_frequency(text)
        diff = self.compare_frequency(input_freq)
        is_close_match = diff < threshold
        
        result = f"Frequency analysis results:\n"
        result += f"{'Character':<10}{'English %':<10}{'Input %':<10}{'Difference':<10}\n"
        for char in sorted(self.english_freq.keys()):
            eng_freq = self.english_freq[char]
            inp_freq = input_freq.get(char, 0)
            diff = abs(eng_freq - inp_freq)
            result += f"{char:<10}{eng_freq:<10.2f}{inp_freq:<10.2f}{diff:<10.2f}\n"
        
        result += f"\nOverall difference: {diff:.2f}\n"
        if is_close_match:
            result += "This text closely matches English letter frequency."
        else:
            result += "This text does not closely match English letter frequency."
        
        return result, is_close_match

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoToolGUI(root)
    root.mainloop()


