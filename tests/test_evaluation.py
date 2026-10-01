"""
Unit tests for tecla.evaluation modules.
"""

import pytest
from tecla.evaluation.term_eval import evaluate_extraction, _normalise_extracted
from tecla.evaluation.metrics import (
    compute_itc_norm,
    compute_growth_curve,
    compute_normalized_mean_coverage,
)


# ---------------------------------------------------------------------------
# evaluate_extraction
# ---------------------------------------------------------------------------

class TestEvaluateExtraction:
    def test_perfect_match(self):
        extracted = ["corpus linguistics", "term extraction"]
        gold = ["corpus linguistics", "term extraction"]
        result = evaluate_extraction(extracted, gold)
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
        assert result["f1"] == 1.0

    def test_no_match(self):
        extracted = ["foo bar"]
        gold = ["corpus linguistics"]
        result = evaluate_extraction(extracted, gold)
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0
        assert result["f1"] == 0.0

    def test_partial_match(self):
        extracted = ["corpus linguistics", "wrong term"]
        gold = ["corpus linguistics", "term extraction"]
        result = evaluate_extraction(extracted, gold)
        assert result["precision"] == pytest.approx(0.5)
        assert result["recall"] == pytest.approx(0.5)
        assert result["tp"] == 1
        assert result["fp"] == 1
        assert result["fn"] == 1

    def test_case_insensitive(self):
        extracted = ["Corpus Linguistics"]
        gold = ["corpus linguistics"]
        result = evaluate_extraction(extracted, gold)
        assert result["tp"] == 1

    def test_dict_input_exact_mode(self):
        extracted = [{"term": "corpus linguistics", "lemma": "corpus linguistic"}]
        gold = ["corpus linguistics"]
        result = evaluate_extraction(extracted, gold, mode="exact")
        assert result["tp"] == 1

    def test_dict_input_lemma_mode(self):
        extracted = [{"term": "corpus linguistics", "lemma": "corpus linguistic"}]
        gold = ["corpus linguistic"]
        result = evaluate_extraction(extracted, gold, mode="lemma")
        assert result["tp"] == 1

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            evaluate_extraction(["term"], ["term"], mode="fuzzy")

    def test_empty_extracted(self):
        result = evaluate_extraction([], ["corpus linguistics"])
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0
        assert result["fn"] == 1

    def test_empty_gold(self):
        result = evaluate_extraction(["corpus linguistics"], [])
        assert result["recall"] == 0.0
        assert result["fp"] == 1


# ---------------------------------------------------------------------------
# metrics (componentes del IRT sobre corpus anotado)
# ---------------------------------------------------------------------------

class TestComputeItcNorm:
    def test_zero_for_empty(self):
        assert compute_itc_norm([]) == 0.0

    def test_zero_for_zero_total(self):
        assert compute_itc_norm([0]) == 0.0

    def test_value_between_zero_and_one(self):
        # Monotonically growing curve
        curve = list(range(1, 21))
        result = compute_itc_norm(curve)
        assert 0.0 < result <= 1.0

    def test_saturated_corpus_low_itc(self):
        # Most new terms appear early, later texts add nothing
        curve = [100, 105, 108, 109, 110, 110, 110, 110]
        result = compute_itc_norm(curve)
        # ITC should be low (most growth already happened)
        assert result < 0.5

    def test_distinguishes_growing_from_saturated(self):
        # Mismo número de textos y de términos finales: la versión anterior
        # devolvía 1/N en ambos casos; ahora el corpus que sigue creciendo al
        # final obtiene un valor mayor que el saturado.
        growing = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        saturated = [60, 80, 90, 95, 98, 100, 100, 100, 100, 100]
        assert compute_itc_norm(growing) > compute_itc_norm(saturated)
        assert compute_itc_norm(saturated) == 0.0
        assert compute_itc_norm(growing) == 0.2

    def test_invalid_tail_fraction(self):
        import pytest
        with pytest.raises(ValueError):
            compute_itc_norm([1, 2, 3], tail_fraction=0)


class TestIrtAnotado:
    def test_keys_and_range(self):
        from tecla.evaluation import compute_irt_anotado
        r = compute_irt_anotado(cmn=0.9, itc_norm=0.1, mattr=0.3, beta=0.5)
        assert set(r) == {"IRT", "interpretación"}
        assert 0.0 <= r["IRT"] <= 1.0

    def test_deprecated_alias(self):
        import pytest
        from tecla.evaluation import compute_itr, compute_irt_anotado
        with pytest.deprecated_call():
            old = compute_itr(cmn=0.9, itc_norm=0.1, mattr=0.3, beta=0.5)
        assert old == compute_irt_anotado(cmn=0.9, itc_norm=0.1, mattr=0.3, beta=0.5)


class TestNormalisedExtracted:
    def test_string_list(self):
        result = _normalise_extracted(["Corpus Linguistics", "Term Extraction"], "exact")
        assert result == ["corpus linguistics", "term extraction"]

    def test_dict_list_exact(self):
        items = [{"term": "Corpus Linguistics", "lemma": "corpus linguistic"}]
        result = _normalise_extracted(items, "exact")
        assert result == ["corpus linguistics"]

    def test_dict_list_lemma(self):
        items = [{"term": "Corpus Linguistics", "lemma": "corpus linguistic"}]
        result = _normalise_extracted(items, "lemma")
        assert result == ["corpus linguistic"]
