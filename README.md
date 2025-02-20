# Welcome to K4TOOLS

A compact package where the user can do a variety of **string manipulation and operations** related to the infamous Kryptos cypher.


## Two string calculations

It is suspected that K4 might be a two layer cipher. Two main reversible operations are implemented: XOR (based on 5 bit decimal alphabet position) and Modular subtraction (based on ASCII).

## Single string analysis and manipulation

A variety of commonly used string analysis and manipulation is supported:
- IoC (English).
	- Tells you the IoC of the input cypher. It will notify if the value is close to English (0.065), which might indicate that the text has been transposed.
- Transposition.
	- Transposes each character (n) positions based on the provided alphabet.
- Reversion.
	- Reverses the string.
- Conversion to Morse code.
	 - Converts the string to Morse code.
- Conversion and translation of inversed morse ("OBKR = "SJRK").
- String Matrix
	- Splits and combines the string based on its divisors, it outputs all possible results.
- Frequency Analysis
	- It determines if the cypher character frequency is similar to English, which might indicate that the text has been transposed.

## Columnar Transposition

Added the ability to present the chypertext in a matrix form (row and column).
- Columnar transposition
  	- Ability to rearrange the column order based on their indices.
- The output string from the original matrix and the transposed one is presented either from leftmost column to right or viceversa depending on user preference. Row based output is also implemented.
  
![image](https://github.com/user-attachments/assets/8ba84f74-d06a-45b0-b393-e5c424578470)

## Vigenère Brute Force attacks

Using a couple large dictionary of English words (words_alpha.txt and words.txt), it will brute force until one of the input plain text words is found on the plaintext.

The vigenère alphabet can be defined by the user.

The brute force succesfully decripts, for example, K2 in under 4 seconds knowing one of the plaintext words.

	K2: EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
	Alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ
	Plain Text: SHADING
	Ouput: Found a match! Key: PALIMPSEST
			Attempts: 223848
			Time taken: 3.74 seconds
			Found match: SHADING
			Plaintext: BETWEENSUBTLE*SHADING*ANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION
	
A brute force based on IoC is also implemented, if the string is close to the user defined range (recommended to use the English IoC (between 0.06 and 0.07)), it will be output for further analysis.

**Useful strings** (strings.txt) contains relevant strings for quick copy paste into the GUI.

## Ideas are welcomed!
The GUI is a work in progress, do you have an idea or suggestion? Feel free to contact me so it can be implemented.
