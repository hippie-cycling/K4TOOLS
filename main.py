from tkinter import *

def convert_to_opposite_morse():

    input = input_text.get("1.0", 'end-1c')
    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..'}

    morse_input = ''
    for char in input.upper():
        if char in morse_dict:
            morse_input += morse_dict[char] + ' '

    inverted_morse = ''
    for char in morse_input:
        if char == '.':
            inverted_morse += '-'
        elif char == '-':
            inverted_morse += '.'
        else:
            inverted_morse += char

    output = ''
    morse_dict = {value: key for key, value in morse_dict.items()}
    for morse in inverted_morse.split():
        if morse in morse_dict:
            output += morse_dict[morse]
        else:
            output += ' '
    opposite_morse_code = output.strip()

    out.insert("1.0", f"\nReversed Morse: {opposite_morse_code}")

def get_morse_code():
    input = input_text.get("1.0", 'end-1c')
    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',  'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', ' ': ' '
    }
    result = {}
    total_dots = 0
    total_dashes = 0
    for char in input.upper():
        if char in morse_dict:
            morse_code = morse_dict[char]
            dots = morse_code.count('.')
            dashes = morse_code.count('-')
            result[char] = f"{dots} dots, {dashes} dashes"
            total_dots += dots
            total_dashes += dashes
        else:
            result[char] = 'Invalid character'
    out.insert("1.0", f"\nDots: {total_dots}, Dashes:{total_dashes}")

def shift_string():
    input = input_text.get("1.0", 'end-1c')
    shifted = ""
    shift_amounts = [1, 2, 3, 4, 5, 1, 2, 3, 4]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" #"KRYPTOSABCDEFGHIJLMNQUVWXZ"
    for i, c in enumerate(input):
        if c.isupper():
            shift = shift_amounts[i % len(shift_amounts)]
            shifted_index = (alphabet.index(c) + shift) % len(alphabet)
            shifted_char = alphabet[shifted_index]
            shifted += shifted_char
        else:
            shifted += c
    out.insert("1.0", f"\nShifted by 5: {shifted}")

def ioc():
    input = input_text.get("1.0", 'end-1c')
    num = 0.0
    den = 0.0
    count_dict = {}  # Create an empty dictionary to store character frequencies
    for char in input:
        count_dict[char] = count_dict.get(char, 0) + 1  # Count the occurrences of each character

    for val in count_dict.values():  # Access the values of the dictionary
        i = val
        num += i * (i - 1)
        den += i

    if den == 0.0:
        ic = 0.0
    else:
        ic = num / (den * (den - 1))

    out.insert("1.0", f"\nIoC of {input}: {ic:.4f}")

def reverse():
    input = input_text.get("1.0", 'end-1c')
    reversed = input[::-1]
    out.insert("1.0", f"\nReversed output: {reversed}")

def transposition():
    input = input_text.get("1.0", 'end-1c')
    step = -5
    alphabets = "KRYPTOSABCDEFGHIJLNQUVWXZ"
    alph2 = alphabets.upper() 

    # lower case translation table
    t = str.maketrans(alphabets, alphabets[-step:]+alphabets[:-step])
    # upper case translation table
    t2 = str.maketrans(alph2, alph2[-step:]+alph2[:-step])
    # merge both translation tables
    t.update(t2)
    result = input.translate(t)
    out.insert("1.0", f"\n{result}")

def boolean_operations():
    op = operation.get()
    cypher = cypher_text.get("1.0", 'end-1c')
    dictionary = dictionary_text.get("1.0", 'end-1c')

    # Define the 5-bit ASCII conversion dictionary
    ascii_dict = {
        'A': '00001', 'B': '00010', 'C': '00011', 'D': '00100', 'E': '00101',
        'F': '00110', 'G': '00111', 'H': '01000', 'I': '01001', 'J': '01010',
        'K': '01011', 'L': '01100', 'M': '01101', 'N': '01110', 'O': '01111',
        'P': '10000', 'Q': '10001', 'R': '10010', 'S': '10011', 'T': '10100',
        'U': '10101', 'V': '10110', 'W': '10111', 'X': '11000', 'Y': '11001',
        'Z': '11010'
    }

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

    # Convert the result back to text using 5-bit ASCII conversion
    result_text = ''
    for i in range(0, len(result_binary), 5):
        chunk = result_binary[i:i+5]
        if chunk == '00000' or chunk == "11111":
            result_text += next(key for key, value in ascii_dict.items() if value == binary1[i:i+5])
        elif chunk in ascii_dict.values():
            result_text += next(key for key, value in ascii_dict.items() if value == chunk)
        else:
            result_text += next(key for key, value in ascii_dict.items() if value == binary1[i:i+5])

    out.insert("1.0", f"\nCalculated {op} output: {result_text}")

def base5_addition():
    cypher = cypher_text.get("1.0", 'end-1c')
    dictionary = dictionary_text.get("1.0", 'end-1c')

    base5_dict = {
        'A': '00', 'B': '01', 'C': '02', 'D': '03', 'E': '04',
        'F': '10', 'G': '11', 'H': '12', 'I': '13', 'J': '14',
        'K': '20', 'L': '21', 'M': '22', 'N': '23', 'O': '24',
        'P': '30', 'Q': '31', 'R': '32', 'S': '33', 'T': '34',
        'U': '40', 'V': '41', 'W': '42', 'X': '00', 'Y': '43',
        'Z': '44'
    }

    # Convert the input strings to base 5 numbers
    num1 = ''.join(base5_dict[char] for char in cypher)
    num2 = ''.join(base5_dict[char] for char in dictionary)

    # Perform addition modulo 5
    result = ''
    for digit1, digit2 in zip(num1, num2):
        sum_digits = (int(digit1) + int(digit2)) % 5
        result += str(sum_digits)

    # Convert the result back to letters
    letters = ''
    for i in range(0, len(result), 2):
        chunk = result[i:i+2]
        letter = next((key for key, value in base5_dict.items() if value == chunk), '?')
        letters += letter

    out.insert("1.0", f"\nBase 5 mod 26 addtition: {letters}")

def clear_output():
    out.delete("1.0", END)

root = Tk()
root.title("K4")

# Create a variable to store the selected value
selected_value = StringVar()

one_string_operation_frame = LabelFrame(root, text="One String Manipulation")
one_string_operation_frame.grid(row= 0, column=0, padx=5, pady=0)

input_label = Label(one_string_operation_frame, text="Input")
input_label.grid(row=0, column=0, padx=5)

input_text = Text(one_string_operation_frame, height=3, width=50, font=("Cambria", 8))
input_text.grid(row=1, column=0, padx=5, columnspan= 8)

layer_2_frame = LabelFrame(root, text="Two String Manipulation")
layer_2_frame.grid(row= 0, column=1, padx=5, pady=5)

output_frame = LabelFrame(root, text="Output")
output_frame.grid(row=1, column=0, padx=5, columnspan=2)

out = Text(output_frame, bg = "#88C0D0", height=10, width=105, font=("Cambria", 8))
out.grid(row=1, column=0, padx=5, pady=5)

cypher_label = Label(layer_2_frame, text="Input 1")
cypher_label.grid(row=1, column=0, padx=5)
dictionary_label = Label(layer_2_frame, text="Input 2")
dictionary_label.grid(row=3, column=0, padx=5)

cypher_text = Text(layer_2_frame, height=3, width=50, font=("Cambria", 8))
dictionary_text = Text(layer_2_frame, height=3, width=50, font=("Cambria", 8))
cypher_text.grid(row=2, column=0, padx=5, columnspan= 8)
dictionary_text.grid(row=4, column=0, padx=5, columnspan= 8)

operation_label = Label(layer_2_frame, text="Operation")
operation = StringVar()
values = ["AND", "OR", "NOT", "NAND", "NOR", "XOR"]
operation_combobox = OptionMenu(layer_2_frame, operation, *values)
operation_combobox.grid(row=5, column=0, padx=5)

button = Button(layer_2_frame, text="Calculate", command = boolean_operations)
button.grid(row=5, column=1, pady=5)

# Button
button_base5 = Button(layer_2_frame, text="Base 5 Addition", command = base5_addition)
button_base5.grid(row=5, column=2, pady=5)

button_reverse = Button(one_string_operation_frame, text="Reverse", command = reverse)
button_reverse.grid(row=3, column=0, pady=5)

ioc_button = Button(one_string_operation_frame, text="IoC", command = ioc)
ioc_button.grid(row=3, column=1, pady=5)

shift_string_button = Button(one_string_operation_frame, text="Transpose", command = shift_string)
shift_string_button.grid(row=3, column=2, pady=5)

morse_button = Button(one_string_operation_frame, text="Morse", command = get_morse_code)
morse_button.grid(row=3, column=3, pady=5)

morse_button = Button(one_string_operation_frame, text="Invert Morse", command = convert_to_opposite_morse)
morse_button.grid(row=3, column=4, pady=5)

clear_button = Button(output_frame, text="Clear", command = clear_output)
clear_button.grid(row=2, column=0, pady=5)



root.mainloop()

