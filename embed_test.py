"""
Hafta 2 - Embedding testi

sample_docs.md içindeki 5 pasajı Foundry Local'in embedding modeliyle
(qwen3-embedding-0.6b) vektöre çevirir, sorgu metnini de embed'ler ve
cosine similarity ile en alakalı pasajı bulur.

Çalıştırmadan önce:
    pip install -r requirements.txt

Çalıştırma:
    python embed_test.py
"""

import re
from pathlib import Path

import numpy as np

from foundry_local_sdk import Configuration, FoundryLocalManager

DOCS_PATH = str(Path(__file__).parent / "sample_docs.md")
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
QUERY = "What is doping in semiconductors?"


def load_passages(path: str) -> list[str]:
    """sample_docs.md dosyasını '## N. Başlık' bölümlerine ayırır."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # İlk "## " öncesindeki başlık/giriş metnini at, geri kalanı pasajlara böl.
    sections = re.split(r"(?m)^## ", content)[1:]
    return [section.strip() for section in sections if section.strip()]


def get_embedding_model(manager: FoundryLocalManager, alias: str):
    """Katalogdan verilen alias'ı bulur; yoksa mevcut ilk embedding modeline düşer."""
    model = manager.catalog.get_model(alias)
    if model is not None:
        return model

    print(f"Uyarı: '{alias}' katalogda bulunamadı, mevcut bir embedding modeli aranıyor...")
    for candidate in manager.catalog.list_models():
        if candidate.info.task == "embeddings":
            print(f"'{candidate.alias}' kullanılacak.")
            return candidate

    raise RuntimeError("Katalogda hiç embedding modeli bulunamadı.")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    passages = load_passages(DOCS_PATH)
    print(f"{len(passages)} pasaj yüklendi ({DOCS_PATH}).")

    # hello_model.py ile aynı mimari: tekil FoundryLocalManager, catalog üzerinden
    # model seçimi, indirme/yükleme adımları.
    FoundryLocalManager.initialize(Configuration(app_name="local-rag-assistant"))
    manager = FoundryLocalManager.instance

    model = get_embedding_model(manager, EMBEDDING_MODEL_ALIAS)
    print(f"'{model.alias}' modeli indiriliyor/yükleniyor (ilk çalıştırmada indirme yapabilir)...")
    model.download()
    model.load()

    embedding_client = model.get_embedding_client()

    print("Pasajlar embed ediliyor...")
    passages_response = embedding_client.generate_embeddings(passages)
    passage_vectors = [np.array(item.embedding) for item in passages_response.data]

    print("Sorgu embed ediliyor...")
    query_response = embedding_client.generate_embedding(QUERY)
    query_vector = np.array(query_response.data[0].embedding)

    similarities = [cosine_similarity(query_vector, vec) for vec in passage_vectors]

    ranked = sorted(zip(similarities, passages), key=lambda x: x[0], reverse=True)

    print(f"\nSoru: {QUERY}\n")
    print("--- Benzerlik sıralaması ---")
    for score, passage in ranked:
        title = passage.splitlines()[0]
        print(f"{score:.4f}  {title}")

    best_score, best_passage = ranked[0]
    print("\n--- En alakalı pasaj ---")
    print(f"(benzerlik: {best_score:.4f})")
    print(best_passage)


if __name__ == "__main__":
    main()
