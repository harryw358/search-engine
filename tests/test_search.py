import pytest
from src.search import Searcher

# --- Fixtures ---

@pytest.fixture
def sample_index():
    """Provides a small, fake inverted index for testing."""
    return {
        "einstein": {
            "http://quotes.toscrape.com/page/1/": {
                "frequency": 1,
                "positions": [5]
            }
        },
        "world": {
            "http://quotes.toscrape.com/page/1/": {
                "frequency": 2,
                "positions": [1, 10]
            },
            "http://quotes.toscrape.com/page/2/": {
                "frequency": 1,
                "positions": [4]
            }
        }
    }

@pytest.fixture
def searcher(sample_index):
    """Provides a Searcher instance loaded with the mock data."""
    return Searcher(sample_index)

# --- Tests ---

def test_print_word_index_found_case_insensitive(searcher, capsys):
    """Tests that an existing word prints its statistics, regardless of case."""
    # We search for "EinSteiN" to test the case-insensitivity requirement
    searcher.print_word_index("EinSteiN")
    
    # capsys.readouterr() captures everything that was printed to the console
    captured = capsys.readouterr()
    
    # Assert the output contains the expected formatting and data
    assert "Index results for 'einstein'" in captured.out
    assert "URL: http://quotes.toscrape.com/page/1/" in captured.out
    assert "Frequency: 1" in captured.out
    assert "Positions: [5]" in captured.out

def test_print_word_index_multiple_pages(searcher, capsys):
    """Tests that a word found on multiple pages prints all URLs."""
    searcher.print_word_index("world")
    captured = capsys.readouterr()
    
    # Both URLs should appear in the print output
    assert "http://quotes.toscrape.com/page/1/" in captured.out
    assert "http://quotes.toscrape.com/page/2/" in captured.out
    assert "Frequency: 2" in captured.out  # From page 1
    assert "Frequency: 1" in captured.out  # From page 2

def test_print_word_index_not_found(searcher, capsys):
    """Tests the edge case where the requested word is not in the index."""
    searcher.print_word_index("python")
    captured = capsys.readouterr()
    
    assert "The word 'python' was not found" in captured.out

def test_print_word_index_empty_index(capsys):
    """Tests the edge case where the user hasn't loaded an index yet."""
    # Instantiate an empty Searcher
    empty_searcher = Searcher({})
    
    empty_searcher.print_word_index("einstein")
    captured = capsys.readouterr()
    
    assert "Error: Index is empty" in captured.out