# ChipCosmos — 2 Dakikalık Video (Sıkıştırılmış)

## ÖNEMLİ: Kayıttan ÖNCE yap (bunlar kayıtta olmayacak)

Her cevap 30-50 saniye sürüyor — bunları kayıt BAŞLAMADAN önce sorup
bitmesini bekle. Kayıtta sadece hazır duran bu sohbeti gezeceksin.

**[Konu: Semiconductors]**
1. `What is a MOSFET?` — bitmesini bekle
2. `What is the capital of France?` — bitmesini bekle (guardrail örneği)

**[Konu: Space Exploration]**
3. `What is the ISS?` — bitmesini bekle

Sohbeti temizleme/yenileme — bu 3 soru-cevap ekranda dururken kayda başla.

---

## KAYIT (hedef: 110-120 sn)

### 0-10 sn — Açılış
**[Ekran: sohbet sayfası, en üstte]**

> "Merhaba, ben [isim]. Bu, ChipCosmos — Microsoft Foundry Local ile
> tamamen çevrimdışı çalışan bir RAG asistanı. Hızlıca gösteriyorum."

### 10-35 sn — Sohbet geçmişini göster (kaydırarak)
**[Aksiyon: Aşağı kaydır, MOSFET cevabını ve kaynak panelini göster]**

> "MOSFET nedir diye sordum, doğru pasajdan kaynak göstererek
> cevapladı — burada benzerlik skorunu da görüyorsunuz, kara kutu
> değil."

### 35-55 sn — Guardrail (en önemli kısım)
**[Aksiyon: Fransa'nın başkenti sorusuna kaydır]**

> "Bilmediği bir şeyi sorduğumda — Fransa'nın başkenti gibi, alakasız
> bir soru — uydurmuyor. 'Dokümanlarımda yok' diyor, hatta düşük
> güven skorunu otomatik tespit edip bunu belirtiyor."

### 55-75 sn — Konu değiştirme + PDF export
**[Aksiyon: ISS cevabına kaydır, konu etiketini göster; sonra bir
mesajda "Export PDF" butonuna bas]**

> "Konu değiştirdiğimde tamamen farklı bir bilgi tabanında arıyor —
> burada uzay araştırmalarından bir örnek. Ve her cevabı böyle PDF
> rapor olarak da dışa aktarabiliyorum."

**[PDF açılınca 2 saniye göster, kapat]**

### 75-95 sn — Dokümanlar sayfası
**[Aksiyon: Sol menü → Dokümanlar]**

> "Buradan yeni doküman yükleyip anında bilgi tabanına ekleyebiliyorum
> — PDF, Word, metin dosyası fark etmez."

### 95-115 sn — Telemetri + kapanış
**[Aksiyon: Sol menü → Telemetri]**

> "Ve burada sistemin canlı CPU, RAM, disk kullanımı — her şey bu
> bilgisayarda çalışıyor, internete hiç ihtiyaç yok. Backend FastAPI,
> arayüz React ile yazıldı. Teşekkürler!"

---

## Alternatif: Süre biraz taşarsa kısaltma önceliği
Sırasıyla şunları atla (en az önemliden en çoğa):
1. Dokümanlar sayfası (75-95 sn bölümü) — tamamen çıkarılabilir
2. PDF export gösterimi — sadece "PDF olarak da indirebiliyorum" diyip
   tıklamadan geçebilirsin
3. Asla atlama: Guardrail kısmı (35-55 sn) — projenin en güçlü noktası
