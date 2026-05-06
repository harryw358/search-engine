import string
import re

class Searcher:
    def __init__(self, inverted_index):
        """
        Initialises the Searcher with the loaded inverted index.
        """
        self.inverted_index = inverted_index

    def print_word_index(self, word):
        """
        Prints the inverted index statistics for a particular word.
        """
        # Ensure the user has actually loaded the index first.
        if not self.inverted_index:
            print("Error: Index is empty. Please run 'load' or 'build' first.")
            return
        
        # Lowercase the search term to match the case-insensitive index.
        search_term = word.lower()

        if search_term in self.inverted_index:
            print(f"\n--- Index results for '{search_term}' ---")
            results = self.inverted_index[search_term]

            # Iterate through the pages where the word was found.
            for url, stats in results.items():
                frequency = stats['frequency']
                positions = stats['positions']
                print(f"URL: {url}")
                print(f"    Frequency: {frequency}")
                print(f"    Positions: {positions}")
            print("-" * (30 + len(search_term)) + "\n")
        else:
            print(f"The word '{word}' was not found in any indexed pages.")

    def find_query(self, query):
        """
        Finds pages containing all words in the search query.
        """
        if not self.inverted_index:
            print("Error: Index is empty. Please run 'load' or 'build' first.")
            return
        
        # 1. Clean the query.
        clean_query = re.sub(r"[^\w\s]", "", query.lower())
        words = clean_query.split()

        if not words:
            print("Error: Query contains no valid searchable words.")
            return
        
        print(f"\n--- Search results for '{query}' ---")

        # 2. Boolean AND search logic.
        first_word = words[0]

        # If the first word isn't in the index at all, the AND search fails immediately.
        if first_word not in self.inverted_index:
            print("No pages found containing all search terms.")
            print("-" * (27 + len(query)) + "\n")
            return
        
        # Start with the set of URLs for the first word.
        matching_urls = set(self.inverted_index[first_word].keys())

        # Intersect with the URL sets of all subsequent words in the query.
        for word in words[1:]:
            if word not in self.inverted_index:
                matching_urls = set() # A required word is missing, so no pages match
                break

            word_urls = set(self.inverted_index[word].keys())
            matching_urls = matching_urls.intersection(word_urls)

        # Print the results.
        if matching_urls:
            print(f"Found {len(matching_urls)} page(s) containing the terms:")
            for url in sorted(matching_urls): # Sort alphabetically for a cleaner output.
                print(f"    - {url}")
        else:
            print("No pages found containing all search terms.")

        print("-" * (27 + len(query)) + "\n")