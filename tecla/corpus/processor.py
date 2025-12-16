"""
TECLA – Corpus Linguistic Processor
-----------------------------------

This module converts a cleaned corpus into a linguistically enriched
representation suitable for terminology extraction.
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
    enriched document representations.

    Parameters
    ----------
    corpus_folder : str
        Path to folder containing cleaned .txt files.

    language : str
        Language code ('en', 'es').

    spacy_model : str
        spaCy model name (e.g. 'en_core_web_trf').

    Returns
    -------
    list of dict
        Documents in TECLA format, ready for extraction.
    """

    corpus_path = Path(corpus_folder)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus folder not found: {corpus_folder}")

    nlp = spacy.load(spacy_model, disable=["ner", "parser"])

    documents = []

    for txt_file in sorted(corpus_path.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8").strip()
        if not text:
            continue

        doc = nlp(text)

        tokens = []
        for token in doc:
            if token.is_space:
                continue

            tokens.append({
                "text": token.text,
                "lemma": token.lemma_.lower(),
                "pos": token.pos_
            })

        documents.append({
            "doc_id": txt_file.stem,
            "language": language,
            "tokens": tokens
        })

    return documents
