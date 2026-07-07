# TECLA: Usage Guide

TECLA (Terminology Extraction and Corpus Linguistics Application) is a toolkit for automatic term extraction from specialized corpora.

## Installation

```bash
pip install -e .
```

## Quick Start

### 1. Basic Term Extraction

```python
from tecla import HybridTermExtractor

# Initialize extractor for Spanish or English
extractor = HybridTermExtractor(language="es")

# Documents to process
documents = [
    {
        "text": "La lingüística de corpus es fundamental para el análisis terminológico.",
        "doc_id": "doc1",
        "language": "es"
    },
    {
        "text": "El procesamiento del lenguaje natural utiliza métodos computacionales.",
        "doc_id": "doc2",
        "language": "es"
    }
]

# Extract top 20 terms
terms = extractor.extract(documents, top_k=20)

# Print results
for term in terms:
    print(f"{term['text']}: {term['score']:.3f}")
```

### 2. Build Corpus from Text Files

```python
from tecla import build_corpus_from_txt

# Build corpus from directory of text files
corpus = build_corpus_from_txt(
    input_dir="path/to/texts/",
    language="es",
    clean=True,
    spacy_model="es_core_news_md"
)

# Extract from corpus documents
terms = extractor.extract(corpus, top_k=50)
```

### 3. Build Corpus from PDFs

```python
from tecla import build_corpus

# Build corpus from PDFs with automatic cleaning
build_corpus(
    pdf_dir="path/to/pdfs/",
    output_dir="corpus_output/",
    language="es",
    clean=True,
    clean_params={
        "remove_headers": True,
        "remove_footers": True,
        "language": "es"
    }
)
```

### 4. Corpus Statistics

```python
from tecla import corpus_statistics

# Get corpus statistics
stats = corpus_statistics(
    corpus_dir="corpus_output/",
    language="es"
)

print(f"Total tokens: {stats['total_tokens']}")
print(f"Unique types: {stats['unique_types']}")
print(f"Type-token ratio: {stats['type_token_ratio']:.2f}")
```

### 5. Evaluate Extraction Results

```python
from tecla import evaluate_extraction

# Evaluate against gold standard
metrics = evaluate_extraction(
    predicted_terms=terms,
    gold_standard_file="reference_glossary.txt",
    language="es"
)

print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1-score: {metrics['f1']:.3f}")
```

## API Reference

### HybridTermExtractor

Main class for hybrid term extraction combining linguistic and statistical methods.

```python
HybridTermExtractor(language: str)
```

**Parameters:**
- `language` (str): Target language ("en" or "es")

**Methods:**

#### extract()
```python
extract(documents: List[Dict], top_k: int = 100) → List[Dict]
```

Extract terms from documents.

**Parameters:**
- `documents`: List of document dicts with keys: `text`, `doc_id`, `language`
- `top_k`: Maximum number of terms to return

**Returns:**
- List of term dictionaries with keys:
  - `text`: Term string
  - `score`: Composite score (0-1)
  - `tfidf`: TF-IDF score
  - `c_value`: C-value statistical score
  - `frequency`: Absolute frequency
  - `doc_frequency`: Number of documents containing term

### build_corpus_from_txt()

```python
build_corpus_from_txt(
    input_dir: str,
    language: str,
    clean: bool = True,
    spacy_model: str = None
) → List[Dict]
```

Build corpus from text files.

**Parameters:**
- `input_dir`: Path to directory containing .txt files
- `language`: "en" or "es"
- `clean`: Apply text cleaning
- `spacy_model`: spaCy model for tokenization (e.g., "es_core_news_md")

**Returns:**
- List of processed document dicts

### corpus_statistics()

```python
corpus_statistics(corpus_dir: str, language: str) → Dict
```

Calculate corpus statistics.

**Returns dict with:**
- `total_tokens`: Total token count
- `unique_types`: Vocabulary size
- `type_token_ratio`: TTR (vocabulary richness)
- `hapax_ratio`: Proportion of hapax legomena
- `heaps_beta`: Heaps Law exponent (vocabulary growth rate)

### evaluate_extraction()

```python
evaluate_extraction(
    predicted_terms: List[Dict],
    gold_standard_file: str,
    language: str
) → Dict
```

Evaluate extraction against reference glossary.

**Returns dict with:**
- `precision`: Precision score
- `recall`: Recall / Coverage score
- `f1`: F1-score
- `confusion_matrix`: True/false positives and negatives

## Command Line Usage

TECLA also provides a CLI:

```bash
# Extract terms from directory
tecla extract --input-dir corpus/ --language es --top-k 50

# Build corpus from PDFs
tecla build-corpus --pdf-dir pdfs/ --output-dir corpus_output/ --language es

# Get corpus statistics
tecla stats --corpus-dir corpus_output/ --language es
```

## Configuration

Default parameters for extraction:

```python
{
    "tfidf_weight": 0.6,      # Weight of TF-IDF in composite score
    "c_value_weight": 0.4,    # Weight of C-value in composite score
    "min_length": 3,          # Minimum term length (tokens)
    "max_length": 5,          # Maximum term length (tokens)
    "min_frequency": 2,       # Minimum document frequency
}
```

Customize by modifying the extractor configuration before extraction.

## Examples

See `/examples/` directory for complete Jupyter notebooks:
- `extraction_workflow.ipynb` - End-to-end workflow
- `bilingual_comparison.ipynb` - English vs Spanish extraction
- `evaluation_pipeline.ipynb` - Term validation and scoring

## Troubleshooting

**Issue:** "spacy model not found"
```bash
python -m spacy download es_core_news_md
python -m spacy download en_core_web_md
```

**Issue:** "langid error"
```bash
python -m nltk.downloader punkt averaged_perceptron_tagger
```

**Issue:** Memory error on large corpus
- Reduce corpus size or process in batches
- Use `streaming=True` in build_corpus()

## Citation

If you use TECLA in research, please cite:

```bibtex
@phdthesis{moyano2026,
  title={Automatic Terminology Extraction via Hybrid Methods},
  author={Moyano, Isabel},
  school={Universidad de Cádiz},
  year={2026}
}
```

## License

MIT License - See LICENSE file
