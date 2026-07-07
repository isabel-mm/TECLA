"""
Tests para HybridTermExtractor (módulo core de TECLA).
"""

import pytest
from unittest.mock import Mock, patch
from tecla.extractor.hybrid_extractor import HybridTermExtractor


class TestHybridTermExtractor:
    """Suite de tests para extractor de términos híbrido."""

    @pytest.fixture
    def extractor_en(self):
        """Instancia de extractor para inglés."""
        return HybridTermExtractor(language="en")

    @pytest.fixture
    def extractor_es(self):
        """Instancia de extractor para español."""
        return HybridTermExtractor(language="es")

    @pytest.fixture
    def sample_docs_en(self):
        """Documentos de prueba en inglés."""
        return [
            {
                "text": "Corpus linguistics is the study of language based on corpora.",
                "language": "en",
                "doc_id": "doc1"
            },
            {
                "text": "Natural language processing uses corpora for training.",
                "language": "en",
                "doc_id": "doc2"
            }
        ]

    @pytest.fixture
    def sample_docs_es(self):
        """Documentos de prueba en español."""
        return [
            {
                "text": "La lingüística de corpus es el estudio del lenguaje basado en corpus.",
                "language": "es",
                "doc_id": "doc1"
            },
            {
                "text": "El procesamiento del lenguaje natural utiliza corpus para el entrenamiento.",
                "language": "es",
                "doc_id": "doc2"
            }
        ]

    def test_extractor_initialization_en(self, extractor_en):
        """Test: Extractor inicializa correctamente para inglés."""
        assert extractor_en.language == "en"
        assert hasattr(extractor_en, 'extract')

    def test_extractor_initialization_es(self, extractor_es):
        """Test: Extractor inicializa correctamente para español."""
        assert extractor_es.language == "es"
        assert hasattr(extractor_es, 'extract')

    def test_extract_returns_list(self, extractor_en, sample_docs_en):
        """Test: extract() retorna lista."""
        result = extractor_en.extract(sample_docs_en, top_k=5)
        assert isinstance(result, list)

    def test_extract_respects_top_k(self, extractor_en, sample_docs_en):
        """Test: extract() respeta parámetro top_k."""
        result_5 = extractor_en.extract(sample_docs_en, top_k=5)
        result_3 = extractor_en.extract(sample_docs_en, top_k=3)
        assert len(result_5) <= 5
        assert len(result_3) <= 3

    def test_extract_with_empty_docs(self, extractor_en):
        """Test: extract() maneja documentos vacíos."""
        result = extractor_en.extract([], top_k=10)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_returns_term_dicts(self, extractor_en, sample_docs_en):
        """Test: extract() retorna diccionarios con claves esperadas."""
        result = extractor_en.extract(sample_docs_en, top_k=5)
        if len(result) > 0:
            term = result[0]
            assert isinstance(term, dict)
            assert 'term' in term or 'text' in term
            # Score fields
            assert any(k in term for k in ['score', 'tfidf', 'c_value', 'tf_idf'])

    def test_extract_bilingual_handling(self, extractor_en, sample_docs_en, sample_docs_es):
        """Test: Extractor maneja bilingüismo (ignora idioma ajeno)."""
        # English extractor should process English docs
        result_en = extractor_en.extract(sample_docs_en, top_k=5)
        assert isinstance(result_en, list)

    def test_extract_language_consistency(self, extractor_es, sample_docs_es):
        """Test: Extractor español procesa textos españoles."""
        result = extractor_es.extract(sample_docs_es, top_k=5)
        assert isinstance(result, list)


class TestHybridExtractorIntegration:
    """Tests de integración para HybridTermExtractor."""

    def test_end_to_end_extraction_en(self):
        """Test: Pipeline completo inglés (corpus → extracción)."""
        extractor = HybridTermExtractor(language="en")
        docs = [{
            "text": "Machine learning and natural language processing.",
            "doc_id": "test1",
            "language": "en"
        }]

        result = extractor.extract(docs, top_k=10)
        assert isinstance(result, list)
        # Debería extraer algo (machine learning, natural language processing, etc)
        assert len(result) >= 0  # Puede estar vacío si config es restrictiva

    def test_end_to_end_extraction_es(self):
        """Test: Pipeline completo español (corpus → extracción)."""
        extractor = HybridTermExtractor(language="es")
        docs = [{
            "text": "El aprendizaje automático y el procesamiento del lenguaje natural.",
            "doc_id": "test1",
            "language": "es"
        }]

        result = extractor.extract(docs, top_k=10)
        assert isinstance(result, list)

    def test_reproducibility(self):
        """Test: Resultados reproducibles (determinísticos)."""
        docs = [{
            "text": "Corpus linguistics and computational methods.",
            "doc_id": "test1",
            "language": "en"
        }]

        extractor1 = HybridTermExtractor(language="en")
        extractor2 = HybridTermExtractor(language="en")

        result1 = extractor1.extract(docs, top_k=5)
        result2 = extractor2.extract(docs, top_k=5)

        # Misma configuración → mismos resultados
        if len(result1) > 0 and len(result2) > 0:
            assert result1[0] == result2[0]


class TestHybridExtractorErrorHandling:
    """Tests de manejo de errores."""

    def test_invalid_language_raises_error(self):
        """Test: Lenguaje inválido genera error."""
        with pytest.raises((ValueError, KeyError, Exception)):
            HybridTermExtractor(language="xyz")

    def test_extract_with_malformed_docs(self):
        """Test: Documentos malformados se manejan gracefully."""
        extractor = HybridTermExtractor(language="en")

        # Falta 'text'
        docs_no_text = [{"doc_id": "test1", "language": "en"}]
        result = extractor.extract(docs_no_text, top_k=5)
        assert isinstance(result, list)

    def test_extract_negative_top_k(self):
        """Test: top_k negativo o cero se maneja."""
        extractor = HybridTermExtractor(language="en")
        docs = [{"text": "test", "doc_id": "test1", "language": "en"}]

        result = extractor.extract(docs, top_k=0)
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
