"""
Unit tests for tecla.extractor modules.
"""

import pytest
from pathlib import Path

from tecla.extractor.linguistic_filter import _match_pos_pattern, _is_pos_tag
from tecla.extractor.statistical_filter import (
    compute_frequencies,
    compute_tfidf,
    compute_cvalue,
    min_max_normalise,
    compute_terminologicity,
)
from tecla.extractor.tbx_export import export_tbx


# ---------------------------------------------------------------------------
# _is_pos_tag
# ---------------------------------------------------------------------------

class TestIsPosTag:
    def test_known_pos_tags(self):
        for tag in ("NOUN", "ADJ", "VERB", "PROPN", "ADV", "ADP"):
            assert _is_pos_tag(tag)

    def test_literal_tokens(self):
        for token in ("of", "de", "the", "para"):
            assert not _is_pos_tag(token)


# ---------------------------------------------------------------------------
# _match_pos_pattern
# ---------------------------------------------------------------------------

class TestMatchPosPattern:
    def _pos(self, seq):
        return [t["pos"] for t in seq]

    def _tok(self, seq):
        return [t["text"] for t in seq]

    def _make(self, items):
        return [{"pos": p, "text": t} for p, t in items]

    def test_simple_noun_match(self):
        tokens = self._make([("NOUN", "corpus"), ("NOUN", "linguistics")])
        matches = _match_pos_pattern(["NOUN", "NOUN"], ["corpus", "linguistics"], ["NOUN", "NOUN"])
        assert (0, 2) in matches

    def test_adj_noun_pattern(self):
        tokens = self._make([("ADJ", "linguistic"), ("NOUN", "analysis")])
        matches = _match_pos_pattern(["ADJ", "NOUN"], ["linguistic", "analysis"], ["ADJ", "NOUN"])
        assert (0, 2) in matches

    def test_literal_of_pattern(self):
        pos_seq = ["NOUN", "ADP", "NOUN"]
        tok_seq = ["part", "of", "speech"]
        # Pattern: NOUN of NOUN — "of" is a literal token
        matches = _match_pos_pattern(pos_seq, tok_seq, ["NOUN", "of", "NOUN"])
        assert (0, 3) in matches

    def test_literal_de_pattern(self):
        pos_seq = ["NOUN", "ADP", "NOUN"]
        tok_seq = ["esquema", "de", "anotación"]
        matches = _match_pos_pattern(pos_seq, tok_seq, ["NOUN", "de", "NOUN"])
        assert (0, 3) in matches

    def test_noun_plus_operator(self):
        pos_seq = ["NOUN", "NOUN", "NOUN", "VERB"]
        tok_seq = ["corpus", "annotation", "scheme", "requires"]
        matches = _match_pos_pattern(pos_seq, tok_seq, ["NOUN+"])
        # Should match the three consecutive NOUNs
        assert any(end - start >= 2 for start, end in matches)

    def test_star_operator_zero_matches(self):
        pos_seq = ["NOUN"]
        tok_seq = ["corpus"]
        # (ADJ|NOUN)* NOUN — star matches zero ADJ/NOUNs, then one NOUN
        matches = _match_pos_pattern(pos_seq, tok_seq, ["(ADJ|NOUN)*", "NOUN"])
        assert len(matches) > 0

    def test_no_match_wrong_pos(self):
        pos_seq = ["VERB", "ADV"]
        tok_seq = ["runs", "quickly"]
        matches = _match_pos_pattern(pos_seq, tok_seq, ["NOUN", "NOUN"])
        assert matches == []

    def test_no_cross_sentence_match(self):
        """
        Regression: _match_pos_pattern is called per sentence, so cross-sentence
        matches are impossible by construction. Verify the function itself is correct.
        """
        pos_seq = ["NOUN"]
        tok_seq = ["end"]
        matches = _match_pos_pattern(pos_seq, tok_seq, ["NOUN", "NOUN"])
        assert matches == []


# ---------------------------------------------------------------------------
# statistical_filter
# ---------------------------------------------------------------------------

class TestComputeFrequencies:
    def test_basic(self):
        candidates = [
            {"lemma": "corpus linguistics", "doc_id": "d1"},
            {"lemma": "corpus linguistics", "doc_id": "d2"},
            {"lemma": "term extraction", "doc_id": "d1"},
        ]
        stats = compute_frequencies(candidates)
        assert stats["corpus linguistics"]["frequency"] == 2
        assert stats["corpus linguistics"]["doc_frequency"] == 2
        assert stats["term extraction"]["frequency"] == 1


class TestComputeTFIDF:
    def test_higher_freq_higher_score(self):
        term_stats = {
            "common term": {"frequency": 10, "doc_frequency": 3},
            "rare term": {"frequency": 1, "doc_frequency": 1},
        }
        scores = compute_tfidf(term_stats, n_documents=5)
        assert scores["common term"] > scores["rare term"]


class TestComputeCValue:
    def test_single_word_uses_unit_length_weight(self):
        # Variante de la tesis (ec. C-value, cap. 4): max(log2|a|, 1), de modo que
        # un término de una palabra no anidado recibe 1 · f(a) en lugar de 0.
        term_stats = {"corpus": {"frequency": 5, "doc_frequency": 2}}
        scores = compute_cvalue(term_stats)
        assert scores["corpus"] == 5.0

    def test_multiword_term_positive(self):
        term_stats = {"corpus linguistics": {"frequency": 5, "doc_frequency": 2}}
        scores = compute_cvalue(term_stats)
        assert scores["corpus linguistics"] > 0.0


class TestMinMaxNormalise:
    def test_range(self):
        scores = {"a": 1.0, "b": 3.0, "c": 5.0}
        normed = min_max_normalise(scores)
        assert normed["a"] == pytest.approx(0.0)
        assert normed["c"] == pytest.approx(1.0)

    def test_all_equal(self):
        scores = {"a": 2.0, "b": 2.0}
        normed = min_max_normalise(scores)
        assert all(v == 1.0 for v in normed.values())

    def test_empty(self):
        assert min_max_normalise({}) == {}


class TestComputeTerminologicity:
    def test_weighted_sum(self):
        tfidf_norm = {"term": 0.8}
        cvalue_norm = {"term": 0.4}
        weights = {"tfidf": 0.5, "cvalue": 0.5}
        result = compute_terminologicity(tfidf_norm, cvalue_norm, weights)
        assert result["term"] == pytest.approx(0.6)

    def test_variance_mode_no_crash(self):
        tfidf_norm = {"a": 0.2, "b": 0.8}
        cvalue_norm = {"a": 0.4, "b": 0.6}
        result = compute_terminologicity(tfidf_norm, cvalue_norm, weights="variance")
        assert set(result.keys()) == {"a", "b"}


# ---------------------------------------------------------------------------
# TBX export
# ---------------------------------------------------------------------------

class TestExportTBX:
    def test_creates_file(self, tmp_path):
        terms = [
            {
                "term": "corpus linguistics",
                "lemma": "corpus linguistics",
                "frequency": 5,
                "terminologicity": 0.87,
                "patterns": ["EN_NOUN_BIGRAM"],
            }
        ]
        output = tmp_path / "terms.tbx"
        export_tbx(terms, str(output), language="en")
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "corpus linguistics" in content
        assert "TBX" in content

    def test_empty_list_creates_empty_body(self, tmp_path):
        output = tmp_path / "empty.tbx"
        export_tbx([], str(output), language="es")
        assert output.exists()
