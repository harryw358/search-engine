import sys
from src.crawler import Crawler
from src.indexer import Indexer

def main():
    print("==================================")
    print("  COMP3011 Search Engine Tool")
    print("==================================")
    print("Available commands:")
    print("  build        - Crawl website and build index")
    print("  load         - Load index from file")
    print("  print <word> - Print inverted index for a specific word")
    print("  find <query> - Find pages containing the search terms")
    print("  exit/quit    - Close the application")
    print("================================\n")

    # Instantiate the indexer once before the main loop starts so memory persists across different commands.
    indexer = Indexer()

    # The main CLI loop
    while True:
        try:
            # Get user input and strip leading/trailing whitespace
            user_input = input("> ").strip()
            
            # Ignore empty inputs
            if not user_input:
                continue
            
            # Split the input into the command and the arguments
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # Route to the correct command logic
            if command == "build":
                print("Executing 'build': Crawling https://quotes.toscrape.com/ and building index...")

                # Instantiate and call the crawler logic.
                crawler = Crawler()
                crawled_data = crawler.crawl()

                if crawled_data:
                    print(f"\nSuccess! Scraped {len(crawled_data)} pages.")

                    indexer.build_index(crawled_data)
                    indexer.save_index()

                
            elif command == "load":
                print("Executing 'load': Loading index from data/ file...")
                indexer.load_index()
                
            elif command == "print":
                if not args:
                    print("Error: Please provide a word to print (e.g., 'print nonsense').")
                else:
                    # MVP Placeholder: Call your index retrieval logic here
                    print(f"[Stub] Executing 'print': Fetching index entries for the word '{args}'...")
                    
            elif command == "find":
                if not args:
                    print("Error: Please provide a query to find (e.g., 'find good friends').")
                else:
                    # MVP Placeholder: Call your search logic here
                    print(f"[Stub] Executing 'find': Searching for pages containing '{args}'...")
                    
            elif command in ["exit", "quit"]:
                print("Exiting search tool. Goodbye!")
                sys.exit(0)
                
            else:
                print(f"Unknown command: '{command}'. Please use build, load, print, or find.")

        except KeyboardInterrupt:
            print("\nExiting search tool. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()