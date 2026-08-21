"""
Hafta 5 - test_queries.py

rag.py'deki answer_query() fonksiyonunu 20 soruyla test eder:
  - 15 pasajın her biriyle ilgili, context'te cevabı olan birer soru
  - 5 çeşitli konuda (tarih, coğrafya, biyoloji, matematik, spor),
    pasajlarda hiç geçmeyen, cevaplanamaması gereken soru

Her soru-cevap çiftini numaralandırıp yazdırır, sonunda bir sonuç
tablosu ve özet verir:
  - context'e uygun cevaplanan soru sayısı
  - cevaplanamaz sorularda modelin gerçekten "bilmiyorum" dediği sayı

Not: Bu otomatik değerlendirme kaba bir sezgiseldir (anahtar kelime /
"bilmiyorum" ifadesi arama); kesin doğruluk için cevapları elle de
okumak gerekir.

Çalıştırma:
    python test_queries.py
"""

from rag import answer_query

# (soru, context'te bekleniyorsa doğrulama için anahtar kelimeler; context
# dışı (cevaplanamaz) sorularda None)
QUESTIONS = [
    # 15 pasajın her biri için birer cevaplanabilir soru
    ("What is a semiconductor?", ["semiconduct", "conduct"]),
    ("What is doping in semiconductors?", ["dop", "impurit"]),
    ("What is a P-N junction?", ["junction", "p-n"]),
    ("What is a transistor used for?", ["transistor"]),
    ("What is Moore's Law?", ["moore"]),
    ("What is an integrated circuit?", ["integrated circuit", "microchip"]),
    ("What happens during wafer fabrication?", ["wafer", "fab"]),
    ("What is photolithography used for?", ["photolithography", "lithography"]),
    ("What is a band gap?", ["band gap"]),
    ("What are compound semiconductors used for?", ["gallium", "compound semiconductor"]),
    ("What is a MOSFET?", ["mosfet"]),
    ("What is a diode used for?", ["diode"]),
    ("What is a semiconductor foundry?", ["foundry", "tsmc"]),
    ("What is the difference between DRAM and NAND flash?", ["dram", "nand"]),
    ("Why is heat dissipation a challenge in semiconductor devices?", ["heat", "dissipat"]),
    # 5 çeşitli konuda, context dışı (cevaplanamaması gereken) soru
    ("Who was the first president of the United States?", None),
    ("What is the longest river in the world?", None),
    ("What is the function of mitochondria in a cell?", None),
    ("What is the Pythagorean theorem?", None),
    ("How many players are on a soccer team?", None),
]

REFUSAL_PHRASES = [
    "don't know", "do not know", "not mentioned", "no information",
    "cannot answer", "can't answer", "not provided", "not in the context",
    "not available in the context", "unable to answer", "not sure",
    "doesn't contain", "does not contain", "not covered", "not related",
    "don't have information", "i'm sorry, but i don't",
]


def looks_grounded(answer: str, keywords: list[str]) -> bool:
    lowered = answer.lower()
    return any(kw in lowered for kw in keywords)


def looks_like_refusal(answer: str) -> bool:
    lowered = answer.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def main():
    results = []  # (no, tür, soru, durum)

    for i, (question, keywords) in enumerate(QUESTIONS, start=1):
        print(f"\n[{i}] Soru: {question}")
        answer, sources = answer_query(question)
        print(f"    Cevap: {answer}")
        if sources:
            top_title, top_score = sources[0]
            print(f"    En iyi kaynak: {top_title} (score: {top_score:.2f})")

        if keywords is not None:
            ok = looks_grounded(answer, keywords)
            status = "OK (context'e uygun)" if ok else "KONTROL ET (anahtar kelime bulunamadı)"
            results.append((i, "Cevaplanabilir", question, status))
        else:
            ok = looks_like_refusal(answer)
            status = "OK (bilmiyorum dedi)" if ok else "UYARI (uydurmus olabilir)"
            results.append((i, "Context-disi", question, status))

        print(f"    -> {status}")

    answerable_total = sum(1 for _, kind, _, _ in results if kind == "Cevaplanabilir")
    grounded_count = sum(
        1 for _, kind, _, status in results if kind == "Cevaplanabilir" and status.startswith("OK")
    )
    unanswerable_total = sum(1 for _, kind, _, _ in results if kind == "Context-disi")
    refusal_count = sum(
        1 for _, kind, _, status in results if kind == "Context-disi" and status.startswith("OK")
    )

    print("\n" + "=" * 90)
    print("SONUC TABLOSU")
    print("=" * 90)
    print(f"{'#':<3} {'Tur':<16} {'Soru':<48} {'Durum'}")
    print("-" * 90)
    for i, kind, question, status in results:
        q_display = question if len(question) <= 48 else question[:45] + "..."
        print(f"{i:<3} {kind:<16} {q_display:<48} {status}")

    print("\n" + "=" * 90)
    print("OZET")
    print("=" * 90)
    print(f"Context'e uygun cevaplanan sorular       : {grounded_count}/{answerable_total}")
    print(f"'Bilmiyorum' diyen cevaplanamaz sorular   : {refusal_count}/{unanswerable_total}")


if __name__ == "__main__":
    main()
