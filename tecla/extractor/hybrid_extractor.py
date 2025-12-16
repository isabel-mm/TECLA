"""
TECLA – Hybrid Term Extractor
----------------------------

Hybrid terminology extractor implementing:
1) Linguistic filtering (unithood)
2) Statistical weighting (termhood)
3) Consolidation into terminological units

The output is a clean terminological inventory
(one row per term).
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import csv
from collections import defaultdict

from tqdm import tqdm

from .linguistic_filter import extract_candidates
from .statistical_filter import compute_statistics


TermLength = Union[int, Tuple[int, Optional[int]]]


class HybridTermExtractor:
    """
    Hybrid terminology extractor based on:
    - POS-based linguistic filtering
    - TF-IDF and C-value statistical weighting
    - Term-level consolidation
    """

    def __init__(
        self,
        language: str,
        grammar_path: Optional[Path] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        self.language = language
        self.weights = weights or {"tfidf": 0.8, "cvalue": 0.2}

        if grammar_path is None:
            self.grammar_path = Path(__file__).parent / "grammar.yaml"
        else:
            self.grammar_path = grammar_path

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def extract(
        self,
        documents: List[Dict[str, Any]],
        *,
        top_k: Optional[int] = None,
        percentile: Optional[float] = None,
        term_length: Optional[TermLength] = None,
        output_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Run the full hybrid extraction pipeline and return
        a consolidated terminological inventory.
        """

        # 1. Linguistic filtering (unithood)
        candidates = extract_candidates(
            documents=documents,
            language=self.language,
            grammar_path=self.grammar_path
        )

        if not candidates:
            return []

        # 2. Statistical weighting (termhood)
        enriched = compute_statistics(
            candidates=candidates,
            documents=documents,
            weights=self.weights
        )

        # 3. Consolidation (TERM LEVEL)
        consolidated = self._consolidate_terms(enriched)

        # 4. Optional filtering by term length
        if term_length is not None:
            consolidated = self._filter_by_length(consolidated, term_length)

        if not consolidated:
            return []

        # 5. Ranking
        ranked = sorted(
            consolidated,
            key=lambda x: x["terminologicity"],
            reverse=True
        )

        # 6. Optional thresholds
        ranked = self._apply_thresholds(
            ranked,
            top_k=top_k,
            percentile=percentile
        )

        # 7. Optional CSV export
        if output_path is not None:
            self._save_to_csv(ranked, output_path)

        return ranked

    # -----------------------------------------------------------------
    # Internal utilities
    # -----------------------------------------------------------------

    @staticmethod
    def _consolidate_terms(
        occurrences: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate occurrences into terminological units.
        """

        buckets = defaultdict(list)

        for occ in occurrences:
            key = occ.get("lemma") or occ["term"]
            buckets[key].append(occ)

        terms = []

        for lemma, occs in tqdm(
            buckets.items(),
            desc="Consolidating terms",
            unit="term"
        ):
            term_surface = max(
                (o["term"] for o in occs),
                key=lambda x: len(x)
            )

            terms.append({
                "term": term_surface,
                "lemma": lemma,
                "language": occs[0]["language"],
                "length": occs[0]["length"],
                "frequency": sum(o.get("frequency", 1) for o in occs),
                "doc_frequency": len({o["doc_id"] for o in occs}),
                "patterns": sorted({o["pattern_id"] for o in occs}),
                "tf_idf": sum(o["tf_idf"] for o in occs) / len(occs),
                "c_value": sum(o["c_value"] for o in occs) / len(occs),
                "tf_idf_norm": sum(o["tf_idf_norm"] for o in occs) / len(occs),
                "c_value_norm": sum(o["c_value_norm"] for o in occs) / len(occs),
                "terminologicity": sum(o["terminologicity"] for o in occs) / len(occs),
            })

        return terms

    @staticmethod
    def _filter_by_length(
        terms: List[Dict[str, Any]],
        term_length: TermLength
    ) -> List[Dict[str, Any]]:
        """
        Filter terms by number of tokens.
        """

        if isinstance(term_length, int):
            return [t for t in terms if t["length"] == term_length]

        min_len, max_len = term_length

        if max_len is None:
            return [t for t in terms if t["length"] >= min_len]

        return [
            t for t in terms
            if min_len <= t["length"] <= max_len
        ]

    @staticmethod
    def _apply_thresholds(
        ranked: List[Dict[str, Any]],
        *,
        top_k: Optional[int],
        percentile: Optional[float]
    ) -> List[Dict[str, Any]]:

        if top_k is not None and percentile is not None:
            raise ValueError("Use either top_k or percentile, not both.")

        if percentile is not None:
            cutoff = int(len(ranked) * (percentile / 100))
            cutoff = max(cutoff, 1)
            return ranked[:cutoff]

        if top_k is not None:
            return ranked[:top_k]

        return ranked

    @staticmethod
    def _save_to_csv(
        results: List[Dict[str, Any]],
        output_path: Path
    ) -> None:
        """
        Save consolidated terminological inventory to CSV.
        """

        if not results:
            return

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "term",
            "lemma",
            "language",
            "length",
            "frequency",
            "doc_frequency",
            "patterns",
            "tf_idf",
            "c_value",
            "tf_idf_norm",
            "c_value_norm",
            "terminologicity"
        ]

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in tqdm(results, desc="Writing CSV", unit="term"):
                row = row.copy()
                row["patterns"] = ";".join(row["patterns"])
                writer.writerow(row)
