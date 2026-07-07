"""
TECLA: Complete Extraction Workflow Example

This example demonstrates the full pipeline:
1. Load documents
2. Extract terms using HybridTermExtractor
3. Evaluate results
4. Export glossary
"""

from tecla import HybridTermExtractor, corpus_statistics, evaluate_extraction
import json


def example_spanish_extraction():
    """Complete workflow for Spanish term extraction."""

    print("="*60)
    print("TECLA: Term Extraction Workflow (Spanish)")
    print("="*60)

    # 1. Prepare documents
    # ==================
    print("\n[1/4] Loading documents...")

    documents = [
        {
            "text": "La lingüística de corpus es una disciplina que estudia el lenguaje "
                   "a través de colecciones de textos. Los corpus lingüísticos son "
                   "recursos fundamentales para el análisis terminológico.",
            "doc_id": "doc_001",
            "language": "es",
            "source": "academic_paper"
        },
        {
            "text": "El procesamiento del lenguaje natural utiliza métodos computacionales "
                   "para analizar y generar lenguaje. Las técnicas de extracción "
                   "automática de términos facilitan la construcción de glosarios.",
            "doc_id": "doc_002",
            "language": "es",
            "source": "textbook"
        },
        {
            "text": "La representación distribucional de palabras captura significado mediante "
                   "vectores de contexto. Los embeddings de palabra permiten modelar "
                   "relaciones semánticas entre términos especializados.",
            "doc_id": "doc_003",
            "language": "es",
            "source": "conference_paper"
        }
    ]

    print(f"✓ Loaded {len(documents)} documents")
    total_tokens = sum(len(doc['text'].split()) for doc in documents)
    print(f"✓ Total tokens: {total_tokens}")

    # 2. Initialize extractor
    # =======================
    print("\n[2/4] Initializing HybridTermExtractor...")

    extractor = HybridTermExtractor(language="es")
    print("✓ Extractor initialized for Spanish")
    print("  Methods: POS-based filtering + TF-IDF + C-value")

    # 3. Extract terms
    # ================
    print("\n[3/4] Extracting terms...")

    terms = extractor.extract(documents, top_k=20)

    print(f"✓ Extracted {len(terms)} terms")
    print("\nTop 10 terms:")
    print("-" * 60)
    print(f"{'Rank':<5} {'Term':<30} {'Score':<10}")
    print("-" * 60)

    for i, term in enumerate(terms[:10], 1):
        term_text = term.get('text') or term.get('term', 'N/A')
        score = term.get('score', term.get('tfidf', 0))
        print(f"{i:<5} {term_text:<30} {score:<10.3f}")

    # 4. Analyze results
    # ===================
    print("\n[4/4] Analyzing results...")

    # Count by document frequency
    df_counts = {}
    for term in terms:
        df = term.get('doc_frequency', 1)
        df_counts[df] = df_counts.get(df, 0) + 1

    print("\nTerm distribution by document frequency:")
    for df in sorted(df_counts.keys()):
        print(f"  {df} document(s): {df_counts[df]} terms")

    # Calculate average score
    avg_score = sum(t.get('score', 0) for t in terms) / len(terms) if terms else 0
    print(f"\nAverage extraction score: {avg_score:.3f}")

    return terms


def example_english_extraction():
    """Complete workflow for English term extraction."""

    print("\n" + "="*60)
    print("TECLA: Term Extraction Workflow (English)")
    print("="*60)

    # 1. Prepare documents
    print("\n[1/4] Loading documents...")

    documents = [
        {
            "text": "Corpus linguistics is the discipline that studies language through "
                   "large collections of texts. Linguistic corpora are fundamental "
                   "resources for terminology analysis and natural language research.",
            "doc_id": "doc_001",
            "language": "en",
            "source": "academic_paper"
        },
        {
            "text": "Natural language processing uses computational methods to analyze and "
                   "generate language. Automatic term extraction techniques facilitate "
                   "the construction of specialized glossaries and terminology databases.",
            "doc_id": "doc_002",
            "language": "en",
            "source": "textbook"
        },
        {
            "text": "Distributional representation of words captures meaning through context "
                   "vectors. Word embeddings enable modeling of semantic relationships "
                   "between specialized terms and technical concepts.",
            "doc_id": "doc_003",
            "language": "en",
            "source": "conference_paper"
        }
    ]

    print(f"✓ Loaded {len(documents)} documents")

    # 2. Initialize extractor
    print("\n[2/4] Initializing HybridTermExtractor...")

    extractor = HybridTermExtractor(language="en")
    print("✓ Extractor initialized for English")

    # 3. Extract terms
    print("\n[3/4] Extracting terms...")

    terms = extractor.extract(documents, top_k=20)

    print(f"✓ Extracted {len(terms)} terms")
    print("\nTop 10 terms:")
    print("-" * 60)
    print(f"{'Rank':<5} {'Term':<35} {'Score':<10}")
    print("-" * 60)

    for i, term in enumerate(terms[:10], 1):
        term_text = term.get('text') or term.get('term', 'N/A')
        score = term.get('score', term.get('tfidf', 0))
        print(f"{i:<5} {term_text:<35} {score:<10.3f}")

    # 4. Save results
    print("\n[4/4] Saving results...")

    # Format for export
    glossary = [
        {
            "term": t.get('text') or t.get('term'),
            "score": round(t.get('score', 0), 3),
            "frequency": t.get('frequency', 0),
            "doc_frequency": t.get('doc_frequency', 0)
        }
        for t in terms
    ]

    # Export to JSON
    with open('extracted_glossary.json', 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)

    print("✓ Glossary saved to extracted_glossary.json")

    return terms


def compare_languages():
    """Compare extraction results between English and Spanish."""

    print("\n" + "="*60)
    print("TECLA: Bilingual Comparison")
    print("="*60)

    # Same document in both languages
    shared_text_en = (
        "Terminology extraction from specialized corpora requires combining "
        "linguistic and statistical approaches for optimal results."
    )

    shared_text_es = (
        "La extracción de terminología de corpus especializados requiere combinar "
        "enfoques lingüísticos y estadísticos para obtener resultados óptimos."
    )

    docs_en = [{"text": shared_text_en, "doc_id": "test", "language": "en"}]
    docs_es = [{"text": shared_text_es, "doc_id": "test", "language": "es"}]

    extractor_en = HybridTermExtractor(language="en")
    extractor_es = HybridTermExtractor(language="es")

    terms_en = extractor_en.extract(docs_en, top_k=5)
    terms_es = extractor_es.extract(docs_es, top_k=5)

    print("\nEnglish terms:")
    for term in terms_en[:5]:
        print(f"  • {term.get('text', 'N/A')}")

    print("\nSpanish terms:")
    for term in terms_es[:5]:
        print(f"  • {term.get('text', 'N/A')}")


if __name__ == "__main__":
    # Run examples
    spanish_terms = example_spanish_extraction()
    english_terms = example_english_extraction()
    compare_languages()

    print("\n" + "="*60)
    print("✓ Workflow complete!")
    print("="*60)
