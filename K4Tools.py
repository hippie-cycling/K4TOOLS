from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path
import numpy as np
import re
import time
from collections import Counter
from functools import lru_cache
import sys

class CryptoToolGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K4 toolkit")
        self.alphabet = None
        self.alphabet_dict = None

        # Create menu bar
        self.menubar = self.menuBar()

        # Create Operations menu
        self.operations_menu = self.menubar.addMenu("String Operations")

        # Create Vigenere menu
        self.vigenere_menu = self.menubar.addMenu("Vigenere Tools")

        # Create Matrix menu
        self.matrix_menu = self.menubar.addMenu("Columnar Transposition")
        self.matrix_menu.addAction("Columnar Operations", self.show_letter_matrix)

        # Create About menu
        self.about_menu = self.menubar.addMenu("About")
        self.about_menu.addAction("About K4 Tools", self.show_about)

        # Create windows for different operations
        self.single_double_window = None
        self.vigenere_window = None
        self.letter_matrix_window = None

        # Add menu items
        self.operations_menu.addAction("Single/Double Input Operations", self.show_single_double_operations)
        self.vigenere_menu.addAction("Vigenere Brute Force", self.show_vigenere_operations)

        # Create main output frame
        self.output_frame = QtWidgets.QGroupBox("Output", self)
        self.setCentralWidget(self.output_frame)
        self.output_layout = QtWidgets.QVBoxLayout(self.output_frame)
        
        self.output_text = self.create_text_widget(self.output_frame, "", width=1000, height=900)
    
        # Add clear button below output text
        clear_button = QtWidgets.QPushButton("Clear", self.output_frame)
        clear_button.setStyleSheet("border: 2px solid black; background: white;")
        
        # Create a layout to place the button at the top right
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        
        self.output_layout.addLayout(button_layout)
        clear_button.clicked.connect(self.clear_output)
        self.output_layout.addWidget(clear_button)
    
        # Set initial size of the main window
        self.resize(1000, 1000)
        # Ensure main window is accessible after opening dialogs
        for action in self.menubar.actions():
            action.setEnabled(True)
        
        # Make dialogs non-modal
        self.about_window = None
        self.letter_matrix_window = None
        self.single_double_window = None
        self.vigenere_window = None

    def create_labeled_frame(self, parent, text):
        frame = QtWidgets.QGroupBox(text, parent)
        layout = QtWidgets.QVBoxLayout(frame)
        frame.setLayout(layout)
        return frame

    def create_text_widget(self, parent, label_text, **kwargs):
        if label_text:
            label = QtWidgets.QLabel(label_text, parent)
            label.setFont(QtGui.QFont("Monaco", 10))
            parent.layout().addWidget(label)

        text_widget = QtWidgets.QTextEdit(parent)
        text_widget.setFont(QtGui.QFont("Monaco", 10))
        text_widget.setFixedHeight(kwargs.get('height', 100))
        text_widget.setFixedWidth(kwargs.get('width', 800))
        parent.layout().addWidget(text_widget)

        return text_widget

    def create_dropdown(self, parent, label_text, values):
        label = QtWidgets.QLabel(label_text, parent)
        label.setFont(QtGui.QFont("Monaco", 8))
        parent.layout().addWidget(label)

        dropdown = QtWidgets.QComboBox(parent)
        dropdown.addItems(values)
        parent.layout().addWidget(dropdown)
        return dropdown

    def create_button(self, parent, text, command):
        button = QtWidgets.QPushButton(text, parent)
        button.clicked.connect(command)
        parent.layout().addWidget(button)
        return button

    def show_about(self):
        if self.about_window is None:
            self.about_window = QtWidgets.QDialog(self)
            self.about_window.setWindowTitle("About K4 Tools")
            self.about_window.setGeometry(100, 100, 400, 300)
            
            about_text = """K4 is being developed by Daniel Navarro aka HippieCycling. 
            \nFor contact please reach out to navarro.leiva.daniel@gmail.com.
            \nhttps://github.com/hippie-cycling"""
            
            label = QtWidgets.QLabel(about_text, self.about_window)
            label.setWordWrap(True)
            label.setAlignment(QtCore.Qt.AlignLeft)
            layout = QtWidgets.QVBoxLayout(self.about_window)
            layout.addWidget(label)
        
        self.about_window.show()

    def show_letter_matrix(self):
        if self.letter_matrix_window is None:
            self.letter_matrix_window = QtWidgets.QDialog(self)
            self.letter_matrix_window.setWindowTitle("Columnar Transposition")
            self.letter_matrix_window.setMinimumWidth(900)
            
            # Main layout with proper spacing
            main_layout = QtWidgets.QHBoxLayout(self.letter_matrix_window)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Left panel for controls
            left_panel = QtWidgets.QWidget()
            left_layout = QtWidgets.QVBoxLayout(left_panel)
            left_layout.setSpacing(15)
            
            # Right panel for matrices
            right_panel = QtWidgets.QWidget()
            right_layout = QtWidgets.QVBoxLayout(right_panel)
            right_layout.setSpacing(15)
            
            # Add panels to main layout
            main_layout.addWidget(left_panel, 1)
            main_layout.addWidget(right_panel, 2)  # Matrix display gets more space
            
            # 1. Input Section
            input_group = QtWidgets.QGroupBox("Input")
            input_layout = QtWidgets.QVBoxLayout(input_group)
            self.input_text_matrix = self.create_text_widget(input_group, "")
            input_layout.addWidget(self.input_text_matrix)
            left_layout.addWidget(input_group)
            
            # 2. Matrix Controls
            controls_group = QtWidgets.QGroupBox("Controls")
            controls_layout = QtWidgets.QGridLayout(controls_group)
            controls_layout.setSpacing(10)
            
            # Row/Column inputs with better spacing
            controls_layout.addWidget(QtWidgets.QLabel("Rows:"), 0, 0)
            self.rows_entry = QtWidgets.QLineEdit()
            self.rows_entry.setFixedWidth(60)
            controls_layout.addWidget(self.rows_entry, 0, 1)
            
            controls_layout.addWidget(QtWidgets.QLabel("Columns:"), 0, 2)
            self.cols_entry = QtWidgets.QLineEdit()
            self.cols_entry.setFixedWidth(60)
            controls_layout.addWidget(self.cols_entry, 0, 3)
            
            update_button = QtWidgets.QPushButton("Update")
            update_button.clicked.connect(self.update_matrix)
            controls_layout.addWidget(update_button, 0, 4)
            
            left_layout.addWidget(controls_group)
            
            # 3. Transposition Order
            order_group = QtWidgets.QGroupBox("Columnar Transposition Order")
            order_layout = QtWidgets.QHBoxLayout(order_group)
            order_layout.setSpacing(10)
            
            self.order_entry = QtWidgets.QLineEdit()
            self.order_entry.setText("0,3,6,2,5,1,4")
            order_layout.addWidget(self.order_entry)
            
            rearrange_button = QtWidgets.QPushButton("Transpose")
            rearrange_button.clicked.connect(self.rearrange_columns)
            rearrange_button.setFixedWidth(150)
            order_layout.addWidget(rearrange_button)
            
            left_layout.addWidget(order_group)
            
            # 4. Matrix Displays
            original_group = QtWidgets.QGroupBox("Original Matrix")
            original_layout = QtWidgets.QVBoxLayout(original_group)
            self.display_frame = QtWidgets.QFrame()
            original_layout.addWidget(self.display_frame)
            right_layout.addWidget(original_group)
            
            transposed_group = QtWidgets.QGroupBox("Transposed Matrix")
            transposed_layout = QtWidgets.QVBoxLayout(transposed_group)
            self.rearranged_frame = QtWidgets.QFrame()
            transposed_layout.addWidget(self.rearranged_frame)
            right_layout.addWidget(transposed_group)
            
            # Direction controls
            direction_group = QtWidgets.QGroupBox("Reading Direction")
            direction_layout = QtWidgets.QVBoxLayout(direction_group)
            direction_layout.setSpacing(10)
            
            # Row-wise vs Column-wise reading
            reading_mode_group = QtWidgets.QGroupBox("Reading Mode")
            reading_mode_layout = QtWidgets.QHBoxLayout(reading_mode_group)
            self.row_wise_radio = QtWidgets.QRadioButton("Row-wise")
            self.column_wise_radio = QtWidgets.QRadioButton("Column-wise")
            self.column_wise_radio.setChecked(True)  # Default to column-wise
            reading_mode_layout.addWidget(self.row_wise_radio)
            reading_mode_layout.addWidget(self.column_wise_radio)
            direction_layout.addWidget(reading_mode_group)
            
            # Column reading direction (left-to-right or right-to-left)
            column_direction_group = QtWidgets.QGroupBox("Column Reading Direction")
            column_direction_layout = QtWidgets.QHBoxLayout(column_direction_group)
            self.right_to_left = QtWidgets.QRadioButton("Right to Left")
            self.right_to_left.setChecked(True)
            left_to_right = QtWidgets.QRadioButton("Left to Right")
            column_direction_layout.addWidget(self.right_to_left)
            column_direction_layout.addWidget(left_to_right)
            direction_layout.addWidget(column_direction_group)
            
            # Row reading direction (top-to-bottom or bottom-to-top)
            row_direction_group = QtWidgets.QGroupBox("Row Reading Direction")
            row_direction_layout = QtWidgets.QHBoxLayout(row_direction_group)
            self.top_to_bottom_radio = QtWidgets.QRadioButton("Top to Bottom")
            self.top_to_bottom_radio.setChecked(True)  # Default to top-to-bottom
            self.bottom_to_top_radio = QtWidgets.QRadioButton("Bottom to Top")
            row_direction_layout.addWidget(self.top_to_bottom_radio)
            row_direction_layout.addWidget(self.bottom_to_top_radio)
            direction_layout.addWidget(row_direction_group)
            
            # Connect signals to update outputs when options change
            self.row_wise_radio.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            self.column_wise_radio.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            self.right_to_left.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            left_to_right.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            self.top_to_bottom_radio.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            self.bottom_to_top_radio.toggled.connect(lambda: self.update_outputs(self.get_current_matrix()))
            
            # 5. Output Section
            output_group = QtWidgets.QGroupBox("Output")
            output_layout = QtWidgets.QVBoxLayout(output_group)
            output_layout.setSpacing(10)
            
            # Original output
            original_output_label = QtWidgets.QLabel("Original:")
            output_layout.addWidget(original_output_label)
            self.matrix_output = self.create_text_widget(output_group, "")
            output_layout.addWidget(self.matrix_output)
            
            # Transposed output
            transposed_output_label = QtWidgets.QLabel("Transposed:")
            output_layout.addWidget(transposed_output_label)
            self.rearranged_output = self.create_text_widget(output_group, "")
            output_layout.addWidget(self.rearranged_output)

            output_layout.addWidget(direction_group)
            left_layout.addWidget(output_group)
            
            # Add stretch to push everything up
            left_layout.addStretch()
            right_layout.addStretch()
        
        self.letter_matrix_window.show()

    def show_single_double_operations(self):
        if self.single_double_window is None:
            self.single_double_window = QtWidgets.QDialog(self)
            self.single_double_window.setWindowTitle("Single/Double Input Operations")
            self.single_double_window.setMinimumWidth(600)
            
            # Main layout
            main_layout = QtWidgets.QVBoxLayout(self.single_double_window)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Single input frame
            self.single_input_frame = QtWidgets.QGroupBox("Single Input Operations")
            main_layout.addWidget(self.single_input_frame)
            single_input_layout = QtWidgets.QGridLayout(self.single_input_frame)
            single_input_layout.setSpacing(10)
            
            # Add single input text widgets
            labels = ["Cyphertext:", "Alphabet:"]
            widgets = []
            for row, label in enumerate(labels):
                label_widget = QtWidgets.QLabel(label)
                label_widget.setFont(QtGui.QFont("Monaco", 10))
                single_input_layout.addWidget(label_widget, row * 2, 0, 1, 2)
                
                text_widget = self.create_text_widget(self.single_input_frame, "")
                single_input_layout.addWidget(text_widget, row * 2 + 1, 0, 1, 2)
                widgets.append(text_widget)
            
            self.input_text, self.alphabet_text = widgets
            
            # Set default values
            self.input_text.setPlainText("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")
            self.alphabet_text.setPlainText("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            
            # Add shift dropdown
            shift_container = QtWidgets.QWidget()
            shift_layout = QtWidgets.QHBoxLayout(shift_container)
            shift_layout.setSpacing(10)
            single_input_layout.addWidget(shift_container, 4, 0, 1, 2)
            
            shift_layout.addWidget(QtWidgets.QLabel("Shift:"))
            self.shift = QtWidgets.QComboBox()
            self.shift.addItems([str(i) for i in range(1, 27)])
            self.shift.setMaximumWidth(80)
            shift_layout.addWidget(self.shift)
            shift_layout.addStretch()
            
            # Create single input buttons in a grid
            button_container = QtWidgets.QWidget()
            button_grid = QtWidgets.QGridLayout(button_container)
            button_grid.setSpacing(10)
            single_input_layout.addWidget(button_container, 5, 0, 1, 2)
            
            single_buttons = [
                ("IoC", self.ioc), ("Reverse", self.reverse), ("Transpose", self.transposition),
                ("Morse", self.get_morse_code), ("Invert Morse", self.convert_to_opposite_morse),
                ("String Matrix", self.process_string), ("Frequency Analysis", self.analyze_frequency)
            ]
            
            for i, (text, command) in enumerate(single_buttons):
                btn = QtWidgets.QPushButton(text)
                btn.clicked.connect(command)
                btn.setMinimumWidth(120)
                button_grid.addWidget(btn, i // 3, i % 3)
            
            # Double input frame
            self.double_input_frame = QtWidgets.QGroupBox("Double Input Operations")
            main_layout.addWidget(self.double_input_frame)
            double_input_layout = QtWidgets.QGridLayout(self.double_input_frame)
            double_input_layout.setSpacing(10)
            
            # Add double input text widgets
            labels = ["Cyphertext:", "Key:"]
            widgets = []
            for row, label in enumerate(labels):
                label_widget = QtWidgets.QLabel(label)
                label_widget.setFont(QtGui.QFont("Monaco", 10))
                double_input_layout.addWidget(label_widget, row * 2, 0, 1, 2)
                
                text_widget = self.create_text_widget(self.double_input_frame, "")
                double_input_layout.addWidget(text_widget, row * 2 + 1, 0, 1, 2)
                widgets.append(text_widget)
            
            self.input1_text, self.input2_text = widgets
            self.input1_text.setPlainText("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")
            
            # Create double input buttons
            double_button_container = QtWidgets.QWidget()
            double_button_grid = QtWidgets.QGridLayout(double_button_container)
            double_button_grid.setSpacing(10)
            double_input_layout.addWidget(double_button_container, 5, 0, 1, 2)
            
            double_buttons = [
                ("XOR", self.xor),
                ("ASCII Subtraction", self.base5_addition),
                ("Modular Subtraction", self.modular_subtraction),
                ("XOR Brute Force (IoC)", self.xor_bruteforce_ioc),
                ("XOR Brute Force (Freq)", self.xor_bruteforce_freq)
            ]
            
            for i, (text, command) in enumerate(double_buttons):
                btn = QtWidgets.QPushButton(text)
                btn.clicked.connect(command)
                btn.setMinimumWidth(120)
                double_button_grid.addWidget(btn, i // 2, i % 2)
            
            # Add progress bar with proper spacing
            self.bf_progress_bar = QtWidgets.QProgressBar()
            self.bf_progress_bar.setMaximum(100)
            self.bf_progress_bar.setTextVisible(False)  # Hide the percentage text
            double_input_layout.addWidget(self.bf_progress_bar, 6, 0, 1, 2)
        
        self.single_double_window.show()

    def show_vigenere_operations(self):
        if self.vigenere_window is None or not self.vigenere_window.isVisible():
            self.vigenere_window = QtWidgets.QDialog(self)
            self.vigenere_window.setWindowTitle("Vigenere Brute Force")
            self.vigenere_window.setMinimumWidth(600)
            
            # Main layout
            main_layout = QtWidgets.QVBoxLayout(self.vigenere_window)
            main_layout.setSpacing(15)  # Add spacing between major sections
            main_layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the window
            
            # Create Vigenere frame
            self.vigenere_frame = QtWidgets.QGroupBox("Vigenère Cipher Brute Force")
            main_layout.addWidget(self.vigenere_frame)
            vigenere_layout = QtWidgets.QGridLayout(self.vigenere_frame)
            vigenere_layout.setSpacing(10)  # Add spacing between elements
            
            # Create text widgets with labels
            labels = ["Ciphertext:", "Alphabet:", "Target Plaintext:"]
            widgets = []
            
            for row, label in enumerate(labels):
                label_widget = QtWidgets.QLabel(label)
                label_widget.setFont(QtGui.QFont("Monaco", 10))
                vigenere_layout.addWidget(label_widget, row * 2, 0, 1, 2)
                
                text_widget = self.create_text_widget(self.vigenere_frame, "")
                vigenere_layout.addWidget(text_widget, row * 2 + 1, 0, 1, 2)
                widgets.append(text_widget)
            
            self.vigenere_cipher_text, self.vigenere_alphabet, self.target_phrases_text = widgets
            
            # Set default values
            self.vigenere_cipher_text.setPlainText("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")
            self.vigenere_alphabet.setPlainText("KRYPTOSABCDEFGHIJLMNQUVWXZ")
            self.target_phrases_text.setPlainText("BERLINCLOCK,EASTNORTH,NORTHEAST,CLOCK,NILREB,TSAEHTRON")
            
            # Attack buttons container
            button_container = QtWidgets.QWidget()
            button_layout = QtWidgets.QHBoxLayout(button_container)
            button_layout.setSpacing(10)
            vigenere_layout.addWidget(button_container, 6, 0, 1, 2)
            
            # Add attack buttons
            attack_btn = QtWidgets.QPushButton("Attack")
            attack_btn.setMinimumWidth(120)
            attack_btn.clicked.connect(self.crack_vigenere)
            button_layout.addWidget(attack_btn)
            
            attack_ioc_btn = QtWidgets.QPushButton("Attack with IoC")
            attack_ioc_btn.setMinimumWidth(120)
            attack_ioc_btn.clicked.connect(self.crack_vigenere_with_ioc)
            button_layout.addWidget(attack_ioc_btn)
            
            button_layout.addStretch()  # Add stretch to keep buttons left-aligned
            
            # IoC range container
            ioc_container = QtWidgets.QWidget()
            ioc_layout = QtWidgets.QHBoxLayout(ioc_container)
            ioc_layout.setSpacing(10)
            vigenere_layout.addWidget(ioc_container, 7, 0, 1, 2)
            
            # Add IoC range inputs
            ioc_layout.addWidget(QtWidgets.QLabel("Min IoC:"))
            self.min_ioc = QtWidgets.QLineEdit()
            self.min_ioc.setText("0.06")
            self.min_ioc.setMaximumWidth(80)
            ioc_layout.addWidget(self.min_ioc)
            
            ioc_layout.addWidget(QtWidgets.QLabel("Max IoC:"))
            self.max_ioc = QtWidgets.QLineEdit()
            self.max_ioc.setText("0.07")
            self.max_ioc.setMaximumWidth(80)
            ioc_layout.addWidget(self.max_ioc)
            
            ioc_layout.addStretch()  # Add stretch to keep IoC inputs left-aligned
            
            # Dictionary selection frame
            dict_frame = QtWidgets.QGroupBox("Dictionary Selection")
            main_layout.addWidget(dict_frame)
            dict_layout = QtWidgets.QVBoxLayout(dict_frame)
            dict_layout.setSpacing(10)
            
            # Create radio buttons for dictionary selection
            self.dict_var = QtWidgets.QButtonGroup(dict_frame)
            for text in ["words_alpha.txt", "words.txt"]:
                radio = QtWidgets.QRadioButton(text)
                self.dict_var.addButton(radio)
                dict_layout.addWidget(radio)
            self.dict_var.buttons()[0].setChecked(True)
            
            # Add progress bar with some spacing
            main_layout.addSpacing(10)
            self.progress_bar = QtWidgets.QProgressBar()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setTextVisible(False)  # Hide the percentage text
            main_layout.addWidget(self.progress_bar)
        
        self.vigenere_window.show()

    def update_matrix(self):
        try:
            rows = int(self.rows_entry.text())
            cols = int(self.cols_entry.text())
            input_text = self.input_text_matrix.toPlainText().upper()
            
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
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def rearrange_columns(self):
        try:
            # Get the column order from the input
            order_text = self.order_entry.text().strip()
            if not order_text:
                raise ValueError("Column order cannot be empty. Please enter a valid order.")
            
            # Convert the order text to a list of integers
            order = [int(x) for x in order_text.split(',')]
            
            # Get the current matrix
            matrix = self.get_current_matrix()
            if matrix is None:
                raise ValueError("No matrix present. Please update the matrix first.")
            
            # Validate the column order
            if len(order) != matrix.shape[1]:
                raise ValueError(f"Invalid column order. Expected {matrix.shape[1]} columns, but got {len(order)}.")
            
            # Rearrange the columns
            rearranged = matrix[:, order]
            
            # Display the rearranged matrix
            self.display_matrix(rearranged, self.rearranged_frame)
            self.output_matrix(rearranged, self.rearranged_output)
            
        except ValueError as e:
            # Show the error message to the user
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def get_current_matrix(self):
        try:
            rows = int(self.rows_entry.text())
            cols = int(self.cols_entry.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Rows and columns must be valid integers.")
            return None
        input_text = self.input_text_matrix.toPlainText().upper()
        
        matrix = np.full((rows, cols), ' ', dtype=str)
        for i, char in enumerate(input_text):
            if i >= rows * cols:
                break
            matrix[i // cols, i % cols] = char
        return matrix

    def display_matrix(self, matrix, frame):
        if frame.layout() is not None:
            old_layout = frame.layout()
            for i in reversed(range(old_layout.count())): 
                old_layout.itemAt(i).widget().setParent(None)
            QtWidgets.QWidget().setLayout(old_layout)
            
        rows, cols = matrix.shape
        grid_layout = QtWidgets.QGridLayout(frame)
        for i in range(rows):
            for j in range(cols):
                label = QtWidgets.QLabel(matrix[i, j], frame)
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setStyleSheet("border: 1px solid #5A5A5A;")
                grid_layout.addWidget(label, i, j)
        frame.setLayout(grid_layout)
                
    def output_matrix(self, matrix, output_widget):
        if matrix is None:
            QtWidgets.QMessageBox.critical(self, "Error", "No matrix present.")
            return
        output_widget.clear()
        output = ''
        rows, cols = matrix.shape

        # Determine reading direction (row-wise or column-wise)
        if self.row_wise_radio.isChecked():
            # Row-wise reading
            if self.bottom_to_top_radio.isChecked():
                # Bottom to top
                for i in range(rows-1, -1, -1):
                    for j in range(cols):
                        if matrix[i, j] != ' ':
                            output += matrix[i, j]
            else:
                # Top to bottom (default)
                for i in range(rows):
                    for j in range(cols):
                        if matrix[i, j] != ' ':
                            output += matrix[i, j]
        else:
            # Column-wise reading (existing behavior)
            if self.right_to_left.isChecked():
                # Right to left
                for j in range(cols-1, -1, -1):
                    for i in range(rows):
                        if matrix[i, j] != ' ':
                            output += matrix[i, j]
            else:
                # Left to right (default)
                for j in range(cols):
                    for i in range(rows):
                        if matrix[i, j] != ' ':
                            output += matrix[i, j]

        output_widget.setPlainText(output)

    def update_outputs(self, matrix):
        """Helper function to update both output widgets"""
        if matrix is None:
            QtWidgets.QMessageBox.critical(self, "Error", "No matrix present.")
            return
        
        self.output_matrix(matrix, self.matrix_output)
        
        if hasattr(self, 'rearranged_frame'):
            try:
                # Attempt to rearrange the matrix based on user input
                rearranged = matrix[:, [int(x) for x in self.order_entry.text().split(',')]]
                self.output_matrix(rearranged, self.rearranged_output)
            except IndexError as e:
                # If an IndexError occurs, show an error message to the user
                QtWidgets.QMessageBox.critical(self, "Error", f"Index out of bounds: {e}\nPlease check the order of indices.")
            except ValueError as e:
                # If a ValueError occurs (e.g., invalid input), show an error message to the user
                QtWidgets.QMessageBox.critical(self, "Error", f"Invalid input: {e}\nPlease enter valid indices separated by commas.")

    @lru_cache(maxsize=None)
    def get_alphabet(self):
        if self.alphabet is None:
            self.alphabet = self.vigenere_alphabet.toPlainText().upper()
            self.alphabet_dict = {char: i for i, char in enumerate(self.alphabet)}
        return self.alphabet, self.alphabet_dict

    def decrypt_vigenere(self, ciphertext, key):
        alphabet, alphabet_dict = self.get_alphabet()
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
        ciphertext = self.vigenere_cipher_text.toPlainText().upper()
        
        class Worker(QtCore.QObject):
            finished = QtCore.pyqtSignal()
            progress = QtCore.pyqtSignal(int)
            result = QtCore.pyqtSignal(str)

            def __init__(self, parent_class):
                super().__init__()
                self.parent_class = parent_class  # Store reference to parent class
            
            def run(self):
                start_time = time.time()
                attempts = 0
                matches_found = 0
                
                try:
                    selected_dict = self.parent_class.dict_var.checkedButton().text()
                    dictionary = self.parent_class.load_dictionary(selected_dict)
                except FileNotFoundError:
                    self.result.emit("\nError: dictionary not found. Please ensure the file is in the same directory as the script.")
                    self.finished.emit()
                    return

                target_phrases_text = self.parent_class.target_phrases_text.toPlainText().strip()
                target_phrases = {phrase.strip().upper() for phrase in target_phrases_text.split(',')}
                
                total_words = len(dictionary)

                for i, key in enumerate(dictionary):
                    attempts += 1
                    plaintext = self.parent_class.decrypt_vigenere(ciphertext, key)
                    
                    if plaintext is None:
                        continue
                    
                    for phrase in target_phrases:
                        if phrase in plaintext:
                            matches_found += 1
                            highlighted_plaintext = self.parent_class.highlight_match(plaintext, phrase)
                            result = f"\nFound match #{matches_found}! Key: {key}\n"
                            result += f"Attempts: {attempts}\n"
                            result += f"Time elapsed: {time.time() - start_time:.2f} seconds\n"
                            result += f"Found match: {phrase}\n"
                            result += f"Plaintext: {highlighted_plaintext}\n"
                            self.result.emit(result)
                            break
                    
                    if attempts % 1000 == 0:
                        self.progress.emit(int((i / total_words) * 100))

                end_time = time.time()
                summary = f"\nCracking complete. Total matches found: {matches_found}\n"
                summary += f"Total attempts: {attempts}\n"
                summary += f"Total time taken: {end_time - start_time:.2f} seconds\n"
                self.result.emit(summary)
                self.finished.emit()

        def start_thread():
            # Create thread first
            thread = QtCore.QThread()
            
            # Create worker without parent
            worker = Worker(self)  # Pass self as parent_class
            
            # Move worker to thread
            worker.moveToThread(thread)

            # Connect signals
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            worker.progress.connect(self.progress_bar.setValue)
            worker.result.connect(self.output_text.append)
            worker.finished.connect(lambda: self.progress_bar.setValue(100))

            # Store references to prevent garbage collection
            self.thread = thread
            self.worker = worker

            # Start thread
            thread.start()

        start_thread()

    def highlight_match(self, text, phrase):
        start = text.index(phrase)
        end = start + len(phrase)
        return f"{text[:start]}*{text[start:end]}*{text[end:]}"
    
    def crack_vigenere_with_ioc(self):
            ciphertext = self.vigenere_cipher_text.toPlainText().upper()
            
            def calculate_ioc(text):
                char_counts = {}
                for char in text:
                    if char.isalpha():
                        char_counts[char] = char_counts.get(char, 0) + 1
                
                n = sum(char_counts.values())
                numerator = sum(count * (count - 1) for count in char_counts.values())
                denominator = n * (n - 1)
                return numerator / denominator if denominator != 0 else 0

            class Worker(QtCore.QObject):
                finished = QtCore.pyqtSignal()
                progress = QtCore.pyqtSignal(int)
                result = QtCore.pyqtSignal(str)

                def __init__(self, parent_class):
                    super().__init__()
                    self.parent_class = parent_class  # Store reference to parent class
                
                def run(self):
                    start_time = time.time()
                    attempts = 0
                    
                    try:
                        selected_dict = self.parent_class.dict_var.checkedButton().text()
                        dictionary = self.parent_class.load_dictionary(selected_dict)
                    except FileNotFoundError:
                        self.result.emit("\nError: dictionary not found. Please ensure the file is in the same directory as the script.")
                        self.finished.emit()
                        return

                    total_words = len(dictionary)
                    
                    for i, key in enumerate(dictionary):
                        attempts += 1
                        plaintext = self.parent_class.decrypt_vigenere(ciphertext, key)
                        ioc_value = calculate_ioc(plaintext)
                        
                        # Changed from self.parent() to self.parent_class
                        min_ioc_val = float(self.parent_class.min_ioc.text())
                        max_ioc_val = float(self.parent_class.max_ioc.text())
                        if min_ioc_val <= ioc_value <= max_ioc_val:
                            end_time = time.time()
                            result = f"\nPotential match found!\n"
                            result += f"Key: {key}\n"
                            result += f"Attempts: {attempts}\n"
                            result += f"Time taken: {end_time - start_time:.2f} seconds\n"
                            result += f"IoC: {ioc_value:.4f}\n"
                            result += f"Plaintext: {plaintext}\n\n"
                            self.result.emit(result)
                        
                        if attempts % 1000 == 0:
                            self.progress.emit(int((i / total_words) * 100))
                            QtWidgets.QApplication.processEvents()
                    
                    end_time = time.time()
                    result = f"\nProcess completed. Total attempts: {attempts}\n"
                    result += f"Total time taken: {end_time - start_time:.2f} seconds\n"
                    self.result.emit(result)
                    self.finished.emit()

            def start_thread():
                # Create thread first
                thread = QtCore.QThread()
                
                # Create worker without parent
                worker = Worker(self)  # Pass self as parent_class
                
                # Move worker to thread
                worker.moveToThread(thread)

                # Connect signals
                thread.started.connect(worker.run)
                worker.finished.connect(thread.quit)
                worker.finished.connect(worker.deleteLater)
                thread.finished.connect(thread.deleteLater)
                worker.progress.connect(self.progress_bar.setValue)
                worker.result.connect(self.output_text.append)
                worker.finished.connect(lambda: self.progress_bar.setValue(100))

                # Store references to prevent garbage collection
                self.thread = thread
                self.worker = worker

                # Start thread
                thread.start()

            start_thread()

    def convert_to_opposite_morse(self):
        input_text = self.input_text.toPlainText()
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

        self.output_text.insertPlainText(f"\nReversed Morse: {output}\n")

    def analyze_frequency(self):
        analyzer = LetterFrequencyAnalyzer()
        input_text = self.input_text.toPlainText().upper()
        result, is_close_match = analyzer.analyze_text(input_text)
        self.output_text.insertPlainText(result)
        if is_close_match:
            self.output_text.insertPlainText("\nPOTENTIAL MATCH FOUND!\n")

    def process_string(self):
        input_text = self.input_text.toPlainText()
        
        def get_divisors(n):
            return [i for i in range(1, n + 1) if n % i == 0]

        def divide_string(s, n):
            return [s[i:i+n] for i in range(0, len(s), n)]

        def transpose(lst):
            return [''.join(x) for x in zip(*lst)]

        length = len(input_text)
        divisors = get_divisors(length)

        self.output_text.insertPlainText(f"Input string: {input_text}\n")
        self.output_text.insertPlainText(f"Length: {length}\n")
        self.output_text.insertPlainText(f"Divisors: {divisors}\n")

        for divisor in divisors:
            divided = divide_string(input_text, length // divisor)
            transposed = transpose(divided)
            result = ''.join(transposed)

            self.output_text.insertPlainText(f"\nDivided into: {divisor}\n")
            self.output_text.insertPlainText(f"Transposed and joined result: {result}\n")

    def get_morse_code(self):
        input_text = self.input_text.toPlainText()
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

        self.output_text.insertPlainText(f"\n{morse_code.strip()}\nDots: {total_dots}, Dashes: {total_dashes}\n")

    def transposition(self):
        input_text = self.input_text.toPlainText()
        step = int(self.shift.currentText())
        alphabet = self.alphabet_text.toPlainText().upper()
        
        shifted_str = ""
        for char in input_text:
            if char.isalpha():
                index = alphabet.index(char.upper())
                shifted_index = (index + step) % len(alphabet)
                shifted_str += alphabet[shifted_index].lower() if char.islower() else alphabet[shifted_index]
            else:
                shifted_str += char

        self.output_text.insertPlainText(f"\nPadded result: {shifted_str}\n")

    def ioc(self):
        input_text = self.input_text.toPlainText()
        char_counts = {}
        for char in input_text:
            char_counts[char] = char_counts.get(char, 0) + 1

        n = sum(char_counts.values())
        numerator = sum(count * (count - 1) for count in char_counts.values())
        denominator = n * (n - 1)
        ic = numerator / denominator if denominator != 0 else 0
        
        if 0.059 <= ic <= 0.071:
            self.output_text.insertPlainText("\nPOTENTIAL ENGLISH TEXT DETECTED!")
        self.output_text.insertPlainText(f"\nIoC (English): {ic:.4f} \nTarget: 0.0667")
        self.output_text.insertPlainText(f"\n{input_text}")

    def reverse(self):
        input_text = self.input_text.toPlainText()
        reversed_text = input_text[::-1]
        self.output_text.insertPlainText(f"\nReversed output: {reversed_text}")

    def base5_addition(self):
        # Get input strings
        input1 = self.input1_text.toPlainText().strip()
        input2 = self.input2_text.toPlainText().strip()

        # Check if the second input is empty
        if not input2:
            QtWidgets.QMessageBox.critical(self, "Error", "Key cannot be empty")
            return

        # Repeat input2 to match the length of input1
        repetitions = (len(input1) + len(input2) - 1) // len(input2)
        input2 = (input2 * repetitions)[:len(input1)]

        # Function to map characters to the range 65-90 (A-Z)
        def map_to_ascii_range(char):
            char = char.upper()
            if ord(char) < 65 or ord(char) > 90:
                char = chr((ord(char) - 65) % 26 + 65)
            return char

        # Map input characters to the range 65-90
        input1_mapped = ''.join(map_to_ascii_range(char) for char in input1)
        input2_mapped = ''.join(map_to_ascii_range(char) for char in input2)

        # Base-5 mapping for A-Z
        base5_dict = {chr(65 + i): f'{i // 5}{i % 5}' for i in range(26)}

        # Convert input strings to base-5
        num1 = ''.join(base5_dict[char] for char in input1_mapped if char in base5_dict)
        num2 = ''.join(base5_dict[char] for char in input2_mapped if char in base5_dict)

        # Perform base-5 subtraction
        result = []
        for d1, d2 in zip(num1, num2):
            diff = (int(d1) - int(d2)) % 5  # Handle negative results with modulo 5
            result.append(str(diff))

        result = ''.join(result)

        # Reverse mapping from base-5 to letters
        reverse_base5_dict = {v: k for k, v in base5_dict.items()}
        letters = ''.join(reverse_base5_dict.get(result[i:i + 2], '?') for i in range(0, len(result), 2))

        # Display the results
        self.output_text.clear()  # Clear previous output
        self.output_text.insertPlainText(f"\nRepeated key: {input2_mapped}")
        self.output_text.insertPlainText(f"\nBase 5 mod 26 subtraction: {letters}")
    
    def base5_addition(self):
        # Get input strings
        input1 = self.input1_text.toPlainText().strip()
        input2 = self.input2_text.toPlainText().strip()

        # Check if the second input is empty
        if not input2:
            QtWidgets.QMessageBox.critical(self, "Error", "Key cannot be empty")
            return

        # Repeat input2 to match the length of input1
        repetitions = (len(input1) + len(input2) - 1) // len(input2)
        input2 = (input2 * repetitions)[:len(input1)]

        # Function to map characters to the range 65-90 (A-Z)
        def map_to_ascii_range(char):
            char = char.upper()
            if ord(char) < 65 or ord(char) > 90:
                char = chr((ord(char) - 65) % 26 + 65)
            return char

        # Map input characters to the range 65-90
        input1_mapped = ''.join(map_to_ascii_range(char) for char in input1)
        input2_mapped = ''.join(map_to_ascii_range(char) for char in input2)

        # Base-5 mapping for A-Z
        base5_dict = {chr(65 + i): f'{i // 5}{i % 5}' for i in range(26)}

        # Convert input strings to base-5
        num1 = ''.join(base5_dict[char] for char in input1_mapped if char in base5_dict)
        num2 = ''.join(base5_dict[char] for char in input2_mapped if char in base5_dict)

        # Perform base-5 subtraction
        result = []
        for d1, d2 in zip(num1, num2):
            diff = (int(d1) - int(d2)) % 5  # Handle negative results with modulo 5
            result.append(str(diff))

        result = ''.join(result)

        # Reverse mapping from base-5 to letters
        reverse_base5_dict = {v: k for k, v in base5_dict.items()}
        letters = ''.join(reverse_base5_dict.get(result[i:i + 2], '?') for i in range(0, len(result), 2))

        # Display the results
        self.output_text.clear()  # Clear previous output
        self.output_text.insertPlainText(f"\nRepeated key: {input2_mapped}")
        self.output_text.insertPlainText(f"\nBase 5 mod 26 subtraction: {letters}")

    def xor(self):
    # Get input strings
        ciphertext = self.input1_text.toPlainText().strip()
        key = self.input2_text.toPlainText().strip()

        # Check if the key is empty
        if not key:
            QtWidgets.QMessageBox.critical(self, "Error", "Key cannot be empty")
            return

        # Repeat key to match ciphertext length
        repetitions = (len(ciphertext) + len(key) - 1) // len(key)
        repeated_key = (key * repetitions)[:len(ciphertext)]

        def letter_to_5bit(char):
            """Convert A-Z to 5-bit binary value (0-25)"""
            val = (ord(char) - ord('A')) % 26
            return format(val, '05b')

        def binary_to_letter(binary):
            """Convert 5-bit binary back to letter A-Z"""
            val = int(binary, 2) % 26
            return chr(val + ord('A'))

        # Perform XOR operation character by character
        result = []
        debug_info = []  # For storing intermediate calculations
        
        for c, k in zip(ciphertext, repeated_key):
            # Convert to 5-bit binary
            c_bin = letter_to_5bit(c)
            k_bin = letter_to_5bit(k)
            
            # Perform XOR on binary strings
            xor_result = ''
            for c_bit, k_bit in zip(c_bin, k_bin):
                xor_result += '1' if c_bit != k_bit else '0'
            
            # Check for null result (00000)
            if xor_result == '00000':
                result_char = c  # Use cipher letter for null result
            else:
                result_char = binary_to_letter(xor_result)
                
            result.append(result_char)
            
            # Store debug info
            debug_info.append(f"{c}({c_bin}) ⊕ {k}({k_bin}) = {xor_result} -> {result_char}")

        result_text = ''.join(result)

        # Display the results
        self.output_text.clear()
        self.output_text.insertPlainText(f"Input text: {ciphertext}\n")
        self.output_text.insertPlainText(f"Repeated key: {repeated_key}\n")
        self.output_text.insertPlainText(f"XOR result: {result_text}\n")
        self.output_text.insertPlainText("\nDetailed binary operations:\n")
        for debug_line in debug_info:
            self.output_text.insertPlainText(debug_line + "\n")

    def modular_subtraction(self):
            # Get input strings
            input1 = self.input1_text.toPlainText().strip()
            input2 = self.input2_text.toPlainText().strip()

            # Check if the second input is empty
            if not input2:
                QtWidgets.QMessageBox.critical(self, "Error", "Key cannot be empty")
                return

            # Repeat input2 to match the length of input1
            repetitions = (len(input1) + len(input2) - 1) // len(input2)
            input2 = (input2 * repetitions)[:len(input1)]

            # Function to map characters to the range 65-90 (A-Z) and handle out-of-range chars
            def map_to_ascii_range(char):
                char = char.upper()
                if not ('A' <= char <= 'Z'):  # More Pythonic check
                    char = chr((ord(char) - ord('A')) % 26 + ord('A')) # Modulo 26 for wrap-around
                return char

            # Map input characters to the range 65-90
            input1_mapped = ''.join(map_to_ascii_range(char) for char in input1)
            input2_mapped = ''.join(map_to_ascii_range(char) for char in input2)

            # Perform alphabet position based subtraction (mod 26)
            result_letters = []
            for char1, char2 in zip(input1_mapped, input2_mapped):
                pos1 = ord(char1) - ord('A')
                pos2 = ord(char2) - ord('A')
                diff = (pos1 - pos2) % 26  # Modulo 26 for wrap-around (important!)
                result_letters.append(chr(diff + ord('A')))  # Convert back to character

            result_string = "".join(result_letters)


            # Display the results
            self.output_text.clear()  # Clear previous output
            self.output_text.insertPlainText(f"\nRepeated key: {input2_mapped}")
            self.output_text.insertPlainText(f"\nAlphabetical Subtraction (mod 26): {result_string}")

    def clear_output(self):
        self.output_text.clear()
    
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

    def xor_operation(text1, text2):
        # Ensure both strings are of the same length
        if len(text1) != len(text2):
            raise ValueError("Both strings must be of the same length")
        
        result = []
        
        for c1, c2 in zip(text1, text2):
            # Perform XOR on the ASCII values of the characters
            xor_result = ord(c1) ^ ord(c2)
            
            # Map the result back to the range 65-90 if it's outside
            if xor_result < 65 or xor_result > 90:
                xor_result = 65 + (xor_result % 26)
            
            # Convert the result back to a character and add to the result list
            result.append(chr(xor_result))
        
        # Join the list into a single string and return
        return ''.join(result)

    def xor_bruteforce_ioc(self):
        input_text = self.input1_text.toPlainText().upper()

        class Worker(QtCore.QObject):
            finished = QtCore.pyqtSignal()
            progress = QtCore.pyqtSignal(int)
            result = QtCore.pyqtSignal(str)

            def __init__(self, parent_class):
                super().__init__()
                self.parent_class = parent_class

            def run(self):
                start_time = time.time()
                matches_found = 0

                try:
                    with open("words_alpha.txt", 'r') as file:
                        words = [word.strip().upper() for word in file]
                except FileNotFoundError:
                    self.result.emit("\nError: words_alpha.txt not found!")
                    self.finished.emit()
                    return

                total_words = len(words)

                for i, word in enumerate(words):
                    if len(word) >= 3:
                        repetitions = (len(input_text) + len(word) - 1) // len(word)
                        repeated_key = (word * repetitions)[:len(input_text)]

                        result = CryptoToolGUI.xor_operation(input_text, repeated_key)
                        ioc = self.parent_class.calculate_ioc(result)

                        if 0.065 <= ioc <= 0.07:
                            matches_found += 1
                            self.result.emit(f"\nMatch found with key: {word}")
                            self.result.emit(f"\nKey repeated: {repeated_key}")
                            self.result.emit(f"\nResult: {result}")
                            self.result.emit(f"\nIoC: {ioc:.4f}\n")

                    if i % 100 == 0:
                        self.progress.emit(int((i / total_words) * 100))

                end_time = time.time()
                summary = f"\nBrute force completed. Found {matches_found} matches.\n"
                summary += f"Total time taken: {end_time - start_time:.2f} seconds\n"
                self.result.emit(summary)
                self.finished.emit()

        def start_thread():
            thread = QtCore.QThread()
            worker = Worker(self)
            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            worker.progress.connect(self.bf_progress_bar.setValue)
            worker.result.connect(self.output_text.append)
            worker.finished.connect(lambda: self.bf_progress_bar.setValue(100))

            self.thread = thread
            self.worker = worker

            thread.start()

        start_thread()

    def xor_bruteforce_freq(self):
        input_text = self.input1_text.toPlainText().upper()
        analyzer = LetterFrequencyAnalyzer()

        class Worker(QtCore.QObject):
            finished = QtCore.pyqtSignal()
            progress = QtCore.pyqtSignal(int)
            result = QtCore.pyqtSignal(str)

            def __init__(self, parent_class):
                super().__init__()
                self.parent_class = parent_class

            def run(self):
                start_time = time.time()
                matches_found = 0

                try:
                    with open("words_alpha.txt", 'r') as file:
                        words = [word.strip().upper() for word in file]
                except FileNotFoundError:
                    self.result.emit("\nError: words_alpha.txt not found!")
                    self.finished.emit()
                    return

                total_words = len(words)

                for i, word in enumerate(words):
                    if len(word) >= 3:
                        repetitions = (len(input_text) + len(word) - 1) // len(word)
                        repeated_key = (word * repetitions)[:len(input_text)]

                        result = self.parent_class.xor_operation(input_text, word)
                        result_analysis, is_close_match = analyzer.analyze_text(result)

                        if is_close_match:
                            matches_found += 1
                            self.result.emit(f"\nMatch found with key: {word}")
                            self.result.emit(f"\nKey repeated: {repeated_key}")
                            self.result.emit(f"\nResult: {result}")
                            self.result.emit(f"\n{result_analysis}\n")

                    if i % 100 == 0:
                        self.progress.emit(int((i / total_words) * 100))

                end_time = time.time()
                summary = f"\nBrute force completed. Found {matches_found} matches.\n"
                summary += f"Total time taken: {end_time - start_time:.2f} seconds\n"
                self.result.emit(summary)
                self.finished.emit()

        def start_thread():
            thread = QtCore.QThread()
            worker = Worker(self)
            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            worker.progress.connect(self.bf_progress_bar.setValue)
            worker.result.connect(self.output_text.append)
            worker.finished.connect(lambda: self.bf_progress_bar.setValue(100))

            self.thread = thread
            self.worker = worker

            thread.start()

        start_thread()

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
        results_window = QtWidgets.QDialog()
        results_window.setWindowTitle("Frequency Analysis Results")
        results_window.setGeometry(100, 100, 600, 400)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(results_window)
        
        # Create table widget
        table = QtWidgets.QTableWidget(results_window)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Character', 'English %', 'Input %', 'Difference'])
        table.setRowCount(len(self.english_freq))
        
        # Add data rows
        for row, char in enumerate(sorted(self.english_freq.keys())):
            eng_freq = self.english_freq[char]
            inp_freq = input_freq.get(char, 0)
            diff_val = abs(eng_freq - inp_freq)
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(char))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{eng_freq:.2f}"))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{inp_freq:.2f}"))
            table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{diff_val:.2f}"))
        
        layout.addWidget(table)
        
        # Add overall results label
        result_text = f"Overall difference: {diff:.2f}\n"
        result_text += "This text closely matches English letter frequency." if is_close_match else \
                      "This text does not closely match English letter frequency."
        result_label = QtWidgets.QLabel(result_text, results_window)
        layout.addWidget(result_label)
        
        results_window.exec_()
        
        # Return values for other functions to use
        summary = f"Frequency Analysis: Overall difference = {diff:.2f}"
        if is_close_match:
            summary += " (Matches English frequency)"
        return summary, is_close_match

def load_stylesheet():
    try:
        style_path = Path('theme.qss')  # Make sure this matches your stylesheet file name
        return style_path.read_text()
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CryptoToolGUI()
    window.show()
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)
    sys.exit(app.exec_())