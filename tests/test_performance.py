import pytest
from src.search import Searcher
from src.indexer import Indexer

# Set up a real Searcher using actual saved index.
@pytest.fixture
def real_searcher():
    indexer = Indexer("data/index.json")
    indexer.load_index()
    return Searcher(indexer.inverted_index)

def test_benchmark_single_word_search(benchmark, real_searcher):
    """
    Benchmarks a simple single-word TF-IDF search.
    Benchmark fixture runs this function repeatedly to get an accurate average.
    """
    benchmark(real_searcher.find_query, "friends")

def test_benchmark_exact_phrase_search(benchmark, real_searcher):
    """
    Benchmarks the advanced exact-phrase positional filtering.
    """
    benchmark(real_searcher.find_query, '"good friends"')

def test_benchmark_typo_suggestion(benchmark, real_searcher):
    """
    Benchmarks the difflib suggestion algorithm.
    """
    benchmark(real_searcher.find_query, "einsteinn")
