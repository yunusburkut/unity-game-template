# toon-art

Blender'dan üretilen 3D sanat ve çizgi film (toon) görünümü için. Pixel Volley ve Mixtrol'deki hattın birleşimi.

## Ekledikleri

| Parça | Ne işe yarar |
|---|---|
| `Assets/__GAME__/Game/Art/Shaders/Toon.shader` | `__GAME__/Toon`: iki bantlı ışık, renkli gölge, parlama, kenar ışığı, zemin teması, piksel cinsinden kontur (uzakta incelir: `_OutlineReferenceDistance`), isteğe bağlı dünya uzayında pas ve kir (`_WEAR`) |
| `Assets/__GAME__/Game/Art/Shaders/InkLines.shader` + `Editor/Art/InkLines.cs` | Siluetin içindeki mürekkep çizgileri: PC renderer'ında tam ekran pass. Menü `__GAME__/Art/Add Ink Lines (PC tier)`, CLI `unity command art ink-lines` |
| `Assets/__GAME__/Game/Art/Shaders/Sky.shader` | `__GAME__/Sky`: düz cel gökyüzü, gradyan ve iki basamaklı güneş diski |
| `Tools/Blender/wear_tile.py` | `_WEAR`'ın okuduğu kesintisiz gürültü tile'ını (`Game/Art/Textures/Wear.png`) headless Blender'da pişirir |
| `Assets/__GAME__/Editor/Art/OutlineNormalsPostprocessor.cs` | `Game/Art/Models/` altındaki modellere yumuşatılmış normal pişirir, kontur sert köşede kopmaz |
| `Assets/__GAME__/Editor/Art/ToonShader.cs` | Materyali toon'a geçirir, konturu açıp kapatır (kapalıyken ikinci çizim yok); wear tile'ının import'unu sabitler (linear, repeat) |
| `Assets/__GAME__/Editor/Art/ToonShaderCheck.cs` | Shader'ın her pass'ini ana keyword setleriyle derler, hatayı loga yazar. Oyun kurulurken `ProjectSetup` çalıştırır; menü: `__GAME__/Art/Check Toon Shader` |
| `.claude/skills/art-pipeline` | Blender script → FBX + JSON manifest → postprocessor → builder hattının kuralları |
| `examples/` | Oyuna kopyalanmayan örnekler: `toon_prop.py` + `PropBuilder.cs.txt` (çalışan, genel başlangıç noktası), `kit_common.py` ve `LevelKitModelPostprocessor.cs.txt` (Mixtrol), `city_assets.py` (Pixel Volley, export'u sözleşme öncesi) |

## Seçimler

- Işık Pixel Volley'den: gerçek ana ışık ve gölgesi (gölge mesafesinde yumuşak sönüş), nokta ve spot ışıklar aynı iki
  bantla (Forward ve Forward+), light layer'lar, sis ve light probe'lardan ortam ışığı. Lightmap ve shadowmask
  okunmaz: toon objeler gerçek zamanlı ışıkla aydınlanır, baked ışığı probe'lardan alır. Gölge bandı da ana ışıkla
  ölçeklenir (tint, aydınlık tarafın oranı), bu yüzden akşam, gece ve iç mekân sahneleri bütün olarak kararır. Mixtrol'ün
  sahte sabit ışığı oyuna özeldi.
- Kontur Mixtrol'den: normal, tangent'e pişiriliyor (skinned mesh'te de çalışıyor), kalınlık 1080p piksel cinsinden.
  Telefon ve monitörde aynı kalınlıkta görünüyor. URP renderer'da Depth Priming kapalı kalmalı (varsayılan), yoksa
  kontur kaybolur.
- SSAO (iki bandı ve ortam ışığını koyulaştırır), DBuffer decal'lar (yüzey rengine) ve Adaptive Probe Volume'lar
  okunuyor. SSAO ve decal'ların okuduğu normal için DepthNormals, TAA, STP ve motion blur için MotionVectors,
  lightmapper için Meta pass'i var; GPU Resident Drawer ve LOD cross-fade destekleniyor.
- Wear, ink lines, sky ve outline incelmesi DumpShift'ten geldi. Hepsi varsayılan olarak kapalı ya da etkisiz: wear
  materyal başına açılır, ink lines menüyle eklenir, sky'ı materyal olarak atarsın, `_OutlineReferenceDistance`
  varsayılanı 100 m (eski sabit kalınlık). Birinci şahıs oyunda 1-6 m ver.
- Shader her yeni oyunda `ToonShaderCheck` ile derlenip kontrol ediliyor: `Logs\setup.log` içinde
  `[toon-art] Toon shader OK` yoksa Console'daki `[toon-art]` hatalarına bak.
