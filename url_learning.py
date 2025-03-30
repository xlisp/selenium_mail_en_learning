from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import string
import os

def extract_unknown_words(url, dictionary_path):
    """
    Extracts all unknown words from a webpage by comparing against a local dictionary.
    
    Args:
        url (str): The URL of the webpage to analyze
        dictionary_path (str): Path to the known words file
        
    Returns:
        list: List of unknown words found on the webpage
    """
    # Load known words from dictionary file
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        known_words = set(word.strip().lower() for word in f.readlines())
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Initialize webdriver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Trying alternative method...")
        driver = webdriver.Chrome(options=chrome_options)
    
    # Load the webpage
    print(f"Accessing URL: {url}")
    driver.get(url)
    
    # Extract text content from the page
    page_text = driver.page_source
    driver.quit()
    
    # Process the text to extract words
    # Remove HTML tags
    text_content = re.sub(r'<[^>]+>', ' ', page_text)
    
    # Remove punctuation and convert to lowercase
    translator = str.maketrans('', '', string.punctuation)
    text_content = text_content.translate(translator).lower()
    
    # Split into words and remove empty strings
    all_words = [word for word in text_content.split() if word]
    
    # Get unique words
    unique_words = set(all_words)
    
    # Find unknown words (words not in the dictionary)
    unknown_words = [word for word in unique_words if word.isalpha() and word not in known_words]
    
    # Sort alphabetically
    unknown_words.sort()
    
    return unknown_words

def save_unknown_words(unknown_words, output_path):
    """
    Saves the list of unknown words to a file.
    
    Args:
        unknown_words (list): List of unknown words
        output_path (str): Path to save the output file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in unknown_words:
            f.write(word + '\n')

def main():
    # Configuration
    url = input("Enter the URL to analyze: ")
    dictionary_path = "knowed-words.md"
    output_path = "unknown-words.txt"
    
    # Check if dictionary file exists
    if not os.path.exists(dictionary_path):
        print(f"Error: Dictionary file '{dictionary_path}' not found.")
        return
    
    # Extract unknown words
    print("Extracting words from webpage...")
    unknown_words = extract_unknown_words(url, dictionary_path)
    
    # Save results
    save_unknown_words(unknown_words, output_path)
    
    # Print summary
    print(f"\nFound {len(unknown_words)} unknown words.")
    print(f"Results saved to '{output_path}'")
    
    # Print preview of unknown words
    if unknown_words:
        preview_limit = min(10, len(unknown_words))
        print(f"\nPreview of first {preview_limit} unknown words:")
        for i in range(preview_limit):
            print(f"  - {unknown_words[i]}")
        
        if len(unknown_words) > preview_limit:
            print(f"  ... and {len(unknown_words) - preview_limit} more")

if __name__ == "__main__":
    main()
