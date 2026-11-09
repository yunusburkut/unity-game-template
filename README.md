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
5. `main` dalında ilk commit atılır; Unity Smart Merge sürücüsü ve `.meta` pre-commit hook'u açılır.

Sonra: Unity Hub > Add > Add project from disk, ardından o klasörde Claude Code'u aç. İlk iş olarak `CLAUDE.md` ve
`DESIGN.md` içindeki TODO satırlarını doldur (ya da `/grill-me` ile Claude'a sordur).

Parametreler: `-Path D:\Games`, `-Company ad`, `-Packs a,b`, `-FeelFrom C:\GitHub\PixelVolley`, `-NoSetup`, `-NoGit`.

## Paketler

Her oyuna gerekmeyen parçalar `packs/` altında durur ve `-Packs` ile eklenir:

```powershell
.\new-game.ps1 -Name SkyHopper -Packs coop-multiplayer,toon-art
```

| Paket | Ekledikleri | Ne zaman |
|---|---|---|
| `coop-multiplayer` | FishNet ağ kuralı, co-op mekanik skill'leri, net-auditor ve idea-forge agent'ları, tasarım korpusu ve co-op dokümanları | 2–4 kişilik online co-op |
| `toon-art` | `__GAME__/Toon` shader'ı, kontur normal pişirici, art-pipeline skill'i (Blender → FBX → prefab) | Blender'dan çizgi film görünümlü 3D |
| `linear` | linear-scout agent'ı ve CLAUDE.md parçası | İşler Linear'da takip ediliyorsa |
| `mobile-2d` | Magic Sort'taki 2D paketleri (sprite, tilemap, aseprite, psdimporter, 2D animation), URP 2D Renderer, 2D Editor modu, ortografik kamera + Global Light 2D | Magic Sort gibi sprite tabanlı mobil oyun |
| `steam` | Steamworks.NET, ilk sahneden önce başlayan `SteamBootstrap`, telefon ve WebGL'de Steam'i kapatan define, steam-deploy CI örneği | Steam'de satılacak PC oyunu |
| `mobile-store` | Google Play In-App Review + iOS StoreKit puan isteği (`StoreReview`), Unity Mobile Notifications | Play Store / App Store'a çıkacak mobil oyun |
| `ci-github` | GameCI ile GitHub Actions: main'e her push'ta ve her PR'da testler, Windows / Android / WebGL build'i, `v*` tag'inde itch.io'ya butler push | Bulutta test ve build, itch.io'ya otomatik yükleme |

Bir paketin `packages.json` dosyası varsa, içindeki UPM paketleri ve scoped registry'ler yeni oyunun
`Packages/manifest.json` dosyasına eklenir. `[ProjectSetupStep]` ile işaretlenmiş Editor metotları `ProjectSetup`'tan
sonra çalışır.

Her paketin README'si ne eklediğini ve kurulumdan sonra elle yapılacakları anlatır; README ve `examples/` oyuna
kopyalanmaz. `packs/reference-docs/` sadece okumak için: frame budget, pazar, Steam, ses, renk teorisi notları,
oyuna göre eklenecek paketler (`packages.md`) ve 2026 mağaza kuralları (`shipping-2026.md`).

## İçinde ne var

| Parça | Nerede |
|---|---|
| Core / Game / Editor / Tests assembly ayrımı, `Easing` örneği ve testleri, Main sahnesini hatasız çalıştıran PlayMode testi | `project/Assets/__GAME__/` |
| Mobil + PC kurulumu: URP Mobile ve PC kalite seviyeleri, sadece Input System, Linear, IL2CPP ARM64, Android target API 36 ve "game" kategorisi, Nice Vibrations define'ı, Main sahnesi. Tekrar çalıştırmak şirket/ürün adını, bundle id'yi, URP asset'lerini ve kalite seviyelerini korur; diğer ayarları yeniden uygular (`mobile-2d` paketi varsa onun adımı da: renderer listesi, `Main` kamerası ve ışıklar) | `Editor/ProjectSetup.cs` |
| Windows / Android APK / Google Play AAB / iOS / WebGL build menüsü, Development Build, itch.io için Brotli WebGL | `Editor/BuildMenu.cs` |
| Claude için derleme, konsol, test, build logları; odak gerektirmeyen `refresh`, platform kodunu denetleyen `compile ios/android`, `play-capture` (Play Mode'a girip 3 ekran görüntüsü + hatalar) | `Editor/AgentBridge.cs` |
| Telefonda 60 fps, çentik için `SafeAreaFitter`, clamp'li `SimulationStep`, Development Build'de kare süresi CSV'si (`FrameLog`, F3) | `Game/` |
| CLAUDE.md, DESIGN.md (kararlar ve playtest kaydı dahil), CLAUDE.md'ye import edilen `PLAN.md` (şu anki iş, sıradakiler, bekleyen Play Mode kontrolleri), README, `.editorconfig`, VS Code eklenti önerisi | `project/` |
| Branch + PR akışı: PR şablonu, `area: özet` + `Verified:` commit biçimi; her `git push` onay ister, `gh pr merge` yasak | `project/.github/`, `project/.claude/settings.json` |
| Git: LF, Unity Smart Merge (`.gitattributes` + `new-game.ps1` sürücüyü kaydeder), eksik `.meta`'yı reddeden pre-commit hook, isteğe bağlı LFS satırları | `project/.gitattributes`, `.githooks/` |
| İzinler, Unity YAML koruma hook'u, C# LSP ve context7 eklentileri | `project/.claude/settings.json`, `hooks/` |

## Global Claude katmanı

Skill'ler ve agent'lar şablonda değil, globalde durur; böylece şablondan açılmamış oyunlarda da çalışırlar:

| Parça | Nerede |
|---|---|
| 20 skill: mimari, performans, debug, review, test, doğrulama, refactor-pass, editor CLI, platformlar, Feel (+ tarifler), game-feel, player-clarity, level-beat-review, launch-review (Steam, Google Play, App Store, itch.io), grill-me, Unity'nin resmi 4 skill'i | `~/.claude/skills/` |
| 7 salt okunur agent: unity-reviewer, bug-hunter, perf-auditor, clarity-reviewer, design-critic, launch-auditor ve Sonnet'te çalışan `Explore` | `~/.claude/agents/` |
| Görev yönlendirici: her yeni istemi S / M / L diye boyutlar (S doğrudan, M tek oturum + gerekirse bir reviewer, L önce öneri), `orchestrate` skill'i L şekillerini ve agent brief'ini tutar; workflow sadece kullanıcı isteyince | `~/.claude/hooks/enhance-prompt.ps1`, `~/.claude/skills/orchestrate/` |
| `lean-code` kuralı ve sadece Unity projelerinde yüklenen `unity-games` kuralı | `~/.claude/rules/` |
| Unity YAML koruma hook'u ve git izinleri | `~/.claude/hooks/guard-unity-yaml.ps1`, `~/.claude/settings.json` |

Blender skill'leri de orada. Global skill'ler `__GAME__` yerine `<Game>` yazar (`Assets/<Game>/Core` gibi);
`unity-games` kuralı bunun bu şablonun düzeni olduğunu, bir projenin farklarını kendi `CLAUDE.md`'sinde yazdığını
anlatır. `project/.claude/` içindeki izinler ve YAML hook'u globaldekilerle aynı değil: her `git push`'un onay
istemesi, `git branch -d/-f/-M` onayları (globalde sadece `-D` var) ve `gh pr merge` yasağı sadece şablondan açılan
oyunlarda var; global
YAML hook'u Bash/PowerShell yazmalarını da yakalar, projedeki sadece Edit/Write'ı.

Global kopyalar hiçbir repoda değil: yeni bir bilgisayara `~/.claude/skills`, `agents`, `rules` ve `hooks`
(`guard-unity-yaml.ps1`, `enhance-prompt.ps1`, `self-check.ps1`, `adhd-mode.ps1`) elle kopyalanır, ardından
`~/.claude/settings.json` içindeki `hooks` bloğu da taşınır (içindeki `C:\Users\<ad>` yollarını düzelt). Unity
skill'lerinin ve agent'larının şablondaki son, yer tutuculu hâlleri `9915c17` commit'indedir; yönlendirici,
`orchestrate` ve `Explore` sonradan eklendi ve orada yok.

## Bilerek alınmayanlar

- Mixtrol'ün karaktere ve level kit'e özel Editor builder'ları ve ağ gecikmesi için yazılmış `FramePacing`: o oyuna
  bağlılar. Desen örneği olarak `packs/toon-art/examples/` içinde bir import postprocessor ve Blender script'leri var.
- PixelVolley'nin `LevelCatalog` / `LevelInspectorWindow` ve Magic Sort'un `AssetGen` / `PreviewCapture` araçları:
  oyuna özeller. Magic Sort'taki ekran yakalama fikri genelleştirilip `play-capture` oldu.
- PrimeTween, Localization ve IAP: manifest bilerek küçük; oyun ihtiyaç duyunca eklenir
  (`packs/reference-docs/packages.md` kurulum satırlarını ve alınmayanları listeler). FishNet `coop-multiplayer`
  paketinin README'sinde, 2D paketleri `mobile-2d` paketiyle gelir.
- `learneter` ve `portfolio-site`: Unity projesi değiller.

## Eksikler

- Android build için Unity Hub'dan **Android Build Support** modülünü ekle (şu an Windows, WebGL ve iOS kurulu).
- iOS build bir Xcode projesi üretir; imzalama ve derleme Mac'te yapılır.

## Template'i güncellemek

Bir oyunda işe yarayan bir skill, agent ya da genel kural çıkarsa, onu projeden bağımsız hale getirip `~/.claude/`
altına koy (bütün oyunlar hemen alır). Şablona özgü kod, ayar ve proje kuralları `project/` altına gider; mevcut
oyunlar etkilenmez, sadece bundan sonra açılanlar alır.
