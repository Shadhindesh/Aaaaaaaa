import os
import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import RIPEMD160  # Import RIPEMD160 from pycryptodome
import libsql_client

# Define the libsql connection URL and auth token
LIBSQL_URL = "libsql://btcadress-yaseen.turso.io"
AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MjgxODUxNDIsImlkIjoiMjE1YmNjNmMtMzNiYS00Nzg4LWI4ODYtMDEzZmRiN2EzOTFmIn0.D-xHGzQKEnP0985b2pWH4lpdTUZRmOUTY0j0Kfm12eqkh6D9ryMvWDtr3dUeMWWvtHve-4dD-xBxikDEQbEXAQ"

# Define the range for private keys
range_start = 0x40000000000000000
range_end = 0x7ffffffffffffffff  # Full range

# Step 1: Calculate Hash160 (RIPEMD160(SHA256(public_key))) using pycryptodome
def hash160(public_key):
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = RIPEMD160.new(sha256_hash).digest()  # Use pycryptodome for RIPEMD160
    return ripemd160_hash

# Step 2: Generate Bitcoin address from public key hash
def public_key_to_address(public_key_hash):
    version = b'\x00'  # Bitcoin mainnet version (P2PKH)
    checksum = hashlib.sha256(hashlib.sha256(version + public_key_hash).digest()).digest()[:4]
    address_bytes = version + public_key_hash + checksum
    return base58.b58encode(address_bytes).decode()  # Convert to Base58 string

# Step 3: Save to the database
def save_to_database(private_key_hex, bitcoin_address):
    query = '''INSERT INTO btc_addresses (private_key, address) VALUES (?, ?)'''
    data = (private_key_hex, bitcoin_address)
    execute_query(query, data)

# Step 4: Save checkpoint to the database
def save_checkpoint(last_processed_key):
    query = '''INSERT OR REPLACE INTO checkpoint (id, last_key) VALUES (1, ?)'''
    data = (last_processed_key,)
    execute_query(query, data)

# Step 5: Load checkpoint from the database
def load_checkpoint():
    query = '''SELECT last_key FROM checkpoint WHERE id = 1'''
    result = execute_query(query)
    if result:
        return int(result[0][0], 16)  # Convert from hex string back to integer
    return range_start

# Step 6: Initialize the database tables if they do not exist
def init_db():
    queries = [
        '''CREATE TABLE IF NOT EXISTS btc_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            private_key TEXT NOT NULL,
            address TEXT NOT NULL
          )''',
        '''CREATE TABLE IF NOT EXISTS checkpoint (
            id INTEGER PRIMARY KEY,
            last_key TEXT NOT NULL
          )'''
    ]
    for query in queries:
        execute_query(query)

# Helper function to execute queries against the database
def execute_query(query, data=None):
    with libsql_client.create_client_sync(LIBSQL_URL, auth_token=AUTH_TOKEN) as client:
        if data:
            result = client.execute(query, data)
        else:
            result = client.execute(query)
        return result.rows

# Step 7: Generate private key, public key, and address one by one
def generate_private_key_and_address():
    init_db()  # Initialize the database
    last_key = load_checkpoint()  # Start from the last saved checkpoint

    for priv_key_int in range(last_key, range_end):
        # Step 7.1: Generate private key from integer
        private_key = SigningKey.from_secret_exponent(priv_key_int, curve=SECP256k1)
        public_key = private_key.get_verifying_key().to_string('compressed')  # Compressed public key
        
        # Step 7.2: Hash the public key to get the public key hash
        public_key_hash = hash160(public_key)
        
        # Step 7.3: Generate the Bitcoin address from the public key hash
        bitcoin_address = public_key_to_address(public_key_hash)
        
        # Step 7.4: Print the private key and corresponding Bitcoin address
        private_key_hex = hex(priv_key_int)
        print(f"Private Key (hex): {private_key_hex}")
        print(f"Bitcoin Address: {bitcoin_address}")
        print("-" * 60)
        
        # Step 7.5: Save the private key and address to the database
        save_to_database(private_key_hex, bitcoin_address)

        # Step 7.6: Save the checkpoint
        save_checkpoint(private_key_hex)

# Run the generator
generate_private_key_and_address()
