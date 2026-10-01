# TECLA: Toolkit for Corpus-based Terminology Extraction

**TECLA** (Terminology Extraction and Corpus Linguistics Application) is a Python toolkit for automatic term extraction from specialized text corpora, combining linguistic filtering with statistical measures.

## Features

✅ **Hybrid Extraction**: Combines POS-based linguistic filtering with TF-IDF and C-value statistical weighting  
✅ **Bilingual Support**: Full support for English (en) and Spanish (es)  
✅ **Corpus Building**: Automatic corpus construction from PDFs or text files with cleaning  
✅ **Evaluation Metrics**: Built-in evaluation against gold-standard glossaries  
✅ **Corpus Statistics**: Compute Heaps Law, TTR, hapax ratios, and more  
✅ **CLI Interface**: Command-line tools for all main operations  
✅ **Cross-domain Validation**: Evaluate generalization to unseen domains (ACTER)  

## Installation

### From source

```bash
cd /path/to/repo
pip install -e .
```

### Dependencies

- Python 3.9+
- spacy >= 3.0 (for linguistic processing)
- pandas, numpy (data processing)
- nltk (language utilities)
- pdfminer.six (PDF extraction)

Download spacy models:
```bash
python -m spacy download es_core_news_md
python -m spacy download en_core_web_md
```

## Quick Start

### Python API

```python
from tecla import HybridTermExtractor

# Initialize
extractor = HybridTermExtractor(language="es")

# Prepare documents
docs = [{
    "text": "La lingüística de corpus...",
    "doc_id": "doc1",
    "language": "es"
}]

# Extract terms
terms = extractor.extract(docs, top_k=50)

for term in terms[:5]:
    print(f"{term['text']}: {term['score']:.3f}")
```

### Command Line

```bash
# Extract terms
tecla extract --corpus-dir data/ --language es --top-k 50

# Build corpus from PDFs
tecla build-corpus --pdf-dir pdfs/ --output-dir corpus/ --language es

# Compute statistics
tecla stats --corpus-dir corpus/ --language es
```

## Module Structure

```
tecla/
├── extractor/           # Term extraction engines
│   ├── hybrid_extractor.py    # Main HybridTermExtractor class
│   ├── statistical_filter.py  # TF-IDF, C-value computation
│   └── linguistic_filter.py   # POS-based filtering
├── corpus/              # Corpus building and processing
│   ├── builder.py       # Build corpus from PDFs/texts
│   ├── processor.py     # Document tokenization & annotation
│   ├── cleaning.py      # Text cleaning & normalization
│   ├── statistics.py    # Corpus metrics (Heaps, TTR, etc)
│   └── language_detection.py  # Automatic language detection
├── evaluation/          # Evaluation metrics
│   └── term_eval.py     # Precision, recall, F1 scoring
├── cli.py              # Command-line interface
└── __init__.py         # Public API exports
```

## Key Classes

### HybridTermExtractor

Main extraction engine combining linguistic and statistical methods.

```python
class HybridTermExtractor:
    def __init__(self, language: str)
    def extract(self, documents: List[Dict], top_k: int = 100) -> List[Dict]
```

**Extract method parameters:**
- `documents`: List of dicts with `text`, `doc_id`, `language`
- `top_k`: Return top k terms (default: 100)

**Return format:**
```python
[
    {
        "text": "terminology extraction",
        "score": 0.856,
        "tfidf": 0.45,
        "c_value": 0.41,
        "frequency": 12,
        "doc_frequency": 8
    },
    ...
]
```

## Examples

See `/examples/` for complete working examples:

- **extraction_workflow.py**: End-to-end workflow (load docs → extract → analyze)
- **bilingual_comparison.py**: Compare English vs Spanish extraction
- **evaluation_pipeline.py**: Validate against reference glossaries

## Core Algorithms

### Hybrid Scoring

```
score = α × TF-IDF + (1-α) × C-value
```

Default weights: α = 0.5 (TF-IDF), (1-α) = 0.5 (NC-value), i.e. the mean of both; adjustable (presets or custom weights)

### C-Value

Statistical measure of term specificity:

```
C-value(t) = log(|documents_containing_t|) × frequency(t)
```

Lower values indicate higher specificity (rare in general language).

### POS-Based Filtering

Valid term patterns (by language):

**English:**
- NN, NNP, NNPS (nouns)
- NN NN, NN ADJ, etc. (noun phrases)
- VB + NN (verbal compounds)

**Spanish:**
- NC, NP (nouns)
- NC NC, ADJ NC, etc. (noun phrases)
- CONJ + NC (conjunctive compounds)

## Evaluation

Evaluate extraction against reference glossary:

```python
from tecla import evaluate_extraction

metrics = evaluate_extraction(
    predicted_terms=extracted_terms,
    gold_standard_file="glossary.txt",
    language="es"
)

print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1: {metrics['f1']:.3f}")
```

## Configuration

Customize extraction behavior:

```python
config = {
    "tfidf_weight": 0.5,      # TF-IDF component weight
    "c_value_weight": 0.4,    # C-value component weight  
    "min_length": 3,          # Min tokens per term
    "max_length": 5,          # Max tokens per term
    "min_frequency": 2,       # Min document frequency
    "min_score": 0.1,         # Min extraction score
}

extractor = HybridTermExtractor(language="es", config=config)
```

## Testing

Run test suite:

```bash
pytest tests/ -v
pytest tests/test_hybrid_extractor.py -v
pytest tests/test_corpus.py -v
```

Coverage report:

```bash
pytest tests/ --cov=tecla --cov-report=html
```

## Performance

Typical extraction speed on modern hardware:

- **Corpus size:** 100 documents, 50K tokens
- **Extraction time:** ~2-5 seconds (Spanish), ~1-3 seconds (English)
- **Memory:** ~200-500 MB for medium corpus

## Limitations

- Requires spacy language models (download needed)
- Performance depends on corpus quality and size
- Statistical measures require minimum corpus size (~10K tokens)
- Cross-domain performance may degrade (see ACTER evaluation)

## Future Work

- [ ] Support for additional languages (FR, DE, IT)
- [ ] Transformer-based embeddings (XLM-RoBERTa)
- [ ] Domain adaptation without re-annotation
- [ ] Interactive term validation UI

## Citation

If you use TECLA in your research, please cite:

```bibtex
@phdthesis{moyano2026termextraction,
  title={Automatic Terminology Extraction via Hybrid Linguistic-Statistical Methods},
  author={Moyano, Isabel},
  school={Universidad de Cádiz},
  year={2026}
}
```

## License

MIT License - See LICENSE file in repository root

## Contact

For issues, questions, or contributions: isabel.moyano@gm.uca.es

---

**Last Updated:** July 7, 2026  
**Version:** 2.0.0
