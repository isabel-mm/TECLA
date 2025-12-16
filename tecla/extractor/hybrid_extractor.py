"""
TECLA – Hybrid Term Extractor
----------------------------

This module orchestrates the hybrid terminology extraction pipeline.
It combines:
1) a linguistic filter (unithood)
2) a statistical filter (termhood)

The output is a ranked list of candidate terms with a continuous
terminologicity score.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import csv

from .linguistic_filter import extract_candidates
from .statistical_filter import compute_statistics


class HybridTermExtractor:
    """
    Hybrid terminology extractor based on:
    - POS-based linguistic filtering
    - TF-IDF and C-value statistical weighting
    """

    def __init__(
        self,
        language: str,
        grammar_path: Optional[Path] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Parameters
        ----------
        language : str
            Language code (e.g. 'en', 'es').

        grammar_path : Path, optional
            Path to grammar.yaml. If None, assumes it is located
            in the same directory as this module.

        weights : dict, optional
            Weights for the composite terminologicity index.
            Example: {"tfidf": 0.8, "cvalue": 0.2}
        """

        self.language = language
        self.weights = weights

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
        output_path: Optional[Path] = None,
        return_intermediate: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run the full hybrid extraction pipeline.

        Parameters
        ----------
        documents : list of dict
            Preprocessed documents with POS-tagged tokens.

        top_k : int, optional
            Return only the top-k ranked candidates.

        percentile : float, optional
            Percentile threshold (e.g. 90 keeps top 10%).

        output_path : Path, optional
            If provided, results are saved to CSV.

        return_intermediate : bool, default False
            If True, returns intermediate outputs for inspection.

        Returns
        -------
        list of dict
            Ranked list of candidate terms.
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

        # 3. Ranking
        ranked = sorted(
            enriched,
            key=lambda x: x["terminologicity"],
            reverse=True
        )

        # 4. Optional filtering
        ranked = self._apply_thresholds(
            ranked,
            top_k=top_k,
            percentile=percentile
        )

        # 5. Optional CSV export
        if output_path is not None:
            self._save_to_csv(ranked, output_path)

        if return_intermediate:
            return {
                "candidates": candidates,
                "enriched": enriched,
                "ranked": ranked
            }

        return ranked

    # -----------------------------------------------------------------
    # Internal utilities
    # -----------------------------------------------------------------

    @staticmethod
    def _apply_thresholds(
        ranked: List[Dict[str, Any]],
        *,
        top_k: Optional[int],
        percentile: Optional[float]
    ) -> List[Dict[str, Any]]:
        """
        Apply top-k or percentile-based filtering.
        """

        if top_k is not None and percentile is not None:
            raise ValueError("Use either top_k or percentile, not both.")

        if percentile is not None:
            if not (0 < percentile < 100):
                raise ValueError("Percentile must be between 0 and 100.")

            cutoff = int(len(ranked) * (1 - percentile / 100))
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
        Save extraction results to a CSV file.
        """

        if not results:
            return

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "term",
            "lemma",
            "language",
            "doc_id",
            "pattern_id",
            "length",
            "frequency",
            "doc_frequency",
            "tf_idf",
            "c_value",
            "tf_idf_norm",
            "c_value_norm",
            "terminologicity"
        ]

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({k: row.get(k) for k in fieldnames})
