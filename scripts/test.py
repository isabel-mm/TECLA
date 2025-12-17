# scripts/test_pipeline.py

from pathlib import Path
from pipeline.pipeline import run_tecla_pipeline

print(">>> SCRIPT STARTED")

results = run_tecla_pipeline(
    corpus_path=Path("pdfs"),
    language="es",
    cleaning_options={
        "structure": True,
        "lemmatize_flag": True,
        "remove_bibliography_flag": True,
    },
    extraction_options={
        "multiword_only": True,
        "percentile": 90,
        "weights": {"tfidf": 0.8, "cvalue": 0.2},
    },
)

print(f"Extracted {len(results)} terms")
print(results[:5])
