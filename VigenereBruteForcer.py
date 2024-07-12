import time

# Custom Vigenere alphabet
ALPHABET = "DYAHRBCEFGIJKLMNOPQSTUVWXZ"

def decrypt_vigenere(ciphertext, key):
    plaintext = ""
    key_length = len(key)
    
    for i, char in enumerate(ciphertext):
        if char == '?':
            plaintext += '?'
        elif char in ALPHABET:
            key_char = key[i % key_length]
            if key_char in ALPHABET:
                shift = ALPHABET.index(key_char)
                char_index = ALPHABET.index(char)
                decrypted_char = ALPHABET[(char_index - shift) % len(ALPHABET)]
                plaintext += decrypted_char
            else:
                plaintext += char  # If key character is not in ALPHABET, leave the ciphertext character as is
        else:
            plaintext += char
    
    return plaintext

def load_dictionary(file_path):
    with open(file_path, 'r') as file:
        return [word.strip().upper() for word in file if set(word.strip().upper()).issubset(set(ALPHABET))]

def crack_vigenere(ciphertext, dictionary):
    start_time = time.time()
    attempts = 0
    
    for key in dictionary:
        attempts += 1
        plaintext = decrypt_vigenere(ciphertext, key)
        
        if "BERLINCLOCK" in plaintext or "EASTNORTH" in plaintext:
            end_time = time.time()
            print(f"\nCracked! Key: {key}")
            print(f"Attempts: {attempts}")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            return "cracked", plaintext, key
        
        if attempts % 1000 == 0:
            print(f"Attempts: {attempts}, Current key: {key}")
    
    end_time = time.time()
    print(f"\nUnable to crack. Attempts: {attempts}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    return "not cracked", "", ""

def main():
    ciphertext = input("Enter the Vigenere ciphertext: ").upper()
    dictionary = load_dictionary("words_alpha.txt")
    
    print(f"Loaded dictionary with {len(dictionary)} valid words")
    print("Starting dictionary-based attack...")
    
    result, plaintext, key = crack_vigenere(ciphertext, dictionary)
    
    if result == "cracked":
        print(f"Cracked! Key: {key}")
        print(f"Plaintext: {plaintext}")
    else:
        print("Unable to crack the cipher.")

if __name__ == "__main__":
    main()