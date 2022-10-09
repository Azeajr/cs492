# Assignment: CS 492 Homework 2
# Author: Antonio Zea Jr
# Description: Implementation of TEA Block encryption algorithm.

# Encryption function
def encrypt(plaintext, key, delta):
    # bitMask is used to make the variables overflow as if they were 32 bit
    # registers instead the unlimited size available in python3.
    bitMask = 0xFFFFFFFF

    # Split the plaintext into two registers
    L = (plaintext & (bitMask << 32)) >> 32
    R = plaintext & bitMask

    # Break the 128 bit key into 4 registers
    subKeys = []
    for i in range(4):
        subKeys.append((key & (bitMask << (32 * i))) >> (32 * i))

    sum = 0
    for i in range(32):
        # Took advantage of operator precedence instead of using parentheses
        sum = sum + delta & bitMask
        # Tried to use addition assignment but couldn't get it to work with the
        # bitMask to properly emulate overflow.
        L = L + (((R << 4 & bitMask) + subKeys[0]) & bitMask ^ (
            R + sum & bitMask) ^ ((R >> 5) + subKeys[1]) & bitMask) & bitMask
        R = R + (((L << 4 & bitMask) + subKeys[2]) & bitMask ^ (
            L + sum & bitMask) ^ ((L >> 5) + subKeys[3]) & bitMask) & bitMask

    # Putting together the two halves using bitwise or
    ciphertext = (L << 32) | (R)

    # print('Ciphertext:\t', hex(ciphertext))
    return ciphertext

# Decryption function


def decrypt(ciphertext, key, delta):
    # bitMask is used once again to emulate a 32-bit register and the overflow
    # that would occur
    bitMask = 0xFFFFFFFF

    # Split the ciphertext into two registers
    L = (ciphertext & (bitMask << 32)) >> 32
    R = ciphertext & bitMask

    # Break the 128 bit key into 4 registers
    subKeys = []
    for i in range(4):
        subKeys.append((key & (bitMask << (32 * i))) >> (32 * i))

    # Any operation that might cause overflow needs to be bit masked to emulate
    # the overflow
    sum = delta << 5 & bitMask
    for i in range(32):
        R = R - (((L << 4 & bitMask) + subKeys[2]) & bitMask ^ (
            L + sum & bitMask) ^ ((L >> 5) + subKeys[3]) & bitMask) & bitMask
        L = L - (((R << 4 & bitMask) + subKeys[0]) & bitMask ^ (
            R + sum & bitMask) ^ ((R >> 5) + subKeys[1]) & bitMask) & bitMask
        sum = sum - delta & bitMask

    # Putting together the two halves using bitwise or
    plaintext = (L << 32) | (R)
    return plaintext


# Encrypt using TEA in CBC mode.  In general I will subdivide the plaintext 
# into 64-bit blocks.  CBC starts with XORing the first block of plaintext with 
# an IV value.  That is then fed into TEA. The result is added to the 
# ciphertext and will be used in place of the IV in the following iterations of 
# the CBC algorithm.
def cbcEncrypt(plaintext, key, delta, iv):
    n, r = divmod(len(hex(plaintext))-2, 16)
    if (r > 0):
        n += 1

    bitMask = 0xFFFFFFFFFFFFFFFF
    ciphertext = 0x0

    for i in range(n):
        block = (plaintext & (bitMask << (64 * i))) >> (64 * i)
        intermediate = iv ^ block
        iv = encrypt(intermediate, key, delta)
        ciphertext = ciphertext << 64 | iv

    return ciphertext

# To decrypt in CBC mode, the process is essentially the reverse of the 
# encryption steps.  We start by passing the ciphertext into the TEA block 
# cipher.  Those results are then XORed with the same IV that was used to 
# encrypt. At this point, you have a block of plaintext.  After this phase, the 
# following phases have the following blocks of ciphertext take the place of 
# the IV and the process continues until all ciphertext blocks have been 
# decrypted.
def cbcDecrypt(ciphertext, key, delta, iv):
    n, r = divmod(len(hex(ciphertext))-2, 16)
    if (r > 0):
        n += 1

    bitMask = 0xFFFFFFFFFFFFFFFF
    plaintext = 0x0

    for i in range(n):
        block = (ciphertext & (bitMask << (64 * i))) >> (64 * i)
        intermediate = decrypt(block, key, delta) ^ iv
        iv = block
        plaintext = plaintext << 64 | intermediate

    return plaintext


key = int('0xBF6BBBCDEF00F000FEAFAFBFACCDEF01', 16)
delta = int('0x9E3779B9', 16)

plaintext = int('0x0FCB45670CABCDEF', 16)
print('Plaintext:\t\t\t', hex(plaintext))

ciphertext = encrypt(plaintext, key, delta)
print('Ciphertext:\t\t\t', hex(ciphertext))


decryptedCiphertext = decrypt(ciphertext, key, delta)
print('Decrypted ciphertext:\t\t', hex(decryptedCiphertext))

iv = 356

ciphertext = cbcEncrypt(plaintext, key, delta, iv)
print('Ciphertext (CBC Mode):\t\t', hex(ciphertext))
decryptedCiphertext = cbcDecrypt(ciphertext, key, delta, iv)
print('Decrypted ciphertext (CBC Mode):', hex(decryptedCiphertext))
