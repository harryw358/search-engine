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
    assert "(Score:" in captured.out # Verify the score is printed

def test_find_query_ranking_order(searcher, capsys):
    """Tests that TF-IDF correctly ranks pages with higher frequencies first."""
    # 'world' appears twice on page 1, and once on page 2.
    # Therefore, page 1 MUST be printed before page 2.
    searcher.find_query("world")
    captured = capsys.readouterr()
    
    # Get the index of where each URL appears in the standard output
    pos_page1 = captured.out.find("http://quotes.toscrape.com/page/1/")
    pos_page2 = captured.out.find("http://quotes.toscrape.com/page/2/")
    
    assert pos_page1 != -1 and pos_page2 != -1, "Both pages should be in the output"
    assert pos_page1 < pos_page2, "Page 1 should be ranked higher than Page 2"

def test_find_query_multi_word_intersection(searcher, capsys):
    """Tests finding pages that contain BOTH words (Boolean AND)."""
    searcher.find_query("good friends")
    captured = capsys.readouterr()
    assert "Found 1 page(s)" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out
    assert "http://quotes.toscrape.com/page/1/" not in captured.out

def test_find_query_multi_word_no_intersection(searcher, capsys):
    """Tests querying two words that exist in the index, but NEVER on the same page."""
    searcher.find_query("einstein friends")
    captured = capsys.readouterr()
    assert "No pages found containing all search terms." in captured.out

def test_find_query_case_and_punctuation(searcher, capsys):
    """Tests query cleaning (lowercasing and punctuation removal)."""
    searcher.find_query("GOOD, friends!")
    captured = capsys.readouterr()
    assert "Found 1 page(s)" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out

def test_find_query_missing_word(searcher, capsys):
    """Tests a multi-word query where one word does not exist at all."""
    searcher.find_query("einstein bananas")
    captured = capsys.readouterr()
    assert "No pages found containing the term 'bananas'." in captured.out

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

def test_find_query_with_typo_suggestion(searcher, capsys):
    """Tests that a misspelled word triggers a 'Did you mean?' suggestion."""
    # Action: Search for a typo of 'einstein'
    searcher.find_query("enstein")
    captured = capsys.readouterr()
    
    # Assert: It should catch the missing word and suggest the closest match
    assert "No results for 'enstein'" in captured.out
    assert "Did you mean: 'einstein'?" in captured.out

def test_find_query_unfixable_typo(searcher, capsys):
    """Tests that completely unknown words fail gracefully without crashing."""
    # Action: Search for a word that is nowhere near anything in the index
    searcher.find_query("zxcvbnm")
    captured = capsys.readouterr()
    
    # Assert: It shouldn't find a match and should print the standard fallback
    assert "No pages found containing the term 'zxcvbnm'" in captured.out