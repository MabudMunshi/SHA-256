import math

def generate_ascii_table():
    return {i: chr(i) for i in range(128)}

def print_ascii_table(ascii_table):
    output = "ASCII Code | Character\n----------------------"
    for code, char in ascii_table.items():
        output += f"\n{code:10} | {char}"
    return output

def convert_to_ascii_and_binary(input_string):
    ascii_values = [ord(char) if ord(char) < 128 else 63 for char in input_string]
    binary_values = [format(value, '08b') for value in ascii_values]
    return ascii_values, binary_values

def to_binary_string(input_string):
    _, binary_values = convert_to_ascii_and_binary(input_string)
    return ''.join(binary_values)

def pad_to_512_bits(binary_string):
    original_length = len(binary_string)
    length_in_bits = format(original_length, '064b')  # 64-bit representation of the length
    padded_binaries = []

    while binary_string:
        if len(binary_string) >= 448:
            block_data = binary_string[:448]
            binary_string = binary_string[448:]
        else:
            block_data = binary_string
            binary_string = ""

        if len(block_data) < 448:
            block_data += '1' + '0' * (448 - len(block_data) - 1)

        padded_binary = block_data + length_in_bits
        padded_binaries.append(padded_binary)

    return padded_binaries

def split_to_words(block):
    return [block[i:i+32] for i in range(0, 512, 32)]

def right_rotate(value, bits):
    return ((value >> bits) | (value << (32 - bits))) & 0xFFFFFFFF

def sha256_sigma0(value):
    return right_rotate(value, 7) ^ right_rotate(value, 18) ^ (value >> 3)

def sha256_sigma1(value):
    return right_rotate(value, 17) ^ right_rotate(value, 19) ^ (value >> 10)

def generate_words(words):
    for t in range(16, 64):
        sigma0 = sha256_sigma0(words[t - 15])
        sigma1 = sha256_sigma1(words[t - 2])
        new_word = (words[t - 16] + sigma0 + words[t - 7] + sigma1) & 0xFFFFFFFF
        words.append(new_word)
    return words

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def first_n_primes(n):
    primes = []
    num = 2
    while len(primes) < n:
        if is_prime(num):
            primes.append(num)
        num += 1
    return primes

def generate_keys():
    primes = first_n_primes(64)
    keys = []
    for prime in primes:
        cube_root = prime ** (1/3)
        fractional_part = cube_root - int(cube_root)
        key = int(fractional_part * (2**32))
        keys.append(format(key, '08x'))  # Convert to 8-character hexadecimal string
    return keys

def generate_initial_hash_values():
    primes = first_n_primes(8)
    initial_hash_values = []
    for prime in primes:
        square_root = math.sqrt(prime)
        fractional_part = square_root - int(square_root)
        initial_hash_value = int(fractional_part * (2**32))
        initial_hash_values.append(format(initial_hash_value, '08x'))  # 8-character hexadecimal string
    return initial_hash_values

def sha256_compression_round(a, b, c, d, e, f, g, h, w, k):
    s1 = (right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25))
    ch = (e & f) ^ ((~e) & g)
    temp1 = (h + s1 + ch + k + w) & 0xFFFFFFFF
    s0 = (right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22))
    maj = (a & b) ^ (a & c) ^ (b & c)
    temp2 = (s0 + maj) & 0xFFFFFFFF

    new_h = g
    new_g = f
    new_f = e
    new_e = (d + temp1) & 0xFFFFFFFF
    new_d = c
    new_c = b
    new_b = a
    new_a = (temp1 + temp2) & 0xFFFFFFFF

    return new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h

def sha256_process_block(h, words, keys, rounds_output):
    a, b, c, d, e, f, g, h0 = h
    for t in range(64):
        a, b, c, d, e, f, g, h0 = sha256_compression_round(a, b, c, d, e, f, g, h0, words[t], int(keys[t], 16))
        rounds_output.append((a, b, c, d, e, f, g, h0))
    return a, b, c, d, e, f, g, h0

def main():
    output = ""
    ascii_table = generate_ascii_table()
    ascii_table_output = print_ascii_table(ascii_table)
    output += f"ASCII Table:\n{ascii_table_output}\n"
    
    user_input = input("Enter your message: ")
    ascii_values, binary_values = convert_to_ascii_and_binary(user_input)
    
    output += "\nInput to ASCII and Binary:\nCharacter | ASCII Value | Binary Representation\n----------------------------------------------"
    for char, ascii_val, binary_val in zip(user_input, ascii_values, binary_values):
        output += f"\n{char:9} | {ascii_val:11} | {binary_val}"
    
    binary_string = to_binary_string(user_input)
    padded_binaries = pad_to_512_bits(binary_string)

    for i, block in enumerate(padded_binaries):
        output += f"\n\nBlock {i + 1} (512 bits): {block}\nData bits (448 bits): {block[:448]}\nMessage length (64 bits): {block[448:]}\n"

        words = split_to_words(block)
        words = [int(word, 2) for word in words]  # Convert binary strings to integers
        words = generate_words(words)
        for j, word in enumerate(words):
            output += f"\nW{j}: {format(word, '032b')}"

    keys = generate_keys()
    for i, key in enumerate(keys):
        output += f"\nKey-{i}: {key}"

    initial_hash_values = generate_initial_hash_values()
    h = [int(h, 16) for h in initial_hash_values]
    for i, value in enumerate(h):
        output += f"\nh{i}: {format(value, '08x')}"

    rounds_output = []

    # Process each padded binary block
    for block in padded_binaries:
        words = split_to_words(block)
        words = [int(word, 2) for word in words]
        words = generate_words(words)
        h = sha256_process_block(h, words, keys, rounds_output)

    output += f"\n\nRound Outputs:"
    for i, round_output in enumerate(rounds_output):
        output += f"\nRound {i}: " + ' '.join(format(x, '08x') for x in round_output)

    # Convert the final hash values to hexadecimal
    final_hash = ''.join(format(x, '08x') for x in h)
    output += f"\n\nFinal Hash: {final_hash}"

    # Store output in a variable instead of printing
    stored_output = output
    print(stored_output)

if __name__ == "__main__":
    main()
