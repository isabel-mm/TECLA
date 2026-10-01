"""
TECLA – Corpus Linguistic Processor
-----------------------------------

Converts a cleaned corpus into a linguistically enriched representation
suitable for terminology extraction.

Each document is segmented into sentences so that the linguistic filter
never matches candidates that cross sentence boundaries.
"""

from pathlib import Path
from typing import List, Dict, Any
import spacy


def corpus_to_documents(
    corpus_folder: str,
    language: str,
    spacy_model: str
) -> List[Dict[str, Any]]:
    """
    Convert a corpus of plain-text files into linguistically
    enriched document representations, segmented by sentence.

    Parameters
    ----------
    corpus_folder : str
        Path to folder containing cleaned .txt files.
    language : str
        Language code ('en', 'es', etc.).
    spacy_model : str
        spaCy model name (e.g. 'es_core_news_sm').

    Returns
    -------
    list of dict
        Each dict contains:
        - doc_id : str
        - language : str
        - sentences : list of list of token dicts
        - tokens : flat list of all token dicts (for backward compatibility)

        Each token dict has 'text', 'lemma', 'pos'.
    """

    corpus_path = Path(corpus_folder)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus folder not found: {corpus_folder}")

    # Load model without NER and dependency parser (not needed for extraction).
    # Add sentencizer so sentence boundaries are still detected via punctuation.
    nlp = spacy.load(spacy_model, disable=["ner", "parser"])
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")

    # Since parser and NER are disabled, memory usage is much lower.
    # Raise the limit to handle large documents without errors.
    nlp.max_length = 3_000_000

    documents = []

    for txt_file in sorted(corpus_path.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8").strip()
        if not text:
            continue

        sentences = _process_text(nlp, text)

        documents.append({
            "doc_id": txt_file.stem,
            "language": language,
            "sentences": sentences,
            "tokens": [tok for sent in sentences for tok in sent],
        })

    return documents


_CHUNK_SIZE = 2_500_000  # chars per chunk when text exceeds max_length


def _process_text(nlp, text: str) -> list:
    """
    Run spaCy on text, splitting into chunks if the text is very long.
    Returns a flat list of sentence token lists.
    """
    if len(text) <= nlp.max_length:
        return _sentences_from_doc(nlp(text))

    # Split at paragraph boundaries to avoid cutting mid-sentence
    sentences = []
    start = 0
    while start < len(text):
        end = start + _CHUNK_SIZE
        if end < len(text):
            # Walk back to the nearest paragraph break
            newline = text.rfind("\n\n", start, end)
            if newline != -1:
                end = newline + 2
        chunk = text[start:end].strip()
        if chunk:
            sentences.extend(_sentences_from_doc(nlp(chunk)))
        start = end

    return sentences


def _sentences_from_doc(doc) -> list:
    sentences = []
    for sent in doc.sents:
        tokens = [
            {"text": tok.text, "lemma": tok.lemma_.lower(), "pos": tok.pos_}
            for tok in sent
            if not tok.is_space
        ]
        if tokens:
            sentences.append(tokens)
    return sentences
