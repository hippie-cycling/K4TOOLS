# Welcome to K4TOOLS

A compact package where the user can do a variety of **string manipulation and operations** related to the infamous Kryptos cypher.


## Two string calculations

It is suspected that K4 might be a two layer cipher. XOR (based on 5 bit ASCII) has been implemented as it is a promising reversible operation that can be easily performed on paper. It also supports the main non-reversible boolean operations (AND, OR, NAND...).

Base 5 mod 26 addition of two strings is also supported.

## Single string analysis and manipulation

A variety of commonly used string analysis and manipulation is supported:
- IoC (English).
	- Tells you the IoC of the input cypher.
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
	- It determines if the cypher character frequency is similar to English. 

## Vigenère Brute Force attacks

Using a large dictionary of English words (words_alpha.txt), it will brute force until one of the input plain text words (**USE CAPS**)  is found on the plaintext.

The vigenère alphabet can be defined by the user.

The brute force succesfully decripts, for example, K2 in under 4 seconds.

	K2: EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
	Alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ
	Plain Text: SHADING
	Ouput: Found a match! Key: PALIMPSEST
			Attempts: 223848
			Time taken: 3.74 seconds
			Found match: SHADING
			Plaintext: BETWEENSUBTLE*SHADING*ANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION
	
A brute force based on IoC is also implemented, if the string is close to the English IoC (between 0.055 and 0.07), it will be output for further analysis. (The values can be tweeked in the K4TOOLS.py crack_thread function.)

**Useful strings** (strings.txt) contains relevant strings for quick copy paste into the GUI.

## Ideas are welcomed!
The GUI is a work in progress, do you have an idea or suggestion? Feel free to contact me so it can be implemented.
