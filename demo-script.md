# Video Kaydı — Demo Script

Önce backend + frontend'in ayakta olduğundan emin ol:
- Backend: `cd backend && uvicorn main:app --port 8000`
- Frontend: `cd frontend && npm run dev`
- Tarayıcı: `http://localhost:5173`

Konu seçmek zorunlu değil gibi düşünme — dropdown'dan seçtiğin konu neyse,
sadece o konudaki dokümanlar arasında arama yapılıyor. Aşağıdaki sorular
hem "KB'de karşılığı kesin olanlardan" hem "kasıtlı konu-dışı" (guardrail
göstermek için) seçildi. İstersen kendi doğal cümlenle de sorabilirsin,
anlamca yakınsa (örn. "MOSFET nedir?" yerine "Explain how a MOSFET works")
yine doğru pasajı bulur — birebir bu kelimeleri kullanman şart değil.

---

## 1. Sohbet — Semiconductors konusu (varsayılan seçili)

Sırayla sor, her birinde: streaming'in aktığını, altında "Kullanılan
kaynaklar" panelinin açıldığını ve skor gösterdiğini, "Export PDF"
butonunu göster.

1. `What is a MOSFET?`
   → 11. MOSFET pasajı, skor ~0.70
2. `What is doping in semiconductors?`
   → 2. Doping pasajı, skor ~0.75 (en yüksek skorlardan biri, güzel örnek)
3. `What is the difference between DRAM and NAND flash?`
   → 14. Memory chips pasajı

**Export PDF**: 2. sorudan sonra butona bas, indirilen PDF'i aç, içeriği
(Query/Topic/Analysis/References) göster.

---

## 2. Konu değiştir → Space Exploration

Sağ üstteki dropdown'dan "Space Exploration" seç.

4. `What is a reusable rocket?`
   → 6. Reusable rockets pasajı
5. `What is the ISS?`
   → 4. The International Space Station pasajı

Bu ikisi konu değiştirmenin gerçekten farklı bir bilgi havuzuna geçtiğini
gösterir (Semiconductors sorularına bu konuda cevap gelmeyeceğini de
istersen ayrıca gösterebilirsin, madde 7'ye bak).

---

## 3. Guardrail / context-dışı soru (kasıtlı, önemli bir demo anı)

Konuyu "Semiconductors"a geri al.

6. `What is the capital of France?`
   → Model reddediyor: *"I don't know based on the provided documents."*
   → Altında **"Not: Bu konuda dokümanlarımda net bir bilgi bulamadım..."**
     notu görünüyor (skor 0.35 altı olduğu için otomatik ekleniyor)
   → Bunu anlatırken vurgula: model kendi genel bilgisinden ("Paris")
     cevap uydurmuyor, sadece yüklü dokümanlarla sınırlı kalıyor.

---

## 4. (Opsiyonel) Konu izolasyonunu göster

7. Konu "Space Exploration" seçiliyken sor: `What is a MOSFET?`
   → Semiconductors'a ait bir soru olduğu için burada da düşük skorlu bir
     "bilmiyorum" cevabı gelecek — konu seçiminin retrieval'ı gerçekten
     kısıtladığının kanıtı.

---

## 5. Dokümanlar sayfası

Sol menüden "📄 Dokümanlar"a geç.
- Mevcut listeyi göster: `sample_docs.md` (Semiconductors, 15 chunk),
  `space_exploration_docs.md` (Space Exploration, 10 chunk), hepsi
  "İndekslendi" durumunda.
- İstersen elindeki bir `.txt` ya da `.pdf` dosyasını sürükle-bırak ile
  yükle, "İndekslendi" olduğunu ve chunk sayısının göründüğünü göster.
  (Not: yeni yüklediğin test dosyasını demo sonrası silmeyi unutma —
  sağdaki "Sil" butonu.)

---

## 6. Telemetri sayfası

Sol menüden "📊 Telemetri"ye geç.
- Canlı CPU/RAM/Disk çubuklarını göster (5 saniyede bir güncelleniyor).
- Alt kısımdaki "Konuya göre bilgi tabanı" tablosunu göster (2 konu,
  doküman/chunk sayıları).
- "100% Offline" rozetini ve "Çalışma süresi"ni göster.

---

## Genel notlar (kayıt sırasında anlatım için)

- Her cevap CPU üzerinde üretiliyor, ~3-4 token/sn — bir cevabın tam
  akması **30-50 saniye** sürebilir, sabırlı ol / kesme.
- Sistem tamamen çevrimdışı: Foundry Local ile hem embedding
  (`qwen3-embedding-0.6b`) hem chat (`phi-3.5-mini`) bu makinede çalışıyor,
  internete hiçbir veri gitmiyor.
- Backend `127.0.0.1:8000`, frontend `[::1]:5173` — ikisi de sadece bu
  bilgisayardan erişilebilir, başka bir cihaz göremez.
