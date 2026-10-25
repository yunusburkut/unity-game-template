# unity-game-template

Her yeni oyun reposunun başlangıç noktası: Unity 6000.6 + URP iskeleti, PC ve mobil (Android, iOS) ve WebGL
hedefleri, ve hazır bir Claude Code katmanı. mixtrolrepo, PixelVolley ve Magic-Sort-Clone'da işe yarayan her şey
projeden bağımsız hale getirilip buraya taşındı.

## Yeni oyun başlat

```powershell
.\new-game.ps1 -Name SkyHopper
```

1. `C:\GitHub\SkyHopper` oluşur, `__GAME__` her yerde `SkyHopper` olur.
2. `-Packs` ile seçilen paketler eklenir.
3. Feel, Assets\Feel'i olan ilk yerel repodan kopyalanır (ücretli paket, git'e girmez).
4. Unity batch modda `ProjectSetup`'ı çalıştırır (ilk import birkaç dakika).
5. `main` dalında ilk commit atılır.

Sonra: Unity Hub > Add > Add project from disk, ardından o klasörde Claude Code'u aç. İlk iş olarak `CLAUDE.md` ve
`DESIGN.md` içindeki TODO satırlarını doldur (ya da `/grill-me` ile Claude'a sordur).

Parametreler: `-Path D:\Games`, `-Company ad`, `-Packs a,b`, `-FeelFrom C:\GitHub\PixelVolley`, `-NoSetup`, `-NoGit`.

## Paketler

Her oyuna gerekmeyen parçalar `library/` altında durur ve `-Packs` ile eklenir:

```powershell
.\new-game.ps1 -Name SkyHopper -Packs coop-multiplayer,toon-art
```

| Paket | Ekledikleri | Ne zaman |
|---|---|---|
| `coop-multiplayer` | FishNet ağ kuralı, co-op mekanik skill'leri, net-auditor ve idea-forge agent'ları, tasarım korpusu ve co-op dokümanları | 2–4 kişilik online co-op |
| `toon-art` | `__GAME__/Toon` shader'ı, kontur normal pişirici, art-pipeline skill'i (Blender → FBX → prefab) | Blender'dan çizgi film görünümlü 3D |
| `linear` | linear-scout agent'ı ve CLAUDE.md parçası | İşler Linear'da takip ediliyorsa |

Her paketin README'si ne eklediğini ve kurulumdan sonra elle yapılacakları anlatır; README ve `examples/` oyuna
kopyalanmaz. `library/reference-docs/` sadece okumak için: frame budget, pazar, Steam, ses, renk teorisi notları.

## İçinde ne var

| Parça | Nerede |
|---|---|
| Core / Game / Editor / Tests assembly ayrımı, `Easing` örneği ve testleri, Main sahnesini hatasız çalıştıran PlayMode testi | `project/Assets/__GAME__/` |
| Mobil + PC kurulumu: URP Mobile ve PC kalite seviyeleri, sadece Input System, Linear, IL2CPP ARM64, Nice Vibrations define'ı, Main sahnesi | `Editor/ProjectSetup.cs` |
| Windows / Android / iOS / WebGL build menüsü, itch.io WebGL boyut ayarları | `Editor/BuildMenu.cs` |
| Claude için derleme, konsol, test, build logları ve `play-capture` (Play Mode'a girip 3 ekran görüntüsü + hatalar) | `Editor/AgentBridge.cs` |
| Telefonda 60 fps, çentik için `SafeAreaFitter`, clamp'li `SimulationStep`, Development Build'de kare süresi CSV'si (`FrameLog`, F3) | `Game/` |
| CLAUDE.md, DESIGN.md, README, `.gitattributes` (LF), VS Code eklenti önerisi | `project/` |
| İzinler, Unity YAML koruma hook'u, C# LSP ve context7 eklentileri | `project/.claude/settings.json`, `hooks/` |
| 20 skill: mimari, performans, debug, review, test, doğrulama, refactor-pass, editor CLI, platformlar, Feel (+ tarifler), game-feel, player-clarity, level-beat-review, launch-review (Steam, Google Play, App Store, itch.io), grill-me, Unity'nin resmi 4 skill'i | `project/.claude/skills/` |
| 6 salt okunur agent: unity-reviewer, bug-hunter, perf-auditor, clarity-reviewer, design-critic, launch-auditor | `project/.claude/agents/` |

Blender skill'leri globalde (`~/.claude/skills`) olduğu için her oyunda zaten var.

## Bilerek alınmayanlar

- Mixtrol'ün karaktere ve level kit'e özel Editor builder'ları ve ağ gecikmesi için yazılmış `FramePacing`: o oyuna
  bağlılar. Desen örneği olarak `library/toon-art/examples/` içinde bir import postprocessor ve Blender script'leri var.
- PixelVolley'nin `LevelCatalog` / `LevelInspectorWindow` ve Magic Sort'un `AssetGen` / `PreviewCapture` araçları:
  oyuna özeller. Magic Sort'taki ekran yakalama fikri genelleştirilip `play-capture` oldu.
- PrimeTween, FishNet ve 2D paketleri: manifest bilerek küçük; oyun ihtiyaç duyunca eklenir.
- `learneter` ve `portfolio-site`: Unity projesi değiller.

## Eksikler

- Android build için Unity Hub'dan **Android Build Support** modülünü ekle (şu an sadece Windows ve WebGL kurulu).
- iOS build bir Xcode projesi üretir; imzalama ve derleme Mac'te yapılır.

## Template'i güncellemek

Bir oyunda işe yarayan bir kural ya da skill çıkarsa, onu projeden bağımsız hale getirip `project/` altına ekle.
Mevcut oyunlar etkilenmez; sadece bundan sonra açılanlar alır.
