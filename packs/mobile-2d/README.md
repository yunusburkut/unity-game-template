# mobile-2d

Magic Sort gibi 2D (sprite tabanlı) oyunlar için. Paket eklenince:

1. `Packages/manifest.json` içine Magic Sort'taki 2D paketleri eklenir: 2D Sprite, Tilemap ve Tilemap Extras,
   2D Animation, Aseprite ve PSD importer, 2D Tooling. Sürümler `packages.json` içinde.
2. `ProjectSetup` bittikten sonra `Setup2D` çalışır:
   - Mobile ve PC URP asset'leri tek bir 2D Renderer kullanır (`Settings/URP_2D_Renderer.asset`): sprite'lar,
     `Light2D`, sorting layer'lar. `ProjectSetup`'ın yarattığı `URP_Mobile_Renderer.asset` ve `URP_PC_Renderer.asset`
     yerinde kalır (her Set Up Project yeniden yaratır) ama 2D oyunda kullanılmaz.
   - Mobile URP asset'inde MSAA kapanır: sprite kenarına katkısı az, telefonun tile GPU'sunda bant genişliği yer.
     PC'deki değer oyunun kararı.
   - Editor 2D modda açılır: yeni texture'lar sprite olarak import edilir, Scene görünümü 2D olur.
   - `Main` sahnesinde 3D güneş silinir, kamera ortografik olur (size 5), bir Global Light 2D eklenir.

Mobil kurulumun geri kalanı (dokunmatik giriş, safe area, 60 fps, kalite seviyeleri) template'ten gelir.

Elle yapılacak tek şey: aşağıdaki satır oyunun `CLAUDE.md`'sinde yoksa ekle (bu README oyuna kopyalanmaz, satır
eklenmezse agent'lar 2D kurallarını bilmez).

**GameKit > Set Up Project**'i tekrar çalıştırmak güvenli: varsayılan renderer'ı zaten 2D olan URP asset'ine
dokunulmaz (MSAA dahil), `Main` sahnesi de içinde bir `Light2D` ya da ortografik kamera varken değiştirilmez.
Sonradan eklediğin renderer'lar, kamera ayarı ve ışıklar korunur; global ışığı silsen de kamera ortografik kaldıkça
sahne yeniden dönüştürülmez. `Main` açık değilse arka planda (additive) açılıp kapatılır; açık sahnelerin değişmez.
`Main` açık ve kaydedilmemiş değişiklik içeriyorsa Unity önce kaydetmeyi sorar; kaydetmezsen `Main`'e dokunulmaz.

## CLAUDE.md'ye eklenecek satır

```
- 2D: sprites render through the URP 2D Renderer (`Settings/URP_2D_Renderer.asset`). Use `Light2D`, sorting layers
  and a Sprite Atlas per screen, not 3D lights or per-sprite materials; one atlas per screen keeps phone draw calls low.
  Sprite sources follow the Art section (I supply or approve each one; every one gets a `docs/asset-sources.md` row).
  `Settings/URP_Mobile_Renderer.asset` and `URP_PC_Renderer.asset` are unused 3D renderers that Set Up Project
  recreates: tune the 2D renderer and the URP_* pipeline assets, never them. Levels: one Grid, one Tilemap per layer
  (Chunk render mode for static tiles, Individual only where sprites must sort between tiles), solids through
  TilemapCollider2D merged into a CompositeCollider2D, rule tiles from Tilemap Extras. Characters: 2D Animation
  (PSD Importer rig) or sprite-sheet clips; keep each Animator small (blend trees, sub-state machines, no Any State
  web) and drive it from Game code that reads Core state, never the other way.
```
