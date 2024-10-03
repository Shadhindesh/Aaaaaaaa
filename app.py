import hashlib
from Crypto.Hash import RIPEMD160
from ecdsa import SigningKey, SECP256k1
import base58
import sys
import time

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = RIPEMD160.new()
    h.update(data)
    return h.digest()

def hash160(data):
    return ripemd160(sha256(data))

def public_key_to_address(public_key):
    h160 = hash160(public_key)
    vh160 = b'\x00' + h160  # Version 0x00 for P2PKH
    checksum = sha256(sha256(vh160))[:4]
    return base58.b58encode(vh160 + checksum)

def private_key_to_wif(private_key):
    extended_key = b'\x80' + private_key  # '\x80' for mainnet WIF format
    checksum = sha256(sha256(extended_key))[:4]
    return base58.b58encode(extended_key + checksum)

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(32, byteorder='big')  # 32-byte private keys for Bitcoin

def solve_puzzle(target_address, start_range, end_range):
    print(f"Trying private key range: {hex(start_range)} to {hex(end_range)}")
    
    target_address_bytes = base58.b58decode(target_address)[:-4]  # Decode target address and remove checksum
    
    for private_key in range(start_range, end_range + 1):
        private_key_bytes = int_to_bytes(private_key)
        
        # Generate public key
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        public_key = sk.get_verifying_key().to_string("compressed")  # Compressed public key
        
        # Generate address
        address = public_key_to_address(public_key)
        
        # Print each attempt on the same line
        output = f"Trying private key: {private_key_bytes.hex()} | Address: {address.decode()}"
        sys.stdout.write('\r' + output)  # Overwrite the current line
        sys.stdout.flush()
        
        if address == target_address.encode():  # Compare the full base58-encoded address
            print()  # Print a new line before showing the result
            return private_key_bytes, private_key_to_wif(private_key_bytes)
    
    print()  # Ensure a new line at the end of the loop
    return None, None

# Target address and range
target_address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
start_range = 0x40000000000000000
end_range = 0x50000000000000000

print("Starting puzzle solver...")
private_key, wif = solve_puzzle(target_address, start_range, end_range)

if private_key:
    print(f"\nFound matching private key: {private_key.hex()}")
    print(f"WIF format: {wif.decode()}")
else:
    print("No matching private key found in the given range.")
