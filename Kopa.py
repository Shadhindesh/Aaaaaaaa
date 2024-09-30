import os
import ecdsa
import requests
from Crypto.Hash import keccak
import time

# Function to calculate the Keccak-256 hash
def keccak256(data):
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

# Function to generate a random Ethereum address and its corresponding private key
def generate_eth_address():
    private_key = os.urandom(32)  # Secure random number generator
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    public_key = signing_key.get_verifying_key().to_string()
    eth_address = '0x' + keccak256(public_key)[-20:].hex()
    return private_key.hex(), eth_address

# Function to check the balance of an Ethereum address using Infura
def check_balance(eth_address, infura_url):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [eth_address, "latest"],
        "id": 1
    }
    response = requests.post(infura_url, json=payload)
    if response.status_code == 200:
        balance_wei = int(response.json().get('result', 0), 16)
        return balance_wei / 1e18  # Convert wei to ether
    return 0

# Main function to continuously generate Ethereum addresses and check for balances
def main(infura_url, file_path):
    while True:  # Infinite loop
        private_key, eth_address = generate_eth_address()
        balance = check_balance(eth_address, infura_url)

        # Print to console for every attempt
        print(f"Private Key: {private_key}, Address: {eth_address}, Balance: {balance} ETH")

        # If a balance is found, write private key, address, and balance to the file
        if balance > 0:
            with open(file_path, 'a') as f:  # Append mode
                f.write(f"Private Key: {private_key}, Address: {eth_address}, Balance: {balance} ETH\n")
                f.write(f"*** Match found! Address: {eth_address} has a balance of {balance} ETH ***\n")

        # Sleep for 0 seconds between requests (can be adjusted)
        time.sleep(0)

if __name__ == "__main__":
    infura_url = 'https://eth-mainnet.g.alchemy.com/v2/8PZtXCt8BWEo6kjKtbNbvvT7oWe_M6Q9'  # Replace with your Infura Project ID
    output_file = "eth_output.txt"  # File to save the output

    print(f"Starting infinite address generation...")
    main(infura_url, output_file)