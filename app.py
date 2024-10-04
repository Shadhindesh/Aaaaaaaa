import requests
from bs4 import BeautifulSoup
import time

# Function to fetch keys and addresses
def fetch_keys():
    # Replace with your actual cURL URL
    url = 'https://privatekeys.pw/keys/bitcoin/random/puzzle/67'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'https://privatekeys.pw/keys/bitcoin-gold/random/puzzle/67'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table and extract keys and addresses
    table = soup.find('table', class_='table')
    rows = table.find_all('tr')[1:]  # Skip the header row

    return rows

# Function to check for matches and save them
def check_for_matches(rows, target_address):
    found = False  # Variable to track if the address is found
    matches = []  # List to store matches

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            private_key = cols[0].text.strip()
            addresses = [a.text.strip() for a in cols[1].find_all('span', class_='hover')]
            
            print(f'Private Key: {private_key}')
            print(f'Addresses: {addresses}')
            
            # Check if the target address matches any of the extracted addresses
            if target_address in addresses:
                found = True
                matches.append(f'Match found: {target_address} with Private Key: {private_key}')
                print(matches[-1])  # Print the last match found

    return found, matches

# Function to save matches to a text file
def save_matches_to_file(matches):
    with open('matches.txt', 'w') as f:
        for match in matches:
            f.write(match + '\n')

# Function to upload to Gofile
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

# Infinite loop
while True:
    # Target address to check against
    target_address = '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'
    
    # Fetch keys and addresses
    rows = fetch_keys()

    # Check for matches
    found, matches = check_for_matches(rows, target_address)

    if not found:
        print(f'No matches found for the address: {target_address}')
    else:
        # Save matches to a text file
        save_matches_to_file(matches)

        # API token and folder ID for Gofile
        api_token = 'ttoDCTma1RmNbzvAH6GG0QJ8tmDNexNi'
        folder_id = 'e0d60535-b34f-4ede-a90d-d3819f30b6ee'
        
        # Upload the matches.txt file
        upload_to_gofile('matches.txt', api_token, folder_id)

     # Adjust this as needed
