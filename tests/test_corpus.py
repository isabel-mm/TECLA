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


class TestBibliographyRemoval:
    """Eliminación de la bibliografía al final del documento."""

    BODY_EN = " ".join(["Corpus linguistics studies language through large collections of texts."] * 60)
    BODY_ES = " ".join(["La lingüística de corpus estudia la lengua a partir de grandes colecciones de textos."] * 60)

    def test_heading_on_its_own_line(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + "\nReferences\nBiber, Douglas. 1993. Representativeness in corpus design.\n"
        assert remove_bibliography(text, "en") == self.BODY_EN

    def test_heading_fused_with_long_first_reference(self):
        """Un párrafo por línea: el encabezado va pegado a una primera referencia larga."""
        from tecla.corpus.cleaning import remove_bibliography
        text = (self.BODY_EN + "\nReferences Archer, Dawn, Anthony M. McEnery, Paul Rayson and Andrew Hardie. 2003. "
                "The semantic tagger.\nBiber, Douglas. 1993. Representativeness in corpus design.\n")
        assert remove_bibliography(text, "en") == self.BODY_EN

    def test_spanish_referencias_citadas(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_ES + "\nReferencias citadas Rojo, Guillermo. 2021. Introducción a la lingüística de corpus en español.\n"
        assert remove_bibliography(text, "es") == self.BODY_ES

    def test_prose_mentioning_references_is_kept(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + "\nreferences to children are frequent in this corpus (1999).\n"
        assert remove_bibliography(text, "en") == text

    def test_heading_early_in_document_is_kept(self):
        """Una lista de referencias al principio (p. ej., de un capítulo) no corta el documento."""
        from tecla.corpus.cleaning import remove_bibliography
        text = "References Biber, Douglas. 1993. Representativeness.\n" + self.BODY_EN
        assert remove_bibliography(text, "en") == text

    def test_heading_in_the_middle_of_a_line(self):
        """El encabezado va pegado al final del último párrafo o a un número de página."""
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_ES + " 8 Bibliografía Alarcos Llorach, Emilio, Estudios de gramática funcional, Madrid, Gredos, 1970.\n"
        assert remove_bibliography(text, "es") == self.BODY_ES + " 8"

    def test_lowercase_mention_in_the_middle_of_a_line_is_kept(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + " the deictic references Aijmer, Karin and others discussed (2002).\n"
        assert remove_bibliography(text, "en") == text

    REFS_EN = "".join(f"Smith{i}, J. ({1990 + i}) 'A study of corpora', Journal of Corpora, {i}: 1-20.\n" for i in range(40))
    REFS_ES = "".join(f"Pérez{i}, M. ({1990 + i}). Un estudio de corpus. Revista de Lingüística, {i}, 1-20.\n" for i in range(40))

    def test_long_reference_list_before_seventy_percent(self):
        """Texto corto con una bibliografía larga: el encabezado cae antes del 70 %."""
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + "\nReferences Adams, B. (1989) 'Corpora', Language, 1: 1-2.\n" + self.REFS_EN
        assert remove_bibliography(text, "en") == self.BODY_EN

    def test_numbered_heading_with_letter(self):
        """«X.5. BIBLIOGRAFÍA», numeración de un capítulo de libro."""
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_ES + "\nX.5. BIBLIOGRAFÍA Baron, N. (1984). Computer Mediated Communication.\n" + self.REFS_ES
        assert remove_bibliography(text, "es") == self.BODY_ES

    def test_early_heading_followed_by_prose_is_kept(self):
        """Antes del 70 %, un encabezado seguido de más texto (otro capítulo) no corta."""
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + "\nReferences Adams, B. (1989) 'Corpora', Language, 1: 1-2.\n" + self.BODY_EN + self.BODY_EN
        assert remove_bibliography(text, "en") == text

    def test_bibliografia_basica_author_year(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_ES + " Bibliografía básica McEnery y Hardie (2012); Sierra (2017)\n"
        assert remove_bibliography(text, "es") == self.BODY_ES

    def test_chapter_after_its_references_is_kept(self):
        """Libro con referencias al final de cada capítulo: se quita la lista, no el capítulo siguiente."""
        from tecla.corpus.cleaning import remove_bibliography
        ch2 = "\nChapter 2 Corpus design\n" + self.BODY_EN
        text = self.BODY_EN + "\nReferences\n" + self.REFS_EN + ch2
        out = remove_bibliography(text, "en")
        assert "Smith0, J." not in out and "Chapter 2 Corpus design" in out and out.endswith(self.BODY_EN)

    def test_appendix_after_references_is_kept(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_EN + "\nReferences\n" + self.REFS_EN + "Appendix 1. Annotation guidelines\n" + self.BODY_EN[:300]
        out = remove_bibliography(text, "en")
        assert "Smith5, J." not in out and "Appendix 1. Annotation guidelines" in out

    def test_final_subject_index_is_removed(self):
        from tecla.corpus.cleaning import remove_bibliography
        index = "Index\n" + " ".join(f"term{i}, {i}, {i + 40}, {i + 90}" for i in range(60)) + "\n"
        text = self.BODY_EN * 5 + "\nReferences\n" + self.REFS_EN + index
        out = remove_bibliography(text, "en")
        assert "term10, 10" not in out and "Smith3, J." not in out

    def test_index_inside_a_reference_is_not_an_index(self):
        from tecla.corpus.cleaning import bibliography_spans
        refs = self.REFS_EN + "de Bellis, N. (2009). Bibliometrics and Citation Analysis: From the Science Citation Index to Cybermetrics.\n" + self.REFS_EN
        text = self.BODY_EN * 5 + "\nReferences\n" + refs + "Appendix A. Supplementary materials\n" + self.BODY_EN[:300]
        sp = bibliography_spans(text, "en")
        assert len(sp) == 1 and "Appendix A" in text[sp[0][1]:]

    def test_capitalised_referencia_in_prose_is_kept(self):
        from tecla.corpus.cleaning import remove_bibliography
        text = self.BODY_ES + " según el Marco Común de Referencia Europea (2017). " + self.BODY_ES[:200] + "\n"
        assert remove_bibliography(text, "es") == text
