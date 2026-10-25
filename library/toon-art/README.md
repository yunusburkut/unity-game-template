# toon-art

Blender'dan üretilen 3D sanat ve çizgi film (toon) görünümü için. Pixel Volley ve Mixtrol'deki hattın birleşimi.

## Ekledikleri

| Parça | Ne işe yarar |
|---|---|
| `Assets/__GAME__/Game/Art/Shaders/Toon.shader` | `__GAME__/Toon`: iki bantlı ışık, renkli gölge, parlama, kenar ışığı, zemin teması, piksel cinsinden kontur |
| `Assets/__GAME__/Editor/Art/OutlineNormalsPostprocessor.cs` | `Game/Art/Models/` altındaki modellere yumuşatılmış normal pişirir, kontur sert köşede kopmaz |
| `Assets/__GAME__/Editor/Art/ToonShader.cs` | Materyali toon'a geçirir, konturu açıp kapatır (kapalıyken ikinci çizim yok) |
| `.claude/skills/art-pipeline` | Blender script → FBX + JSON manifest → postprocessor → builder hattının kuralları |
| `examples/` | Kopyalanmayan örnekler: `city_assets.py` (Pixel Volley), `kit_common.py` ve `LevelKitModelPostprocessor.cs.txt` (Mixtrol) |

## Seçimler

- Işık Pixel Volley'den: gerçek ana ışık ve gölge, her sahnede çalışır. Mixtrol'ün sahte sabit ışığı oyuna özeldi.
- Kontur Mixtrol'den: normal, tangent'e pişiriliyor (skinned mesh'te de çalışıyor), kalınlık 1080p piksel cinsinden.
  Telefon ve monitörde aynı kalınlıkta görünüyor.
- Shader henüz bir projede derlenmedi. İlk açılışta Console'da shader hatası var mı bak.
