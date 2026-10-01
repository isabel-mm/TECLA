import pandas as pd
from .compute_irt import evaluate_corpus_irt_anotado
from .metrics import extract_all_terms


df = pd.read_csv("results/en/features_labeled_BIO.csv")
# debe tener columnas: file_id, token, label

terms = extract_all_terms(df)
print(f"Número total de UTs reconstruidas: {len(terms)}")
print(f"Términos únicos anotados: {len(set(terms))}")

resultado = evaluate_corpus_irt_anotado(df)
print(resultado)
