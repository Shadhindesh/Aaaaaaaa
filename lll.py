from web3 import Web3
from eth_account import Account
from tronapi import Tron
from bit import Key
from solana.rpc.api import Client as SolanaClient
from near_api import NearClient, NearAccount
from near_api.signer import InMemorySigner
from near_api.utils import KeyPair
from ton import TonLibWrapper
import requests
from mnemonic import Mnemonic  # Import the mnemonic library

# Seed phrase generator
def generate_seed_phrase():
    mnemo = Mnemonic("english")  # Specify the language
    seed_phrase = mnemo.generate(strength=256)  # Generate a 24-word seed phrase
    return seed_phrase

# Ethereum/BSC address generation
def eth_bsc_address(seed_phrase):
    acct, _ = Account.from_mnemonic(seed_phrase)
    return acct.address

# TRON address generation
def tron_address(seed_phrase):
    tron = Tron(network='mainnet')
    return tron.create_account(is_text=True, private_key_format='raw', passphrase=seed_phrase)

# Bitcoin/Dogecoin/Litecoin address generation
def btc_bch_address(seed_phrase):
    key_btc = Key.from_mnemonic(seed_phrase, network='btc')
    return key_btc.address, key_btc.to_wif()

# Solana address generation
def solana_address(seed_phrase):
    keypair = KeyPair.from_mnemonic(seed_phrase)
    return keypair.public_key.toString()

# Dogecoin address generation
def dogecoin_address(seed_phrase):
    key_doge = Key.from_mnemonic(seed_phrase, network='doge')
    return key_doge.address

# Litecoin address generation
def litecoin_address(seed_phrase):
    key_ltc = Key.from_mnemonic(seed_phrase, network='ltc')
    return key_ltc.address

# NEAR address generation
def near_address(seed_phrase):
    keypair = KeyPair.from_mnemonic(seed_phrase)
    return keypair.public_key.toString()

# TON address generation
def ton_address(seed_phrase):
    ton_wrapper = TonLibWrapper()
    ton_wrapper.init()
    wallet = ton_wrapper.create_wallet(seed_phrase)
    return wallet.address

# Ethereum/BSC balance check
def eth_bsc_balance(address):
    infura_url = "https://mainnet.infura.io/v3/cafa7b07a8f14122a14ff4a5ab18e80e"  # Your Infura API Key
    web3 = Web3(Web3.HTTPProvider(infura_url))
    balance = web3.eth.get_balance(address)
    eth_balance = web3.fromWei(balance, 'ether')
    print(f"Ethereum/BSC Balance: {eth_balance} ETH")
    return eth_balance

# TRON balance check
def tron_balance(address):
    tron = Tron(network='mainnet')
    balance = tron.trx.get_balance(address)
    print(f"TRON Balance: {balance} TRX")
    return balance

# Bitcoin/Dogecoin/Litecoin balance check
def btc_balance(address):
    key_btc = Key(address)
    balance = key_btc.get_balance('btc')
    print(f"Bitcoin Balance: {balance} BTC")
    return balance

# Solana balance check
def solana_balance(address):
    solana_client = SolanaClient("https://api.mainnet-beta.solana.com")
    balance = solana_client.get_balance(address)
    sol_balance = balance['result']['value'] / 1e9  # Solana balance is in lamports, convert to SOL
    print(f"Solana Balance: {sol_balance} SOL")
    return sol_balance

# Dogecoin balance check
def dogecoin_balance(address):
    key_doge = Key(address)
    balance = key_doge.get_balance('doge')
    print(f"Dogecoin Balance: {balance} DOGE")
    return balance

# Litecoin balance check
def litecoin_balance(address):
    key_ltc = Key(address)
    balance = key_ltc.get_balance('ltc')
    print(f"Litecoin Balance: {balance} LTC")
    return balance

# NEAR balance check
def near_balance(address, seed_phrase):
    keypair = KeyPair.from_mnemonic(seed_phrase)
    signer = InMemorySigner.from_key_pair("test", "test", keypair)
    near_client = NearClient("https://rpc.mainnet.near.org")
    account = NearAccount(near_client, address, signer)
    balance = account.state()['amount']
    print(f"NEAR Balance: {balance} NEAR")
    return balance

# TON balance check
def ton_balance(address):
    ton_wrapper = TonLibWrapper()
    ton_wrapper.init()
    wallet = ton_wrapper.load_wallet(address)
    balance = wallet.get_balance()
    print(f"TON Balance: {balance} TON")
    return balance

# Function to generate addresses and check balances
def generate_and_check_balances(seed_phrase):
    print("\nGenerating addresses and checking balances...\n")

    # Ethereum/BSC
    eth_address = eth_bsc_address(seed_phrase)
    eth_bsc_balance(eth_address)

    # TRON
    tron_addr = tron_address(seed_phrase)
    tron_balance(tron_addr)

    # Bitcoin/Dogecoin/Litecoin
    btc_addr, _ = btc_bch_address(seed_phrase)
    btc_balance(btc_addr)

    # Solana
    sol_addr = solana_address(seed_phrase)
    solana_balance(sol_addr)

    # Dogecoin
    doge_addr = dogecoin_address(seed_phrase)
    dogecoin_balance(doge_addr)

    # Litecoin
    lite_addr = litecoin_address(seed_phrase)
    litecoin_balance(lite_addr)

    # NEAR
    near_addr = near_address(seed_phrase)
    near_balance(near_addr, seed_phrase)

    # TON
    ton_addr = ton_address(seed_phrase)
    ton_balance(ton_addr)

if __name__ == "__main__":
    # Generate a new seed phrase or input an existing one
    seed_phrase = generate_seed_phrase()
    print(f"Generated Seed Phrase: {seed_phrase}")

    # Generate addresses and check balances
    generate_and_check_balances(seed_phrase)