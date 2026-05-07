import string
import re
import math
import difflib

class Searcher:
    def __init__(self, inverted_index):
        """
        Initialises the Searcher with the loaded inverted index.
        """
        self.inverted_index = inverted_index
        self.total_docs = self._calculate_total_docs()

    def _calculate_total_docs(self):
        """
        Helper method to count the total number of unique URLs in the index.
        """
        if not self.inverted_index:
            return 0
        urls = set()
        for word_data in self.inverted_index.values():
            urls.update(word_data.keys())
        return len(urls)

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
        Finds pages containing all words in the search query. Ranks by TF-IDF score.
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

        # Query Suggestions: Checks if any words are missing from the index and suggests similar words.
        missing_words = [word for word in words if word not in self.inverted_index]
        if missing_words:
            # Generate a suggestion and abort the search.
            for missing in missing_words:
                # Find the closest match in our dictionary of indexed words.
                matches = difflib.get_close_matches(missing, self.inverted_index.keys(), n=1, cutoff=0.7)

                if matches:
                    print(f"No results for '{missing}'. Did you mean: '{matches[0]}'?")
                else:
                    print(f"No pages found containing the term '{missing}'.")
            
            print("-" * (27 + len(query)) + "\n")
            return

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

        # Apply TF-IDF Ranking to the matched URLs.
        if matching_urls:
            url_scores = {}
            for url in matching_urls:
                score = 0
                for word in words:
                    tf = self.inverted_index[word][url]['frequency']
                    df = len(self.inverted_index[word])
                    # IDF formula: log10(Total Docs / Docs containing search word)
                    idf = math.log10(self.total_docs / df) if df > 0 else 0
                    score += tf * idf

                url_scores[url] = score

            # Sort URLs by their computed score in descending order.
            ranked_urls = sorted(url_scores.items(), key=lambda item: item[1], reverse=True)

            print(f"Found {len(ranked_urls)} page(s) containing the terms:")
            for url, score in ranked_urls:
                # Format the score to 4 decimal places.
                print(f"    - {url} (Score: {score:.4f})")
        else:
            print("No pages found containing all search terms.")

        print("-" * (27 + len(query)) + "\n")