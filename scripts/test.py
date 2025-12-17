# scripts/test_pipeline.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


print(">>> SCRIPT STARTED")

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


from pathlib import Path
from pipeline.pipeline import run_tecla_pipeline

results = run_tecla_pipeline(
    corpus_path=Path("ruta/a/tu/corpus"),
    language="en",
    cleaning_options={
        "structure": True,
        "lemmatize_flag": True,
        "remove_bibliography_flag": True,
    },
    extraction_options={
        "multiword_only": True,
        "percentile": 90,
        "weights": {"tfidf": 0.8, "cvalue": 0.2},
    }
)

print(len(results))
print(results[:10])
