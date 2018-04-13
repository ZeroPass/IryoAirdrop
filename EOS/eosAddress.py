import argparse
from binascii import hexlify, unhexlify

import hashlib
import binascii

b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

addr_prefix = "EOS"

#base58 encode function
def encode(b):
    """Encode bytes to a base58-encoded string"""

    # Convert big-endian bytes to integer
    n = int(b, 16)

    # Divide that integer into bas58
    res = []
    while n > 0:
        n, r = divmod (n, 58)
        res.append(b58_digits[r])
    res = ''.join(res[::-1])

    # Encode leading zeros as base58 zeros
    import sys
    czero = b'\x00'
    if sys.version > '3':
        # In Python3 indexing a bytes returns numbers, not characters.
        czero = 0
    pad = 0
    for c in b:
        if c == czero: pad += 1
        else: break
    return b58_digits[0] * pad + res

#base58 decode function
def decode(s):
    """Decode a base58-encoding string, returning bytes"""
    if not s:
        return b''

    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        if c not in b58_digits:
            raise Exception('Character %r is not a valid base58 character' % c)
        digit = b58_digits.index(c)
        n += digit

    # Convert the integer to bytes
    h = '%x' % n
    if len(h) % 2:
        h = '0' + h
    res = unhexlify(h.encode('utf8'))

    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == b58_digits[0]: pad += 1
        else: break
    return hexlify(b'\x00' * pad + res).decode('utf8')

def checksum(hexstr):
    h = hashlib.new('ripemd160')
    h.update(binascii.unhexlify(hexstr))
    return h.hexdigest()[0:8]
    
def make_address(pubkey):
    chksum = checksum(pubkey)
    addr = encode(pubkey + chksum)
    return addr_prefix + addr

def verify_address(addr):
    try:
        if addr.find(addr_prefix) != 0:
            return False

        hex_addr = decode(addr[len(addr_prefix):])
        pubkey = hex_addr[:len(hex_addr) -8]
        chksum = hex_addr[-8:]

        return checksum(pubkey) == chksum
    except Exception as e:
        return False
