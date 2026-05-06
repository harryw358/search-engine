# COMP3011 Search Engine Tool

[![Tests](https://github.com/harryw358/search-engine/actions/workflows/python-tests.yml/badge.svg)](https://github.com/harryw358/search-engine/actions)

## Project Overview and Purpose
This project is a command-line search engine tool developed for the COMP3011 Web Services and Web Data module. It is designed to crawl the target website ([http://quotes.toscrape.com/](http://quotes.toscrape.com/)), to extract quote text and their authors, and construct an inverted index.

The tool processes the extracted text by lowercasing and stripping punctuation using regular expressions, to ensure case-insensitive searching. It allows users to build and save the index to the file system, load it back into memory, view detailed statistics for individual words, and perform boolean AND searches for multi-word queries.

## Dependencies
This project requires Python 3.10+ and the following third-party libraries:
- ```requests```: For making HTTP requests and managing sessions during the crawling phase.
- ```beautifulsoup4```: For parsing HTML to extract quotes and navigate pagination.
- ```pytest```: For running the automated testing suite.

## Installation and Setup
1. **Clone the repository:**
```bash
git clone https://github.com/harryw358/search-engine.git
```
2. **Create and activate a virtual environment:**
  - **Mac/Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
  - **Windows**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3. **Install the dependencies:**
  Ensure you are in the root directory of the project (```search-engine/```), then run:
  ```bash
  pip install -r requirements.txt
  ```

## Command Usage Examples
To start the search engine's command line interface, ensure you are in the root directory of the project (```search-engine/)``` and run the following command:
```bash
python -m src.main
```
Once the interactive prompt (```>```) appears, you can use the following four main commands:
1. **```build```**
crawls the target website, whilst respecting a 6-second politeness window, to build the inverted index from the scraped text, and saves it to a single file at ```data/index.json```.
  - **Example:**
    ```plaintext
    > build
    ```
2. **```load```**
loads the previously saved inverted index from ```data/index.json``` into the application's memory so it can be queried. **You must run this (or ```build```) before attempting to search.**
  - **Example:**
    ```plaintext
    > load
    ```
3. **```print <word>```**
prints the inverted index statistics (URLs, frequencies, and word positions) for a speciic word. The search is case-insensitive.
  - **Example:**
    ```plaintext
    print einstein
    ```
4. **```find <query>```**
finds and returns a list of all pages containing the specified search terms. For multi-word queries, it performs a boolean AND search (returning only pages that contain _all_ the words.
  - **Examples:**
    ```plaintext
    > find indifference
    > find good friends
5. **```quit```** or **```exit```**
gracefully exists the search engine tool.

## Testing Instructions
This project uses ```pytest``` for comprehensive unit and integration testing, including mocks for network requests to ensure tests run quickly and reliably without hitting the live website.
To run the entire test suite covering the crawler, indexer, and search modules:
1. Ensure you are in the root directory of the project (```search-engine/```).
2. Run the following commmand:
   ```bash
   pytest tests/ -v
   ```

Should you wish to test each invidual component of the search engine independently, you can also run the following three commands:
1. ```bash
   pytest tests/test_crawler.py -v
   ```
2. ```bash
   pytest tests/test_indexer.py -v
   ```
3. ```bash
   pytest tests/test_searcher.py -v
   ```
### Continuous Integration:
This project is also configured with a GitHub Actions CI pipeline (```.github/workflows/python-tests.yml```). Every time code is pushed to the repository, the test suite is automatically executed in a cloud environment to ensure code stability and prevent regressions.
