import pytest
from src.search import Searcher

# --- Fixtures ---

@pytest.fixture
def sample_index():
    """Provides a small, fake inverted index for testing."""
    return {
        "einstein": {
            "http://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [5]}
        },
        "world": {
            "http://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [1, 10]},
            "http://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [4]}
        },
        "good": {
            "http://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [2]},
            "http://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [5]}
        },
        "friends": {
            "http://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [6]},
            "http://quotes.toscrape.com/page/3/": {"frequency": 1, "positions": [1]}
        }
    }

@pytest.fixture
def searcher(sample_index):
    """Provides a Searcher instance loaded with the mock data."""
    return Searcher(sample_index)

# --- Tests for print_word_index ---

def test_print_word_index_found_case_insensitive(searcher, capsys):
    """Tests that an existing word prints its statistics, regardless of case."""
    searcher.print_word_index("EinSteiN")
    captured = capsys.readouterr()
    assert "Index results for 'einstein'" in captured.out
    assert "URL: http://quotes.toscrape.com/page/1/" in captured.out

def test_print_word_index_multiple_pages(searcher, capsys):
    """Tests that a word found on multiple pages prints all URLs."""
    searcher.print_word_index("world")
    captured = capsys.readouterr()
    assert "http://quotes.toscrape.com/page/1/" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out

def test_print_word_index_not_found(searcher, capsys):
    """Tests the edge case where the requested word is not in the index."""
    searcher.print_word_index("python")
    captured = capsys.readouterr()
    assert "The word 'python' was not found" in captured.out

def test_print_word_index_empty_index(capsys):
    """Tests the edge case where the user hasn't loaded an index yet."""
    empty_searcher = Searcher({})
    empty_searcher.print_word_index("einstein")
    captured = capsys.readouterr()
    assert "Error: Index is empty" in captured.out

# --- Tests for find_query ---

def test_find_query_single_word(searcher, capsys):
    """Tests finding pages for a single existing word."""
    searcher.find_query("einstein")
    captured = capsys.readouterr()
    assert "Found 1 page(s)" in captured.out
    assert "http://quotes.toscrape.com/page/1/" in captured.out

def test_find_query_multi_word_intersection(searcher, capsys):
    """Tests finding pages that contain BOTH words (Boolean AND)."""
    # 'good' is on pages 1 and 2. 'friends' is on pages 2 and 3. 
    # The intersection should ONLY be page 2.
    searcher.find_query("good friends")
    captured = capsys.readouterr()
    assert "Found 1 page(s)" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out
    assert "http://quotes.toscrape.com/page/1/" not in captured.out

def test_find_query_multi_word_no_intersection(searcher, capsys):
    """Tests querying two words that exist in the index, but NEVER on the same page."""
    # 'einstein' is on page 1. 'friends' is on pages 2 and 3.
    searcher.find_query("einstein friends")
    captured = capsys.readouterr()
    assert "No pages found containing all search terms." in captured.out

def test_find_query_case_and_punctuation(searcher, capsys):
    """Tests query cleaning (lowercasing and punctuation removal)."""
    searcher.find_query("GOOD, friends!")
    captured = capsys.readouterr()
    # Should resolve exactly the same as "good friends"
    assert "Found 1 page(s)" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out

def test_find_query_missing_word(searcher, capsys):
    """Tests a multi-word query where one word does not exist at all."""
    searcher.find_query("einstein bananas")
    captured = capsys.readouterr()
    assert "No pages found containing all search terms." in captured.out

def test_find_query_empty_or_punctuation_only(searcher, capsys):
    """Edge Case: Tests a query that results in no words after stripping punctuation."""
    searcher.find_query("?!,.")
    captured = capsys.readouterr()
    assert "Error: Query contains no valid searchable words." in captured.out

def test_find_query_empty_index(capsys):
    """Edge Case: Tests searching when no index is loaded."""
    empty_searcher = Searcher({})
    empty_searcher.find_query("good friends")
    captured = capsys.readouterr()
    assert "Error: Index is empty" in captured.out