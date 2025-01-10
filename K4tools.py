import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
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

        # Create menu bar
        self.menubar = tk.Menu(master)
        master.config(menu=self.menubar)

        # Create Operations menu
        self.operations_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="String Operations", menu=self.operations_menu)

        # Create Vigenere menu
        self.vigenere_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Vigenere Tools", menu=self.vigenere_menu)

        # Create Matrix menu
        self.matrix_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Columnar Transposition", menu=self.matrix_menu)
        self.matrix_menu.add_command(label="Columnar Operations", command=self.show_letter_matrix)

        # Create About menu
        self.about_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="About", menu=self.about_menu)
        self.about_menu.add_command(label="About K4 Tools", command=self.show_about)

        # Create windows for different operations
        self.single_double_window = None
        self.vigenere_window = None
        self.letter_matrix_window = None

        # Add menu items
        self.operations_menu.add_command(label="Single/Double Input Operations", 
                                       command=self.show_single_double_operations)
        self.vigenere_menu.add_command(label="Vigenere Brute Force", 
                                      command=self.show_vigenere_operations)

        # Create main output frame
        self.output_frame = ttk.LabelFrame(self.master, text="Output")
        self.output_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.output_text = self.create_text_widget(self.output_frame, "", 0, 0, 
                                                 font=("Hack NF", 8), width=140, height=30)
        
        self.setup_text_tags()

        # Add clear button below output text
        clear_button = ttk.Button(self.output_frame, text="Clear Output", command=self.clear_output)
        clear_button.grid(row=1, column=0, pady=5)

    def show_about(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("About K4 Tools")
        about_window.geometry("400x300")
        
        about_text = f"""K4 is being developed by Daniel Navarro aka HippieCycling. 
        \nFor contact please reach out to navarro.leiva.daniel@gmail.com.
        \nhttps://github.com/hippie-cycling"""
        
        label = ttk.Label(about_window, text=about_text, wraplength=350, justify='left')
        label.pack(padx=20, pady=20)

    def show_letter_matrix(self):
        if self.letter_matrix_window is None or not self.letter_matrix_window.winfo_exists():
            self.letter_matrix_window = tk.Toplevel(self.master)
            self.letter_matrix_window.title("Columnar Transposition")
            
            # Create main frames
            left_frame = ttk.Frame(self.letter_matrix_window)
            left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            
            right_frame = ttk.Frame(self.letter_matrix_window)
            right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
            
            # Configure grid weights
            self.letter_matrix_window.grid_columnconfigure(0, weight=1)
            self.letter_matrix_window.grid_columnconfigure(1, weight=1)
            
            # Input section
            input_frame = self.create_labeled_frame(left_frame, "Input", 0, 0)
            self.input_text = self.create_text_widget(input_frame, "Cyphertext", 1, 0, width=50, height=3)
            
            # Matrix controls
            control_frame = self.create_labeled_frame(left_frame, "Controls", 1, 0)
            ttk.Label(control_frame, text="Rows:").grid(row=0, column=0, padx=5)
            self.rows_entry = ttk.Entry(control_frame, width=5)
            self.rows_entry.grid(row=0, column=1, padx=5)
            
            ttk.Label(control_frame, text="Columns:").grid(row=0, column=2, padx=5)
            self.cols_entry = ttk.Entry(control_frame, width=5)
            self.cols_entry.grid(row=0, column=3, padx=5)
            
            ttk.Button(control_frame, text="Update", 
                      command=self.update_matrix).grid(row=0, column=4, padx=5)
            
            # Column order section
            order_frame = self.create_labeled_frame(left_frame, "Columnar Transposition Order", 2, 0)
            self.order_entry = ttk.Entry(order_frame, width=30)
            self.order_entry.grid(row=0, column=0, padx=5)
            self.order_entry.insert(0, "0,3,6,2,5,1,4")  # Default order
            
            ttk.Button(order_frame, text="Rearrange", 
                      command=self.rearrange_columns).grid(row=0, column=1, padx=5)
            
            # Matrix displays
            matrix_frame = self.create_labeled_frame(right_frame, "Original", 0, 0)
            self.display_frame = ttk.Frame(matrix_frame)
            self.display_frame.grid(row=0, column=0, padx=5, pady=5)
            
            rearranged_frame = self.create_labeled_frame(right_frame, "Transposed", 1, 0)
            self.rearranged_frame = ttk.Frame(rearranged_frame)
            self.rearranged_frame.grid(row=0, column=0, padx=5, pady=5)
            
            # Output section
            # Output section with direction control
            output_frame = self.create_labeled_frame(left_frame, "Output", 3, 0)
            self.matrix_output = self.create_text_widget(output_frame, "Original", 1, 0, width=50, height=3)
            self.rearranged_output = self.create_text_widget(output_frame, "Transposed", 3, 0, width=50, height=3)
            
            # Add direction control radio buttons
            direction_frame = ttk.LabelFrame(output_frame, text="Column Reading Direction")
            direction_frame.grid(row=4, column=0, padx=5, pady=5)
            
            self.right_to_left = tk.BooleanVar(value=True)
            ttk.Radiobutton(direction_frame, text="Right to Left", 
                          variable=self.right_to_left, value=True,
                          command=lambda: self.update_outputs(self.get_current_matrix())).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(direction_frame, text="Left to Right", 
                          variable=self.right_to_left, value=False,
                          command=lambda: self.update_outputs(self.get_current_matrix())).pack(side=tk.LEFT, padx=5)

    def update_matrix(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            input_text = self.input_text.get("1.0", 'end-1c').upper()
            
            if not input_text.isalpha():
                raise ValueError("Please enter only letters")
            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive")
                
            # Create and display matrices
            matrix = np.full((rows, cols), ' ', dtype=str)
            for i, char in enumerate(input_text):
                if i >= rows * cols:
                    break
                matrix[i // cols, i % cols] = char
                
            self.display_matrix(matrix, self.display_frame)
            self.output_matrix(matrix, self.matrix_output)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def rearrange_columns(self):
        try:
            order = [int(x) for x in self.order_entry.get().split(',')]
            matrix = self.get_current_matrix()
            
            if len(order) != matrix.shape[1]:
                raise ValueError("Invalid column order")
                
            rearranged = matrix[:, order]
            self.display_matrix(rearranged, self.rearranged_frame)
            self.output_matrix(rearranged, self.rearranged_output)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def get_current_matrix(self):
        rows = int(self.rows_entry.get())
        cols = int(self.cols_entry.get())
        input_text = self.input_text.get("1.0", 'end-1c').upper()
        
        matrix = np.full((rows, cols), ' ', dtype=str)
        for i, char in enumerate(input_text):
            if i >= rows * cols:
                break
            matrix[i // cols, i % cols] = char
        return matrix

    def display_matrix(self, matrix, frame):
        for widget in frame.winfo_children():
            widget.destroy()
            
        rows, cols = matrix.shape
        for i in range(rows):
            for j in range(cols):
                ttk.Label(frame, text=matrix[i,j], width=2, 
                         relief="solid").grid(row=i, column=j, padx=1, pady=1)
                
    def output_matrix(self, matrix, output_widget):
            output_widget.delete('1.0', tk.END)
            output = ''
            rows, cols = matrix.shape
                            
            # Create output based on direction
            if self.right_to_left.get():
                # Right to left (original behavior)
                for j in range(cols-1, -1, -1):
                    for i in range(rows):
                        if matrix[i,j] != ' ':
                            output += matrix[i,j]
            else:
                # Left to right
                for j in range(cols):
                    for i in range(rows):
                        if matrix[i,j] != ' ':
                            output += matrix[i,j]
                            
            output_widget.insert('1.0', output)

    def update_outputs(self, matrix):
            """Helper function to update both output widgets"""
            self.output_matrix(matrix, self.matrix_output)
            if hasattr(self, 'rearranged_frame'):
                rearranged = matrix[:, [int(x) for x in self.order_entry.get().split(',')]]
                self.output_matrix(rearranged, self.rearranged_output)
    def show_single_double_operations(self):
        if self.single_double_window is None or not self.single_double_window.winfo_exists():
            self.single_double_window = tk.Toplevel(self.master)
            self.single_double_window.title("Single/Double Input Operations")
            
            # Single input frame
            self.single_input_frame = self.create_labeled_frame(self.single_double_window, 
                                                              "Single Input Operations", 0, 0)
            self.input_text = self.create_text_widget(self.single_input_frame, "Cyphertext", 1, 0, width=80)
            self.alphabet_text = self.create_text_widget(self.single_input_frame, "Alphabet", 4, 0, width=80)
            
            # Set default cypher
            self.input_text.insert("1.0", "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")
            # Set default alphabet
            self.alphabet_text.insert("1.0", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

            self.shift = tk.IntVar()
            self.create_dropdown(self.single_input_frame, "Shift", self.shift, range(1, 27), 6, 0)
            
            # Double input frame
            self.double_input_frame = self.create_labeled_frame(self.single_double_window, 
                                                              "Double Input Operations", 0, 1)
            self.input1_text = self.create_text_widget(self.double_input_frame, "Cyphertext", 1, 0, width=80)
            self.input2_text = self.create_text_widget(self.double_input_frame, "Key", 3, 0, width=80)
            
            self.input1_text.insert("1.0", "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")

            self.operation = tk.StringVar()
            self.create_dropdown(self.double_input_frame, "Operation", self.operation, 
                               ["AND", "OR", "NOT", "NAND", "NOR", "XOR"], 5, 0)

            # Create buttons
            self.create_button(self.single_input_frame, "IoC", self.ioc, 2, 0)
            self.create_button(self.single_input_frame, "Reverse", self.reverse, 2, 1)
            self.create_button(self.single_input_frame, "Transpose", self.transposition, 6, 1)
            self.create_button(self.single_input_frame, "Morse", self.get_morse_code, 2, 2)
            self.create_button(self.single_input_frame, "Invert Morse", self.convert_to_opposite_morse, 2, 3)
            self.create_button(self.single_input_frame, "String Matrix", self.process_string, 2, 4)
            self.create_button(self.single_input_frame, "Frequency Analysis", self.analyze_frequency, 2, 5)

            self.create_button(self.double_input_frame, "Calculate", self.boolean_operations, 5, 1)
            self.create_button(self.double_input_frame, "Base 5 Addition", self.base5_addition, 5, 2)
            self.create_button(self.double_input_frame, "XOR Brute Force (IoC)", self.xor_bruteforce_ioc, 5, 3)
            self.create_button(self.double_input_frame, "XOR Brute Force (Freq)", self.xor_bruteforce_freq, 5, 4)

            # Add progress bar
            self.bf_progress_var = tk.DoubleVar()
            self.bf_progress_bar = ttk.Progressbar(self.double_input_frame, 
                                                 variable=self.bf_progress_var, maximum=100)
            self.bf_progress_bar.grid(row=7, column=0, columnspan=5, padx=5, pady=5, sticky='ew')

    def show_vigenere_operations(self):
        if self.vigenere_window is None or not self.vigenere_window.winfo_exists():
            self.vigenere_window = tk.Toplevel(self.master)
            self.vigenere_window.title("Vigenere Brute Force")
            
            # Create Vigenere frame
            self.vigenere_frame = self.create_labeled_frame(self.vigenere_window, 
                                                          "Vigenère Cipher Brute Force", 0, 0)
            
            # Create text widgets with increased width and height
            self.vigenere_cipher_text = self.create_text_widget(
                self.vigenere_frame, 
                "Ciphertext", 
                1, 
                0,
                width=100,  
                height=4,   
                font=("Hack NF", 8)
            )
            
            self.vigenere_alphabet = self.create_text_widget(
                self.vigenere_frame, 
                "Alphabet", 
                3, 
                0,
                width=100,
                height=4,   
                font=("Hack NF", 8)
            )
            
            # Set default cypher
            self.vigenere_cipher_text.insert("1.0", "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")

            # Set default alphabet
            self.vigenere_alphabet.insert("1.0", "KRYPTOSABCDEFGHIJLMNQUVWXZ")
            
            self.target_phrases_text = self.create_text_widget(
                self.vigenere_frame, 
                "Target Plaintext (comma-separated)", 
                5, 
                0,
                width=100,
                height=4,   
                font=("Hack NF", 8)
            )
            
            # Set default target phrases
            default_phrases = "BERLINCLOCK,EASTNORTH,NORTHEAST,CLOCK,NILREB,TSAEHTRON"
            self.target_phrases_text.insert("1.0", default_phrases)

            # Create larger buttons with bigger font and tooltips
            ttk.Style().configure('Large.TButton', font=('Hack NF', 10))
            
            # Add attack buttons and IoC range in same row
            attack_btn = ttk.Button(self.vigenere_frame, text="Attack", 
                                  command=self.crack_vigenere, 
                                  style='Large.TButton')
            attack_btn.grid(row=6, column=0, pady=10)
            
            attack_ioc_btn = ttk.Button(self.vigenere_frame, text="Attack with IoC", 
                                      command=self.crack_vigenere_with_ioc, 
                                      style='Large.TButton')
            attack_ioc_btn.grid(row=6, column=1, pady=10)

            # IoC range entries next to Attack with IoC button
            ttk.Label(self.vigenere_frame, text="Min IoC:").grid(row=6, column=2, padx=5)
            self.min_ioc = tk.StringVar(value="0.06")
            ttk.Entry(self.vigenere_frame, textvariable=self.min_ioc, width=10).grid(row=6, column=3, padx=5)
            
            ttk.Label(self.vigenere_frame, text="Max IoC:").grid(row=6, column=4, padx=5)
            self.max_ioc = tk.StringVar(value="0.07")
            ttk.Entry(self.vigenere_frame, textvariable=self.max_ioc, width=10).grid(row=6, column=5, padx=5)

            # Create tooltips
            attack_tooltip = tk.Label(self.vigenere_frame, 
                                    text="The function will go through every word in the dictionary and output any matches.",
                                    bg="white", relief="solid", borderwidth=1)
            attack_ioc_tooltip = tk.Label(self.vigenere_frame,
                                        text="The function will go through every word in the dictionary and output any match to the defined IoC range.",
                                        bg="white", relief="solid", borderwidth=1)

            def show_tooltip(event, tooltip):
                tooltip.lift()
                tooltip.place(x=event.x_root - self.vigenere_window.winfo_rootx(), 
                            y=event.y_root - self.vigenere_window.winfo_rooty())

            def hide_tooltip(event, tooltip):
                tooltip.place_forget()

            # Bind tooltip events
            attack_btn.bind("<Enter>", lambda e: show_tooltip(e, attack_tooltip))
            attack_btn.bind("<Leave>", lambda e: hide_tooltip(e, attack_tooltip))
            attack_ioc_btn.bind("<Enter>", lambda e: show_tooltip(e, attack_ioc_tooltip))
            attack_ioc_btn.bind("<Leave>", lambda e: hide_tooltip(e, attack_ioc_tooltip))

            # Add dictionary selection frame
            self.dict_frame = self.create_labeled_frame(self.vigenere_window, 
                                                      "Dictionary Selection", 1, 0)
            
            # Create radio buttons for dictionary selection
            self.dict_var = tk.StringVar(value="words_alpha.txt")  # default value
            ttk.Radiobutton(self.dict_frame, text="Dictionary (words_alpha.txt)", 
                          variable=self.dict_var, value="words_alpha.txt").grid(row=0, column=0, padx=5)
            ttk.Radiobutton(self.dict_frame, text="Full Dictionary (words.txt)", 
                          variable=self.dict_var, value="words.txt").grid(row=0, column=1, padx=5)

            # Add progress bar
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(
                self.vigenere_window,
                variable=self.progress_var, 
                maximum=100,
                length=100
            )
            self.progress_bar.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

    def create_labeled_frame(self, parent, text, row, column, **kwargs):
        frame = ttk.LabelFrame(parent, text=text)
        frame.grid(row=row, column=column, padx=5, **kwargs)
        return frame

    def create_text_widget(self, parent, label_text, row, column, **kwargs):
        if label_text:
            ttk.Label(parent, text=label_text, font=("Hack NF", 8)).grid(row=row-1, column=column, padx=5)
        
        # Default values
        default_kwargs = {
            'height': 5,  # Increased height
            'width': 50,
            'font': ("Hack NF", 8),  # Increased font size
        }
        # Update default values with any provided kwargs
        default_kwargs.update(kwargs)
        
        text_widget = tk.Text(parent, **default_kwargs)
        text_widget.grid(row=row, column=column, padx=5, columnspan=8, sticky='nsew')
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal', command=text_widget.xview)
        h_scrollbar.grid(row=row+1, column=column, columnspan=8, sticky='ew')
        text_widget.config(xscrollcommand=h_scrollbar.set)
        
        # Add uppercase conversion
        def to_upper(event=None):
            content = text_widget.get("1.0", 'end-1c')  # Use end-1c to exclude final newline
            upper_content = content.upper()
            if content != upper_content:
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", upper_content)
            return "break"
        
        text_widget.bind('<FocusOut>', to_upper)
        
        return text_widget

    def create_dropdown(self, parent, label_text, variable, values, row, column):
        ttk.Label(parent, text=label_text, font=("Hack NF", 8)).grid(row=row-1, column=column, padx=5)
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
        # Removed unused variable
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
                selected_dict = self.dict_var.get()  # Get selected dictionary file
                dictionary = self.load_dictionary(selected_dict)
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: dictionary not found. Please ensure the file is in the same directory as the script.")
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
                        result = f"\nFound a match! Key: {key}\n"
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
                selected_dict = self.dict_var.get()  # Get selected dictionary file
                dictionary = self.load_dictionary(selected_dict)
            except FileNotFoundError:
                self.output_text.insert("1.0", "\nError: dictionary not found. Please ensure the file is in the same directory as the script.")
                return

            total_words = len(dictionary)
            
            for i, key in enumerate(dictionary):
                attempts += 1
                plaintext = self.decrypt_vigenere(ciphertext, key)
                ioc_value = calculate_ioc(plaintext)
                
                min_ioc_val = float(self.min_ioc.get())
                max_ioc_val = float(self.max_ioc.get())
                if min_ioc_val <= ioc_value <= max_ioc_val:
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
        
        if 0.059 <= ic <= 0.07:
            self.output_text.insert("1.0", "\nPOTENTIAL ENGLISH TEXT DETECTED!", "highlight")
        self.output_text.insert("1.0", f"\nIoC (English): {ic:.4f} \nTarget: 0.0667")
        self.output_text.insert("1.0", f"\n{input_text}")

    def reverse(self):
        input_text = self.input_text.get("1.0", 'end-1c')
        reversed_text = input_text[::-1]
        self.output_text.insert("1.0", f"\nReversed output: {reversed_text}")

    def boolean_operations(self):
        op = self.operation.get()
        input1 = self.input1_text.get("1.0", 'end-1c')
        input2 = self.input2_text.get("1.0", 'end-1c')
        
        # Repeat input2 to match length of input1
        repetitions = (len(input1) + len(input2) - 1) // len(input2)
        input2 = (input2 * repetitions)[:len(input1)]

        ascii_dict = {
            'A': '00001', 'B': '00010', 'C': '00011', 'D': '00100', 'E': '00101',
            'F': '00110', 'G': '00111', 'H': '01000', 'I': '01001', 'J': '01010',
            'K': '01011', 'L': '01100', 'M': '01101', 'N': '01110', 'O': '01111',
            'P': '10000', 'Q': '10001', 'R': '10010', 'S': '10011', 'T': '10100',
            'U': '10101', 'V': '10110', 'W': '10111', 'X': '11000', 'Y': '11001',
            'Z': '11010', '?': '11111'
        }

        # Convert the input strings to binary
        binary1 = ''.join(ascii_dict[char] for char in input1)
        binary2 = ''.join(ascii_dict[char] for char in input2)

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

        
        self.output_text.insert("1.0", f"\nRepeated key: {input2}")
        self.output_text.insert("1.0", f"\nCalculated {op} output: {result_text}")

    def base5_addition(self):
        input1 = self.input1_text.get("1.0", 'end-1c')
        input2 = self.input2_text.get("1.0", 'end-1c')
        
        # Repeat input2 to match length of input1
        repetitions = (len(input1) + len(input2) - 1) // len(input2)
        input2 = (input2 * repetitions)[:len(input1)]

        base5_dict = {chr(65+i): f'{i//5}{i%5}' for i in range(26)}
        base5_dict['X'] = '00'  # Special case for 'W'

        num1 = ''.join(base5_dict[char] for char in input1.upper() if char in base5_dict)
        num2 = ''.join(base5_dict[char] for char in input2.upper() if char in base5_dict)

        result = ''.join(str((int(d1) + int(d2)) % 5) for d1, d2 in zip(num1, num2))

        reverse_base5_dict = {v: k for k, v in base5_dict.items()}
        letters = ''.join(reverse_base5_dict.get(result[i:i+2], '?') for i in range(0, len(result), 2))

        self.output_text.insert("1.0", f"\nRepeated key: {input2}")
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
            
            self.output_text.insert("1.0", f"Brute force completed. Found {matches_found} matches.\n")
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
        
        # Create new window for results
        results_window = tk.Toplevel()
        results_window.title("Frequency Analysis Results")
        
        # Create treeview for table
        # Create frame to hold treeview and scrollbar
        frame = ttk.Frame(results_window)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Create scrollbar first
        scrollbar = ttk.Scrollbar(frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # Create treeview
        tree = ttk.Treeview(frame, columns=('char', 'eng_freq', 'input_freq', 'diff'), 
                           show='headings', yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=tree.yview)
        
        # Define column headers
        tree.heading('char', text='Character')
        tree.heading('eng_freq', text='English %')
        tree.heading('input_freq', text='Input %')
        tree.heading('diff', text='Difference')
        
        # Set column widths
        for col in tree['columns']:
            tree.column(col, width=100)
            
        # Add data rows
        for char in sorted(self.english_freq.keys()):
            eng_freq = self.english_freq[char]
            inp_freq = input_freq.get(char, 0)
            diff_val = abs(eng_freq - inp_freq)
            tree.insert('', 'end', values=(char, f"{eng_freq:.2f}", f"{inp_freq:.2f}", f"{diff_val:.2f}"))
        
        # Add overall results label
        result_text = f"Overall difference: {diff:.2f}\n"
        result_text += "This text closely matches English letter frequency." if is_close_match else \
                      "This text does not closely match English letter frequency."
        ttk.Label(results_window, text=result_text).pack(pady=10)
        
        # Return values for other functions to use
        summary = f"Frequency Analysis: Overall difference = {diff:.2f}"
        if is_close_match:
            summary += " (Matches English frequency)"
        return summary, is_close_match

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoToolGUI(root)
    root.mainloop()



