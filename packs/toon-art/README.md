# toon-art

Blender'dan üretilen 3D sanat ve çizgi film (toon) görünümü için. Pixel Volley ve Mixtrol'deki hattın birleşimi.

## Ekledikleri

| Parça | Ne işe yarar |
|---|---|
| `Assets/__GAME__/Game/Art/Shaders/Toon.shader` | `__GAME__/Toon`: iki bantlı ışık, renkli gölge, parlama, kenar ışığı, zemin teması, piksel cinsinden kontur |
| `Assets/__GAME__/Editor/Art/OutlineNormalsPostprocessor.cs` | `Game/Art/Models/` altındaki modellere yumuşatılmış normal pişirir, kontur sert köşede kopmaz |
| `Assets/__GAME__/Editor/Art/ToonShader.cs` | Materyali toon'a geçirir, konturu açıp kapatır (kapalıyken ikinci çizim yok) |
| `Assets/__GAME__/Editor/Art/ToonShaderCheck.cs` | Shader'ın her pass'ini ana keyword setleriyle derler, hatayı loga yazar. Oyun kurulurken `ProjectSetup` çalıştırır; menü: `__GAME__/Art/Check Toon Shader` |
| `.claude/skills/art-pipeline` | Blender script → FBX + JSON manifest → postprocessor → builder hattının kuralları |
| `examples/` | Oyuna kopyalanmayan örnekler: `toon_prop.py` + `PropBuilder.cs.txt` (çalışan, genel başlangıç noktası), `kit_common.py` ve `LevelKitModelPostprocessor.cs.txt` (Mixtrol), `city_assets.py` (Pixel Volley, export'u sözleşme öncesi) |

## Seçimler

- Işık Pixel Volley'den: gerçek ana ışık ve gölgesi (gölge mesafesinde yumuşak sönüş), nokta ve spot ışıklar aynı iki
  bantla (Forward ve Forward+), light layer'lar, sis ve light probe'lardan ortam ışığı. Lightmap ve shadowmask
  okunmaz: toon objeler gerçek zamanlı ışıkla aydınlanır, baked ışığı probe'lardan alır. Mixtrol'ün sahte sabit ışığı
  oyuna özeldi.
- Kontur Mixtrol'den: normal, tangent'e pişiriliyor (skinned mesh'te de çalışıyor), kalınlık 1080p piksel cinsinden.
  Telefon ve monitörde aynı kalınlıkta görünüyor. URP renderer'da Depth Priming kapalı kalmalı (varsayılan), yoksa
  kontur kaybolur.
- SSAO ve decal'lar için DepthNormals, lightmapper için Meta pass'i var; GPU Resident Drawer ve LOD cross-fade
  destekleniyor.
- Shader her yeni oyunda `ToonShaderCheck` ile derlenip kontrol ediliyor: `Logs\setup.log` içinde
  `[toon-art] Toon shader OK` yoksa Console'daki `[toon-art]` hatalarına bak.
