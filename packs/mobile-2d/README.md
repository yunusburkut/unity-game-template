# mobile-2d

Magic Sort gibi 2D (sprite tabanlı) oyunlar için. Paket eklenince:

1. `Packages/manifest.json` içine Magic Sort'taki 2D paketleri eklenir: 2D Sprite, Tilemap ve Tilemap Extras,
   2D Animation, Aseprite ve PSD importer, 2D Tooling. Sürümler `packages.json` içinde.
2. `ProjectSetup` bittikten sonra `Setup2D` çalışır:
   - Mobile ve PC URP asset'leri tek bir 2D Renderer kullanır (`Settings/URP_2D_Renderer.asset`): sprite'lar,
     `Light2D`, sorting layer'lar.
   - Editor 2D modda açılır: yeni texture'lar sprite olarak import edilir, Scene görünümü 2D olur.
   - `Main` sahnesinde 3D güneş silinir, kamera ortografik olur (size 5), bir Global Light 2D eklenir.

Mobil kurulumun geri kalanı (dokunmatik giriş, safe area, 60 fps, kalite seviyeleri) template'ten gelir.

Elle yapılacak bir şey yok. **<Oyun> > Set Up Project**'i tekrar çalıştırmak bu adımı da yeniden uygular: URP
asset'lerinin renderer listesi tek 2D renderer'a döner, `Main` sahnesindeki ışıklar silinir ve kamera yeniden
ortografik size 5'e, (0, 0, -10)'a ayarlanır. Bunları değiştirdiysen önce commit et. Açık sahnede kaydedilmemiş
değişiklik varsa Unity önce kaydetmeyi sorar; iptal edersen `Main` sahnesine dokunulmaz.

## CLAUDE.md'ye eklenecek satır

```
- 2D: sprites render through the URP 2D Renderer (`Settings/URP_2D_Renderer.asset`). Use `Light2D`, sorting layers
  and a Sprite Atlas per screen, not 3D lights or per-sprite materials; one atlas per screen keeps phone draw calls low.
```
