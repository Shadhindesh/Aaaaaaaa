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

# Function to check the balance of an Ethereum address using various blockchain APIs
def check_balance(eth_address, blockchain):
    if blockchain == "arbitrum":
        url = "https://arb1.arbitrum.io/rpc"
    elif blockchain == "avalanche":
        url = "https://api.avax.network/ext/bc/C/rpc"
    elif blockchain == "base":
        url = "https://mainnet.base.org"
    elif blockchain == "bnb":
        url = "https://bsc-dataseed.binance.org/"
    elif blockchain == "merlin":
        url = "https://rpc.merlinchain.io"  # Replace with the correct Merlin RPC URL
    elif blockchain == "linea":
        url = "https://rpc.linea.build"  # Replace with the correct Linea RPC URL
    elif blockchain == "kusama":
        url = "https://1rpc.io/eth"  # Replace with the correct Kusama RPC URL
    elif blockchain == "zksyncera":
        url = "https://zksync2-mainnet.zksync.io"  # Replace with the correct zkSync Era RPC URL
    else:
        print(f"Unsupported blockchain: {blockchain}")
        return 0

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [eth_address, "latest"],
        "id": 1
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        balance_wei = int(response.json().get('result', 0), 16)
        return balance_wei / 1e18  # Convert wei to ether
    return 0

# Function to upload the private key and address information to GoFile
def upload_to_gofile(file_path, api_token, folder_id):
    upload_url = 'https://store1.gofile.io/uploadFile'
    with open(file_path, 'rb') as file:
        files = {'file': file}
        headers = {"Authorization": f"Bearer {api_token}"}
        data = {"folderId": folder_id}

        response = requests.post(upload_url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                print(f"File successfully uploaded: {result['data']['downloadPage']}")
            else:
                print(f"Error during upload: {result['status']}")
        else:
            print(f"Failed to upload file, status code: {response.status_code}")
        
        # Sleep for 2 seconds after each upload
        time.sleep(2)

# Main function to continuously generate Ethereum addresses and check for balances
def main(file_path, api_token, folder_id):
    blockchains = ["arbitrum", "avalanche", "base", "bnb", "merlin", "linea", "kusama", "zksyncera"]  # Added new blockchains
    while True:  # Infinite loop
        private_key, eth_address = generate_eth_address()

        for blockchain in blockchains:
            balance = check_balance(eth_address, blockchain)
            print(f"Blockchain: {blockchain}, Private Key: {private_key}, Address: {eth_address}, Balance: {balance} ETH")

            # If a balance is found, write private key, address, and balance to the file
            if balance > 0:
                with open(file_path, 'w') as f:  # Write mode to create a new file
                    f.write(f"Private Key: {private_key}, Address: {eth_address}, Balance: {balance} ETH\n")
                    f.write(f"*** Match found! Address: {eth_address} has a balance of {balance} ETH ***\n")

                # Upload the file to GoFile
                upload_to_gofile(file_path, api_token, folder_id)

        # Sleep for a short time between address generations
        time.sleep(0.5)

if __name__ == "__main__":
    output_file = "eth_output.txt"  # File to save the output
    api_token = 'ttoDCTma1RmNbzvAH6GG0QJ8tmDNexNi'  # Replace with your GoFile API token
    folder_id = 'e0d60535-b34f-4ede-a90d-d3819f30b6ee'  # Replace with your GoFile folder ID

    print("Starting infinite address generation...")
    main(output_file, api_token, folder_id)
