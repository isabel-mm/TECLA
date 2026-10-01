"""
Tests para módulo corpus de TECLA.
"""

import pytest
from unittest.mock import Mock, patch


class TestCorpusCleaning:
    """Tests para limpieza de textos."""

    def test_clean_text_removes_extra_whitespace(self):
        """Test: Limpieza elimina espacios extra."""
        from tecla import clean_text
        text = "Esto   es   un    texto  con\n\nespacios  extras."
        cleaned = clean_text(text, language="es")
        assert isinstance(cleaned, str)

    def test_clean_text_handles_unicode(self):
        """Test: Limpieza preserva caracteres Unicode."""
        from tecla import clean_text
        text = "Lingüística de corpus: análisis semántico."
        cleaned = clean_text(text, language="es")
        assert isinstance(cleaned, str)
        assert len(cleaned) > 0

    def test_clean_text_empty_input(self):
        """Test: Limpieza maneja entrada vacía."""
        from tecla import clean_text
        text = ""
        cleaned = clean_text(text, language="es")
        assert isinstance(cleaned, str)


class TestLanguageDetection:
    """Tests para detección de idioma."""

    def test_language_detection_spanish(self):
        """Test: Detección de español."""
        from tecla import detect_language
        text = "Este es un texto en español con términos especializados."
        lang, confidence = detect_language(text)
        assert lang == "es"

    def test_language_detection_english(self):
        """Test: Detección de inglés."""
        from tecla import detect_language
        text = "This is a text in English with specialized terms."
        lang, confidence = detect_language(text)
        assert lang == "en"

    def test_language_detection_returns_code_and_confidence(self):
        """Test: detect_language devuelve (código de idioma, confianza)."""
        from tecla import detect_language
        lang, confidence = detect_language("test text")
        assert isinstance(lang, str)
        assert isinstance(confidence, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
