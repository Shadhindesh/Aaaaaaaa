import requests
import re
import os
from bs4 import BeautifulSoup
import time

# Step 1: Define the checkpoint system
CHECKPOINT_FILE = 'checkpoint.txt'
STARTER_FILE = 'starter.txt'
MAX_PAGE = 73786976294838207  # Set a reasonable maximum page limit
TARGET_ADDRESS = '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'  # Target address for matching

# Function to load the starting page from starter.txt
# Function to load the second line from starter.txt
def load_second_line():
    if os.path.exists(STARTER_FILE):
        with open(STARTER_FILE, 'r') as f:
            lines = f.readlines()
            try:
                return lines[2].strip() if len(lines) > 1 else None  # Return second line, or None if not available
            except IndexError:
                return None  # Return None if there's an issue
    return None
    
def load_checkpoint():
    start_page = load_second_line()  # Load start page from starter.txt
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            try:
                page = int(f.read().strip())
                if 1 <= page <= MAX_PAGE:  # Ensure the page is within a valid range
                    return page
            except ValueError:
                pass  # In case of error, return start_page
    return start_page  # Return the starting page if no checkpoint or invalid data

# Function to save checkpoint (save current page number)
def save_checkpoint(page):
    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(str(page))

# Step 2: Make the request to the target page
def fetch_page(page_number):
    url = f'https://hashkeys.space/67/?page={page_number}'  # Use the correct page number
    headers = {
        'authority': 'hashkeys.space',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.1.355250481.1728059291; _ga_K7CFDCYECE=GS1.1.1728059290.1.1.1728059310.0.0.0',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            print(f"Page {page_number} not found. Stopping the script.")
            return None  # Return None if the page does not exist
        else:
            raise Exception(f"Failed to fetch page {page_number}: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        return None  # Return None on network failure

# Step 3: Extract and process the target addresses using BeautifulSoup
def process_page(page_content, page_number):
    addresses = []
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find all divs containing the hex value and address
    for div in soup.find_all('div'):
        text = div.get_text(strip=True)
        # Regex to match Bitcoin addresses within the text
        matches = re.findall(r'(\b1[A-HJ-NP-Za-km-z1-9]{25,34}\b)', text)
        
        # Extract key hex values from the div text
        hex_matches = re.findall(r'([0-9a-fA-F]+)\s+([13][a-zA-Z0-9]{25,34})', text)

        for hex_value, address in hex_matches:
            addresses.append((hex_value.strip(), address.strip()))
            
            # Check if the extracted address matches the target address
            if address.strip() == TARGET_ADDRESS:
                save_data_to_txt(hex_value.strip(), address.strip(), page_number)
                print(f"Match found! Saved - Key Hex: {hex_value.strip()}, Address: {address.strip()}, Page: {page_number}")
                return True  # Return True indicating a match was found

    return bool(addresses)

# Step 4: Save the extracted data to a .txt file
def save_data_to_txt(key_hex, address, page_number):
    with open('target_data.txt', 'a') as f:
        f.write(f"Key Hex: {key_hex}, Address: {address}, Page: {page_number}\n")

# Main process loop
def main():
    page = load_checkpoint()  # Start from last checkpoint or start page
    
    while True:
        print(f"Fetching page {page}...")
        page_content = fetch_page(page)
        
        if page_content is None:
            print(f"No more valid pages to fetch. Waiting for 10 minutes before retrying.")
            time.sleep(600)  # Wait for 10 minutes before retrying
            continue
        
        if process_page(page_content, page):
            print(f"Target address found on page {page}. Saving and stopping.")
            save_checkpoint(page)
            break  # Stop if match is found
        
        save_checkpoint(page)  # Save after processing the current page
        print(f"No target address found on page {page}. Moving to the next page.")
        page += 1  # Move to the next page

        if page > MAX_PAGE:  # Stop if the page exceeds the maximum limit
            print("Reached maximum page limit. Waiting for 10 minutes before restarting.")
            time.sleep(600)  # Wait for 10 minutes before restarting
            page = load_start_page()  # Reset the page number if it exceeds the limit

if __name__ == "__main__":
    main()
