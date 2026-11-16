# reference-docs

Okumak için, oyunlara kopyalanmaz. Her biri belirli bir oyun için yazıldı; yöntem ve sayılar başka oyunlarda da işe
yarar.

`packages.md` ile `shipping-2026.md` istisna: her oyuna uyarlar, bu yüzden tek kaynakları gamekit eklentisine taşındı
(`plugin/skills/unity-package-management/references/select-packages.md` ve
`plugin/skills/launch-review/references/shipping-2026.md`); buradaki iki dosya yalnızca oraya işaret eder. Düzeltmeyi
eklentide yap.

Dosyalardaki `docs/...` yolları yazıldıkları oyunun (Mixtrol) deposundaki yollardır: `docs/windows-build.md` buradaki
`windows-build.md`'dir; `docs/level-kit.md`, `docs/network-testing.md` ve `docs/gdd.md` buraya alınmadı. Burada yalnız
tablodaki dosyalar var.

| Dosya | Ne anlatıyor |
|---|---|
| `frame-budget.md` | 60 FPS = 16.6 ms; düz kare süresi, GC sıçramaları, ölçüm yöntemi (Mixtrol) |
| `go-to-market.md` | Bu tür oyunlar nasıl satıyor: kaynaklı rakamlar, Steam sayfası, wishlist (Mixtrol) |
| `market-2026.md` | 2026 pazarı, "friendslop" co-op furyası ve rakipler (Mixtrol) |
| `clarity-playbook.md` | Oyuncuya ne yapacağını anlatmak: tur öncesi ekran, ipuçları, olay anlatımı (Mixtrol) |
| `audio-plan.md` | Hangi sese ihtiyaç var, nereye takılır (Mixtrol, Türkçe) |
| `windows-build.md` | Windows build almak ve ilk build'de bozulanlar (Mixtrol) |
| `claude_blender_character_reference_guide.md` | Tek bir karakterin (Mixtrol, antenli karakter) Blender brief'i, örnek olarak; süreç `blender-image-to-3d`, export `unity-export` becerisinde |
| `design-audit.md` | Bir oyunun tasarım korpusuna göre denetimi, örnek bir audit (Mixtrol) |
| `Sort bulmaca oyunu renk teorisi.md` | Sort bulmaca oyunlarında renk teorisi raporu (Magic Sort) |
| `research_notes/` | O raporun notları: tür karşılaştırması, renk ayırt edilebilirliği, Unity renk hattı, görsel hiyerarşi |
| `packages.md` | İşaretçi: oyuna göre eklenecek paketler ve alınmayanlar `unity-package-management` referansında |
| `shipping-2026.md` | İşaretçi: 2026 mağaza kuralları (Play API 36, AAB, 16 KB, Xcode 26, itch.io WebGL) `launch-review` referansında |
