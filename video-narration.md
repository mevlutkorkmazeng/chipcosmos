# ChipCosmos — Video Anlatım Metni

Doğal konuşma diliyle yazıldı, ezber değil rehber niyetine — kendi
cümlelerinle söylemen daha samimi durur. **[Aksiyon: ...]** işaretli
yerler ne yapacağını gösteriyor, geri kalanı konuşma metni.

---

## 1. Açılış (~20 sn)

> "Merhaba, ben [isim]. Bu ay boyunca Microsoft Foundry Local kullanarak
> tamamen çevrimdışı çalışan bir RAG — yani Retrieval-Augmented Generation
> — asistanı geliştirdim: ChipCosmos.
>
> Fikir şu: internete hiç bağlanmadan, kendi bilgisayarımda çalışan bir
> yapay zeka modeline sorular soruyorum, o da bana verdiğim dokümanlara
> dayanarak cevap veriyor — uydurma bilgi vermek yerine, sadece elindeki
> kaynaklardan. Şu an iki konuda bilgi tabanım var: yarı iletkenler ve
> uzay araştırmaları. Birlikte deneyelim."

**[Aksiyon: Masaüstündeki ChipCosmos kısayoluna çift tıkla, tarayıcı
otomatik açılsın]**

> "Gördüğünüz gibi tek tıkla hem sunucu hem arayüz ayağa kalkıyor —
> arka planda hem embedding modeli hem sohbet modeli bu bilgisayarda,
> yerel olarak çalışıyor."

---

## 2. Semiconductors — ilk sorular (~2 dk)

**[Aksiyon: Konu "Semiconductors" seçili, soruyu yaz: `What is a MOSFET?`]**

> "Konu olarak şu an 'Semiconductors' seçili. Basit bir soruyla
> başlayalım: MOSFET nedir?"

**[Yanıt akarken]**

> "Cevabın token token, canlı olarak aktığını görüyorsunuz — bu bir
> streaming yanıt, ChatGPT'deki gibi anlık üretiliyor, ama tamamen
> bu bilgisayarda, internete hiçbir veri gitmeden."

**[Yanıt bitince, "Kullanılan kaynaklar" panelini aç]**

> "Ve burada önemli bir kısım: her cevabın altında hangi pasajdan
> geldiğini ve ne kadar alakalı olduğunu — benzerlik skorunu — açıkça
> gösteriyorum. Yani model bir 'kara kutu' değil, hangi bilgiye
> dayandığını denetleyebiliyorum."

**[Aksiyon: `What is doping in semiconductors?` sor]**

> "Bir soru daha soralım — katkılama, yani doping nedir?"

**[Yanıt gelince]**

> "Görüldüğü gibi burada da doğru pasajı bulup, kaynak göstererek
> cevaplıyor."

**[Aksiyon: "Export PDF" butonuna bas, açılan PDF'i göster]**

> "Bir de her cevabı PDF rapor olarak dışa aktarabiliyorum — sorgu,
> konu, tarih ve kaynaklarıyla birlikte, kurumsal bir rapor formatında.
> Bunu isterseniz kayıt altına alıp paylaşabilirsiniz."

---

## 3. Konu değiştirme — Space Exploration (~1.5 dk)

**[Aksiyon: Sağ üstteki dropdown'dan "Space Exploration" seç]**

> "Şimdi konuyu değiştiriyorum: Uzay araştırmaları. Sistem artık
> tamamen farklı bir bilgi tabanında arama yapacak — yarı iletkenlerle
> ilgili hiçbir şey bilmiyormuş gibi davranacak."

**[Aksiyon: `What is a reusable rocket?` sor]**

> "Yeniden kullanılabilir roket nedir, diye soralım."

**[Yanıt gelince, kaynağı göster]**

> "Yine doğru pasajı buldu — bu sefer uzay dokümanlarından."

**[Aksiyon: `What is the ISS?` sor]**

> "Bir soru daha: Uluslararası Uzay İstasyonu nedir?"

---

## 4. Guardrail testi — context dışı soru (~1.5 dk, önemli kısım)

**[Aksiyon: Konuyu tekrar "Semiconductors" yap]**

> "Şimdi asıl ilginç kısma geliyoruz. Bu sistemin en önemli özelliği:
> bilmediği bir şeyi uydurmuyor. Test edelim."

**[Aksiyon: `What is the capital of France?` sor]**

> "Fransa'nın başkenti neresidir diye soruyorum — bu, elimizdeki
> dokümanlarla hiç alakası olmayan bir soru."

**[Yanıt gelince]**

> "Ve görüyorsunuz: model 'Paris' demiyor, kendi genel bilgisinden
> cevap uydurmuyor. Bunun yerine 'dokümanlarımda bu bilgi yok' diyor.
> Hatta altında bir güven notu da ekliyor — çünkü retrieval sırasında
> bulduğu en yakın pasajın benzerlik skoru çok düşük, sistem bunu
> otomatik tespit edip beni uyarıyor. Bu, gerçek dünyada yanlış bilgi
> vermemesi için kritik bir güvenlik katmanı."

---

## 5. (Opsiyonel) Konu izolasyonu (~1 dk)

**[Aksiyon: Konu "Space Exploration" seçiliyken `What is a MOSFET?` sor]**

> "Son bir test daha: Uzay konusundayken yarı iletken sorsam ne olur?"

**[Yanıt gelince]**

> "Yine reddediyor — çünkü konu seçimi gerçekten retrieval'ı
> kısıtlıyor, sadece görsel bir filtre değil, arka planda veritabanı
> sorgusunu da değiştiriyor."

---

## 6. Dokümanlar sayfası (~1 dk)

**[Aksiyon: Sol menüden "Dokümanlar"a geç]**

> "Buraya geçelim. Burada sistemdeki tüm dokümanları görebiliyorum —
> hangi konuya ait, kaç parçaya (chunk) bölünmüş, indekslenme durumu
> ne. İstersem buradan sürükle-bırak ile yeni bir PDF, Word ya da
> metin dosyası yükleyip anında bilgi tabanına ekleyebiliyorum."

**[İsteğe bağlı: bir test dosyası yükle, indekslendiğini göster]**

---

## 7. Telemetri sayfası (~1 dk)

**[Aksiyon: Sol menüden "Telemetri"ye geç]**

> "Son olarak sistem telemetrisi. Burada bilgisayarın anlık CPU, RAM
> ve disk kullanımını canlı olarak görebiliyorum — beş saniyede bir
> güncelleniyor. Alt tarafta da hangi konuda kaç doküman, kaç chunk
> olduğunu özetliyor. Ve tabii ki '%100 Offline' rozeti — bu sistemin
> internete hiç ihtiyaç duymadığının bir hatırlatıcısı."

---

## 8. Kapanış (~20 sn)

> "Özetle: ChipCosmos, Microsoft Foundry Local üzerinde çalışan,
> tamamen yerel, kaynak gösteren ve bilmediğini bilen bir RAG asistanı.
> Backend'i FastAPI, arayüzü React ile yazdım, embedding ve sohbet
> modelleri bu bilgisayarda çalışıyor. Dinlediğiniz için teşekkürler."

---

## Genel hatırlatmalar
- Doğal konuş, metni ezberleme — yukarıdakiler sadece akış rehberi.
- Bir cevabın akması 30-50 saniye sürebilir; o sırada konuşmaya devam
  edebilir ya da sessizce bekleyip ekranı gösterebilirsin.
- Bir yerde hata/beklenmedik bir şey olursa paniklemeden "ilginç,
  bakalım neden" diyip devam edebilirsin — bu doğal bir demo hissi
  verir, sorun değil.
