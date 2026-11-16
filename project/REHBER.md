# Rehber

## Yaz

| İstediğin | Yaz |
|---|---|
| Yeni oyunda ilk iş (bir kez) | `/gamekit:new-game şekillendir` (Claude sorar, sen cevaplarsın) |
| Küçük değişiklik (S, 1-3 dosya) | Direkt iste: `topun hızını 1,2 katına çıkar` |
| Özellik, çok dosyalı iş (M) | Direkt iste. Claude PLAN.md'ye spec kartı yazar, yapar, puanlatır. Sonda varsayımlarını söyler: yanlışsa söyle |
| Büyük ya da belirsiz iş (L) | Direkt iste. Claude soru sorar: cevapla. Sonra seçersin: `devam` ya da (Auto modda) `/gamekit:feature` |
| Bir fikri önce dene (atılacak kod) | `prototip: kancadan kancaya sallanmak akıcı hissettiriyor mu` · `dene bakalım ...`. Claude soruyu ölçülebilir yazar, `Prototypes/` altında hızlıca kurar; sen oynarsın, sonuç (PROCEED / PIVOT / KILL) DESIGN.md Decisions'a yazılır, prototip silinir (PIVOT'ta bir sonraki denemeye kadar kalır) |
| Türün alışılmış ayarları | `tür varsayılanları: platformer` (kamera, his, ilk sürüme girmeyecekler) |
| Gözetimsiz yaptır | Auto modda `/gamekit:feature <istek>` (kart hazırsa yalnız `/gamekit:feature`). Bitene kadar yeni iş verme, Play'e girme, Claude Code'u kapatma. İlerleme ve durdurma: ⋮ menüsü > Background tasks (terminalde `/workflows`) |
| Yarım işi sürdür | `devam` |
| Boyut yanlış (Claude'un ilk satırında yazar) | `bu S` · `bu M` · `bu L` |
| Hata | Hata mesajını yapıştır ya da ne olduğunu anlat |
| İkinci göz (kodu puanlar, 9'a kadar düzeltir; bölüm, metin ya da mağaza sayfasında sadece yorumlar) | `review et` · `puanla` |
| Uzman bakışı (sadece okur) | `telefonda 60 fps tutar mı` · `bölümü yorumla` · `metinleri gözden geçir` · `mağaza sayfasını incele` |
| Build ya da test | `webgl build al` (itch.io) · `android build al` · `testleri çalıştır` (Claude onay ister) |
| Review 3 turda 9 olmadı | `devam` (bir tur daha) · `kabul` (açık bulgular Known issues'a, iş teslim) |
| Yarım kartı bırak | `kartı Next'e taşı` (sürdürmek için o işi yine iste) |
| Kod temizliği | `/gamekit:refactor-pass` |
| Şablon güncellemesi | `/gamekit:sync-template` |
| GitHub'a gönder | `push et` (ilk seferde private GitHub reposu açar; Claude kendiliğinden göndermez, onay ister) |
| Yeni işe geç | `/clear`, sonra iste |

## Senin işin

1. Unity açık kalsın. Sahnede kaydetmediğin değişiklik varsa iş vermeden önce kaydet (Ctrl+S). Unity
   birkaç saniyeliğine kendiliğinden Play'e girip çıkarsa (Claude'un kontrolü) dokunma.
2. `PLAN.md` → Pending Play Mode checks: adımları oyunda dene, sonucu yaz: `hepsi tamam` ya da neyin bozulduğunu.
   `unverified` yazan satır Play Mode'da denenmez: Sinyaller'deki `unverified` satırını yap.
3. `PLAN.md` → Next'te `[karar]` satırı varsa: seçeneği seç ya da istenen playtesti oyna, sonucu yaz.
4. Sorulunca onay ver: build, test, push, ilk `/gamekit:feature` (izin kartı). Manual modda her dosya düzenlemesi de sorar; gözetimsiz iş için Auto mod
   (mesaj kutusundaki mod seçici > Auto; terminalde Shift+Tab).

## Sinyaller

| Görürsen | Anlamı | Yap |
|---|---|---|
| `gk-bridge: FAIL` | Kontrol geçmedi (satır nedenini yazar) | Bekle: Claude düzeltir. `unsaved scene` yazıyorsa Ctrl+S, sonra isteği tekrarla. İş durduysa `devam` |
| `UNKNOWN ... does not know 'refresh'` | Bu oyunun Unity köprüsü GameKit'ten eski: derleme kontrolü hep UNKNOWN, `/gamekit:feature` burada çalışmaz | Unity penceresine tıkla (derler), sonra `devam`: Claude `compile.log`'a bakar. Kalıcı çözüm: `/gamekit:sync-template GameKit'e geçir` |
| `UNKNOWN ... does not know` (başka istek) | Bu oyunun köprüsü bu isteği bilmiyor (derleme kontrolü çalışır) | Kalıcı çözüm: `/gamekit:sync-template GameKit'e geçir` |
| `gk-bridge: UNKNOWN` (diğer) | Kontrol yapılamadı (satır nedenini yazar) | `build is running` ya da `test run is in progress` yazıyorsa bitmesini bekle (20 dakikadan uzun sürerse Unity'yi kapatıp aç). `module is not installed` yazıyorsa Unity Hub > Installs > modülü ekle, Unity'yi yeniden aç, sonra `devam`. Değilse: Unity'yi aç, Play'den çık, açılır pencereyi kapat (`unsaved scene` yazıyorsa Ctrl+S). Sonra `devam` |
| Açılışta `Enter Safe Mode?` | Kodda derleme hatası var; Safe Mode'da köprü çalışmaz | `Ignore` seç. Zaten Safe Mode'daysan Console'daki hatayı yapıştır: düzelince Unity Safe Mode'dan kendiliğinden çıkar |
| `unverified` (commit'te ya da Pending'de) | Bir kontrol yapılamadı, commit yine de atıldı | `WebGL` / `PC player`: o build'de dene. `module is not installed`: Unity Hub > Installs > modülü ekle, Unity'yi yeniden aç, sonra `devam`. Başka neden: yanındaki yazıya uyan UNKNOWN satırını yap |
| `Puan: 8/10` ya da `Tur r1 ... 8` | Review 9'un altında | Bekle: Claude düzeltir |

## Durum

| Nerede | Ne var |
|---|---|
| `PLAN.md` | Şu anki iş, spec kartı, Play Mode listesi |
| `DESIGN.md` | Kararlar (Claude'un varsayımları dahil), playtestler |
| `git log` | Yapılanlar |
