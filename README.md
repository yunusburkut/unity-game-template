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
3. Feel, Assets\Feel'i olan ilk yerel repodan kopyalanır ve oyunun repo'suna commit edilir. Böylece klon ve CI
   Asset Store'suz derlenir. Feel ücretli olduğu için oyun repo'su **private kalmalı**.
4. Unity batch modda `ProjectSetup`'ı çalıştırır (ilk import birkaç dakika).
5. `main` dalında ilk commit atılır; Unity Smart Merge sürücüsü ve `.meta` pre-commit hook'u açılır.

Sonra: Unity Hub > Add > Add project from disk, ardından o klasörde Claude Code'u aç. İlk iş olarak `CLAUDE.md` ve
`DESIGN.md` içindeki TODO satırlarını doldur (ya da `/grill-me` ile Claude'a sordur). Claude ile nasıl çalışılır: oyundaki `REHBER.md`.

Parametreler: `-Path D:\Games`, `-Company ad`, `-Packs a,b`, `-FeelFrom C:\GitHub\PixelVolley`, `-NoSetup`, `-NoGit`,
`-GitHub` (ilk commit'ten sonra `gh` ile `<Name>` adında private repo açar ve `main`'i push eder; `gh auth login` gerekir).

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

## Üç parça

| Parça | Nerede | Oyuna nasıl gider | Güncelleme |
|---|---|---|---|
| **Kopya:** iskelet, CLAUDE.md, DESIGN.md, PLAN.md, ayarlar, git dosyaları | `project/`, `packs/` | `new-game.ps1` kopyalar, oyunun olur | Oyunda `/gamekit:sync-template`, seçerek |
| **GameKit paketi:** ortak Unity kodu | `packages/com.yunusburkut.gamekit/` | `Packages/manifest.json` içinde git URL + tag | Oyunda tag'i değiştir |
| **gamekit plugin'i:** skill'ler, agent'lar, hook'lar | `plugin/` (marketplace: `.claude-plugin/`) | `enabledPlugins` | Kendiliğinden (`autoUpdate`) |

### Kopya (`project/`)

| İçerik | Nerede |
|---|---|
| Core / Game / Editor / Tests assembly ayrımı, `Easing` örneği ve testleri, Main sahnesini hatasız çalıştıran PlayMode testi, telefonda 60 fps (`AppStartup`), clamp'li `SimulationStep` | `project/Assets/__GAME__/` |
| CLAUDE.md, DESIGN.md (kararlar ve playtest kaydı dahil), CLAUDE.md'ye import edilen `PLAN.md`, README, `.editorconfig`, VS Code eklenti önerisi, `lean-code` kuralı | `project/` |
| Tek dal akışı: her iş `main`'de, `area: özet` + `Verified:` commit biçimi, M/L işte puanlı review (her reviewer ≥9/10); her `git push` onay ister | `project/CLAUDE.md`, `project/.claude/settings.json` |
| Git: LF, Unity Smart Merge (`.gitattributes` + `new-game.ps1` sürücüyü kaydeder), eksik `.meta`'yı reddeden pre-commit hook, isteğe bağlı LFS satırları | `project/.gitattributes`, `.githooks/` |
| İzinler; C# LSP, context7 ve gamekit eklentileri | `project/.claude/settings.json` |

### GameKit paketi (`com.yunusburkut.gamekit`)

| İçerik | Dosya |
|---|---|
| **GameKit > Set Up Project:** URP Mobile ve PC kalite seviyeleri, sadece Input System, Linear, IL2CPP ARM64, Android target API 36 ve "game" kategorisi, Nice Vibrations define'ı, Main sahnesi. Oyun klasörünü `Assets/<Game>/Core/<Game>.Core.asmdef`'ten bulur. Tekrar çalıştırmak şirket/ürün adını, bundle id'yi, URP asset'lerini ve kalite seviyelerini korur; pack'lerin `[ProjectSetupStep]` metotlarını da çalıştırır | `Editor/ProjectSetup.cs` |
| **GameKit > Build:** Windows / Android APK / Google Play AAB / iOS / WebGL, Development Build, itch.io için Brotli WebGL | `Editor/BuildMenu.cs` |
| Claude için derleme, konsol, test, build logları (`Logs/agent/`); odak gerektirmeyen `refresh`, `compile ios/android`, `play-capture` | `Editor/AgentBridge.cs` |
| Çentik için `SafeAreaFitter`; Development Build'de kare süresi CSV'si (`FrameLog`, F3) | `Runtime/` |

### gamekit plugin'i

| İçerik | Nerede |
|---|---|
| `pipeline` skill'i: istem → PLAN.md'de spec kartı → plan → her birimde derleme kapısı → doğrulama → 10 üzerinden puanlı review (her reviewer ≥9) → teslim | `plugin/skills/pipeline/` |
| 20 skill daha: mimari, performans, debug, review, test, doğrulama, refactor-pass, editor CLI, platformlar, Feel (+ tarifler), game-feel, player-clarity, level-beat-review, launch-review, sync-template, Unity'nin resmi 4 skill'i | `plugin/skills/` |
| 8 agent: scout (bağlam), builder (tek birim: yaz, kapı, commit), unity-reviewer, bug-hunter, perf-auditor, clarity-reviewer, design-critic, launch-auditor | `plugin/agents/` |
| `gk-bridge` komutu: AgentBridge isteğini gönderir, bekler, `PASS`/`FAIL`/`UNKNOWN` (exit 0/1/2) döner | `plugin/bin/` |
| `/gamekit:feature [istek]` workflow'u: kartı (yoksa önce yazar) gözetimsiz yapar, yalnız istenince | `plugin/workflows/` |
| Hook'lar: görev yönlendirici (S/M/L), Unity YAML koruma, `.cs`/`.asmdef`/`.asmref` düzenlemesinden ve `git rm`/`git mv`'den sonra `refresh`, derleme hatası ya da derlenmemiş script varken turun bitmesini bir kez engelleyen Stop self-check | `plugin/hooks/` |

Oyunda kullanım rehberi: [`project/REHBER.md`](project/REHBER.md) (yeni oyunlara kopyalanır; eski oyunlara `/gamekit:sync-template` getirir).

Plugin'de `version` bilerek yok: her commit yeni sürüm sayılır, `autoUpdate` ile oyunlara kendiliğinden gelir.
Plugin'ler kural dosyası taşıyamaz; `unity-games` kuralı `~/.claude/rules/` altında kalır.

## Global Claude katmanı (`~/.claude`, repoda değil)

Oyuna özgü olmayan kişisel parçalar: görev yönlendirici (`hooks/enhance-prompt.ps1` + `orchestrate` skill'i; Unity
projesinde susar, yerine gamekit'in yönlendiricisi çalışır),
`grill-me`, Sonnet'te çalışan `Explore` agent'ı, ADHD modu, `lean-code` ve `unity-games` kuralları, Blender
skill'leri. Kullanıcı ayarında gamekit plugin'i açıktır, böylece şablondan açılmamış oyunlar da onu alır.

Yeni bir bilgisayarda: `gh auth login` ve `gh auth setup-git` (repo private), sonra

```powershell
claude plugin marketplace add yunusburkut/unity-game-template
claude plugin install gamekit@unity-game-template
```

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

| Değişen | Nereye | Oyunlara nasıl gider |
|---|---|---|
| Skill, agent, hook | `plugin/` | `main`'e girince kendiliğinden (`autoUpdate`; hemen istersen `claude plugin update gamekit@unity-game-template`) |
| Ortak Unity kodu | `packages/com.yunusburkut.gamekit/` | `package.json` sürümünü artır, `gamekit-vX.Y.Z` tag'i at ve push et; oyunun `Packages/manifest.json` içindeki `#gamekit-v...` kısmını yeni tag yap |
| İskelet, CLAUDE.md, ayarlar | `project/`, `packs/` | Yeni oyunlar hemen alır. Mevcut oyunda Claude'a `/gamekit:sync-template` de: oyunun son eşitlendiği template commit'inden beri değişenleri listeler, seçtiklerini patch olarak uygular (oyunun değiştirdiği yerler `.rej` olur, elle birleşir), GameKit tag'ini son sürüme çeker ve `template: sync to unity-game-template@<sha>` commit'i atar |

`project/`, `packs/`, `packages/` veya `new-game.ps1` değişince `.\test-template.ps1` çalıştır (yaklaşık 2-5 dk):
`%TEMP%`'te gerçek bir oyun açar, 0 derleme hatası, Main sahnesi, sync işareti ve GameKit kaynağını kontrol eder, sonra
siler. `-Packs mobile-2d` değişen paketi, `-Tests` oyunun EditMode ve PlayMode testlerini de çalıştırır. Bu repoda
Claude'un uyduğu kurallar kökteki `CLAUDE.md`'de.

GameKit'i tag atmadan denemek için: `.\new-game.ps1 -Name Deneme -LocalGameKit` (oyun paketi bu checkout'tan
`file:` ile alır). Mevcut bir oyunda aynısı: manifest'teki GameKit satırını
`"file:C:/GitHub/unity-game-template/packages/com.yunusburkut.gamekit"` yap, deneme bitince tag'e geri al.

Eski oyunlar (bu düzenden önce açılanlar) kendi `AgentBridge` / `BuildMenu` kopyalarını taşır. Geçiş için oyunda
`/gamekit:sync-template GameKit'e geçir` yaz: kopyaları siler, sahnenin GUID ile kullandığı bileşeni (`SafeAreaFitter` gibi;
taşınırsa "Missing Script" olur) bırakıp söyler. Plugin'i ise kullanıcı ayarından zaten alırlar.
