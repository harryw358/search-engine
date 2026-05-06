import json
import os
import string
import re

class Indexer:
    def __init__(self, index_file_path="data/index.json"):
        """
        Initialises the Indexer with the target path for the index file.
        """

        self.index_file_path = index_file_path
        self.inverted_index = {}

    def build_index(self, crawled_data):
        """
        Takes the crawled data, tokenises the text, and builds the inverted index.
        """
        self.inverted_index = {}
        for page in crawled_data:
            url = page['url']
            text = page['text']

            # Convert to lowercase.
            text = text.lower()

            # Replace non-alphanumeric characters with a space.
            clean_text = re.sub(r"[^\w\s]", "", text.lower())

            # Split the text into individual words.
            words = clean_text.split()

            for position, word in enumerate(words):
                if word not in self.inverted_index:
                    self.inverted_index[word] = {}

                if url not in self.inverted_index[word]:
                    # Store frequency and list of positions.
                    self.inverted_index[word][url] = {
                        'frequency': 0,
                        'positions': []
                    }

                self.inverted_index[word][url]['frequency'] += 1
                self.inverted_index[word][url]['positions'].append(position)

        print(f"Index built successfully with {len(self.inverted_index)} unique words.")
        return self.inverted_index
            
    def save_index(self):
        """
        Saves the inverted index to a single JSON file.
        """   
        # Ensure the data/ directory exists.
        os.makedirs(os.path.dirname(self.index_file_path), exist_ok=True)

        with open(self.index_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.inverted_index, f, indent=4)

        print(f"Index saved successfully to {self.index_file_path}")

    def load_index(self):
        """
        Loads the inverted index from the JSON file on the file system.
        """
        if not os.path.exists(self.index_file_path):
            print(f"Error: Index file not found at {self.index_file_path}. Please run 'build' first.")
            return False
        
        try:
            with open(self.index_file_path, 'r', encoding='utf-8') as f:
                self.inverted_index = json.load(f)

            print(f"Index successfully loaded from {self.index_file_path}")
            print(f"Loaded {len(self.inverted_index)} unique words into memory.")
            return True
        
        except json.JSONDecodeError:
            print(f"Error: {self.index_file_path} is corrupted or not a valid JSON file.")
            return False