import sys
from src.crawler import Crawler

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

                print("[Stub] Building and saving the index to data/.")
                
            elif command == "load":
                # MVP Placeholder: Call your file loading logic here later
                print("[Stub] Executing 'load': Loading index from data/ file...")
                
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