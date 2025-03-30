import re
import sys
from pathlib import Path
from collections import Counter

def load_known_words(dictionary_path):
    """
    Load known words from a markdown file.
    
    Args:
        dictionary_path (str): Path to the known words markdown file
        
    Returns:
        set: Set of known words
    """
    known_words = set()
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract words from markdown content
            # This assumes words are listed one per line or separated clearly
            words = re.findall(r'\b[a-zA-Z]+\b', content)
            known_words = set(word.lower() for word in words)
        print(f"Loaded {len(known_words)} known words from dictionary.")
    except FileNotFoundError:
        print(f"Dictionary file not found: {dictionary_path}")
    except Exception as e:
        print(f"Error loading dictionary: {e}")
    
    return known_words

def find_unknown_words(text_path, known_words):
    """
    Find words in the text that are not in the known words set.
    
    Args:
        text_path (str): Path to the English text file
        known_words (set): Set of known words
        
    Returns:
        list: List of unknown words with their frequencies
    """
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract all words, ignoring punctuation and numbers
        all_words = re.findall(r'\b[a-zA-Z]+\b', content)
        
        # Convert to lowercase for comparison
        all_words_lower = [word.lower() for word in all_words]
        
        # Count word frequencies
        word_counter = Counter(all_words_lower)
        
        # Filter unknown words
        unknown_words = {word: count for word, count in word_counter.items() 
                         if word not in known_words}
        
        print(f"Total words in text: {len(all_words)}")
        print(f"Unique words in text: {len(word_counter)}")
        print(f"Unknown words found: {len(unknown_words)}")
        
        # Sort by frequency (most frequent first)
        sorted_unknown = sorted(unknown_words.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_unknown
        
    except FileNotFoundError:
        print(f"Text file not found: {text_path}")
        return []
    except Exception as e:
        print(f"Error processing text file: {e}")
        return []

def save_unknown_words(unknown_words, output_path):
    """
    Save unknown words to a file.
    
    Args:
        unknown_words (list): List of tuples (word, frequency)
        output_path (str): Path to save the output
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Unknown Words\n\n")
            f.write("| Word | Frequency |\n")
            f.write("|------|----------:|\n")
            for word, count in unknown_words:
                f.write(f"| {word} | {count} |\n")
        print(f"Unknown words saved to {output_path}")
    except Exception as e:
        print(f"Error saving unknown words: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python unknown_words_finder.py <english_text.txt> <knowed-words.md> [output.md]")
        return
    
    text_path = sys.argv[1]
    dictionary_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "unknown_words.md"
    
    known_words = load_known_words(dictionary_path)
    if not known_words:
        return
    
    unknown_words = find_unknown_words(text_path, known_words)
    if unknown_words:
        save_unknown_words(unknown_words, output_path)

if __name__ == "__main__":
    main()
