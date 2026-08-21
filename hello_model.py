"""
Hafta 1 - "Hello Model" testi

Bu script, Foundry Local'in bilgisayarında düzgün kurulduğunu doğrular.
Küçük bir modeli (phi-3.5-mini) indirir/çalıştırır ve basit bir tamamlama üretir.

Çalıştırmadan önce:
    pip install -r requirements.txt

Çalıştırma:
    python hello_model.py
"""

from foundry_local_sdk import Configuration, FoundryLocalManager

# Kullanılacak model - küçük ve hızlı, ilk test için ideal
MODEL_ALIAS = "phi-3.5-mini"


def main():
    print(f"'{MODEL_ALIAS}' modeli başlatılıyor (ilk çalıştırmada indirme yapabilir, biraz sürebilir)...")

    # Foundry Local yöneticisini başlat (yerel Foundry Local Core'a bağlanır).
    FoundryLocalManager.initialize(Configuration(app_name="local-rag-assistant"))
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(MODEL_ALIAS)
    if model is None:
        raise RuntimeError(f"Model '{MODEL_ALIAS}' katalogda bulunamadı.")

    model.download()
    model.load()

    chat_client = model.get_chat_client()
    # Bu bilgisayarda CPU üzerinde üretim yavaş; sınırsız üretim (varsayılan
    # 2048 token'a kadar) dahili bir zaman aşımına takılıp iptal edilebiliyor.
    chat_client.settings.max_tokens = 100
    response = chat_client.complete_chat(
        [{"role": "user", "content": "Merhaba, kendini bir cümlede tanıt."}]
    )

    print("\n--- Model cevabı ---")
    print(response.choices[0].message.content)
    print("\nKurulum başarılı! Foundry Local çalışıyor.")


if __name__ == "__main__":
    main()
