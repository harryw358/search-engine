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