"""
Shared pytest fixtures for TECLA tests.
"""

import pytest


@pytest.fixture
def sample_documents():
    """Minimal linguistically enriched documents for extractor tests."""
    return [
        {
            "doc_id": "doc1",
            "language": "en",
            "sentences": [
                [
                    {"text": "corpus", "lemma": "corpus", "pos": "NOUN"},
                    {"text": "linguistics", "lemma": "linguistics", "pos": "NOUN"},
                    {"text": "is", "lemma": "be", "pos": "AUX"},
                    {"text": "a", "lemma": "a", "pos": "DET"},
                    {"text": "linguistic", "lemma": "linguistic", "pos": "ADJ"},
                    {"text": "field", "lemma": "field", "pos": "NOUN"},
                ],
                [
                    {"text": "term", "lemma": "term", "pos": "NOUN"},
                    {"text": "extraction", "lemma": "extraction", "pos": "NOUN"},
                    {"text": "requires", "lemma": "require", "pos": "VERB"},
                    {"text": "a", "lemma": "a", "pos": "DET"},
                    {"text": "large", "lemma": "large", "pos": "ADJ"},
                    {"text": "corpus", "lemma": "corpus", "pos": "NOUN"},
                ],
            ],
            "tokens": [],  # populated below
        },
        {
            "doc_id": "doc2",
            "language": "en",
            "sentences": [
                [
                    {"text": "linguistic", "lemma": "linguistic", "pos": "ADJ"},
                    {"text": "analysis", "lemma": "analysis", "pos": "NOUN"},
                    {"text": "uses", "lemma": "use", "pos": "VERB"},
                    {"text": "corpus", "lemma": "corpus", "pos": "NOUN"},
                    {"text": "data", "lemma": "data", "pos": "NOUN"},
                ],
            ],
            "tokens": [],
        },
    ]


@pytest.fixture
def sample_gold():
    return ["corpus linguistics", "term extraction", "linguistic analysis", "corpus data"]
