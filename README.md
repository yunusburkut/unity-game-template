# unity-game-template

Her yeni oyun reposunun başlangıç noktası: Unity 6000.6 + URP iskeleti, PC ve mobil (Android, iOS) ve WebGL
hedefleri, ve hazır bir Claude Code katmanı. mixtrolrepo, PixelVolley ve Magic-Sort-Clone'da işe yarayan her şey
projeden bağımsız hale getirilip buraya taşındı.

## Yeni oyun başlat

En kolayı, herhangi bir Claude Code oturumunda: `/gamekit:new-game SkyHopper <oyunun ilk fikri>`. Paketleri ve
GitHub reposunu sorar, oyunu kurar, fikri `DESIGN.md`ye yazar, Unity'yi açar ve oyun klasöründe fikri şekillendiren
yeni bir oturum başlatır. Elle kurmak için:

```powershell
.\new-game.ps1 -Name SkyHopper
```

1. `C:\GitHub\SkyHopper` oluşur, `__GAME__` her yerde `SkyHopper` olur.
2. `-Packs` ile seçilen paketler eklenir.
3. Feel, Assets\Feel'i olan ilk yerel repodan kopyalanır ve oyunun repo'suna commit edilir. Böylece klon ve CI
   Asset Store'suz derlenir. Feel ücretli olduğu için oyun repo'su **private kalmalı**.
4. Unity batch modda `ProjectSetup`'ı çalıştırır (ilk import birkaç dakika).
5. `main` dalında ilk commit atılır; Unity Smart Merge sürücüsü ve `.meta` pre-commit hook'u açılır.

Sonra: Unity Hub > Add > Add project from disk, ardından o klasörde Claude Code'u aç. İlk iş olarak
`/gamekit:new-game şekillendir` yaz: Claude tür varsayılanlarıyla soru sorar, `CLAUDE.md` ve `DESIGN.md` içindeki TODO
satırlarını cevaplarınla doldurur, kararları `DESIGN.md`ye yazar ve commit atar. Claude ile nasıl çalışılır: oyundaki `REHBER.md`.

Parametreler: `-Path D:\Games`, `-Company ad`, `-Packs a,b`, `-FeelFrom C:\GitHub\PixelVolley`, `-Unity <Unity.exe>`
(varsayılan: `ProjectVersion.txt`'deki sürümün Hub kurulumu), `-SetupTimeoutMinutes 30` (ProjectSetup bu sürede
bitmezse Unity kapatılır), `-NoSetup`, `-NoGit`, `-LocalGameKit` (GameKit'i tag yerine bu checkout'tan `file:` ile
alır), `-GitHub` (ilk commit'ten sonra `gh` ile `<Name>` adında private repo açar ve `main`'i push eder;
`gh auth login` gerekir). Hepsinin açıklaması: `Get-Help .\new-game.ps1 -Detailed`.

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
| `ci-github` | GameCI ile GitHub Actions: main'e her push'ta ve her PR'da testler (sadece Markdown değişince değil); `v*` tag'inde ya da elle çalıştırınca Windows (Windows runner) / Android / WebGL build'i, `v*` tag'inde itch.io'ya butler push; `GAMEKIT_TOKEN` secret'ı gerekir | Bulutta test ve build, itch.io'ya otomatik yükleme |

Bir paketin `packages.json` dosyası varsa, içindeki UPM paketleri ve scoped registry'ler yeni oyunun
`Packages/manifest.json` dosyasına eklenir. `[ProjectSetupStep]` ile işaretlenmiş Editor metotları `ProjectSetup`'tan
sonra çalışır.

Her paketin README'si ne eklediğini ve kurulumdan sonra elle yapılacakları anlatır; README ve `examples/` oyuna
kopyalanmaz. İstisna: README'nin `## CLAUDE.md'ye eklenecek satır` başlığı altındaki kod bloğu (oyunun `## Packs`
bölümüne) ve ` ```markdown ` ile açılıp `## ` ile başlayan her blok (ör. coop-multiplayer'ın `## Networking` bölümü)
oyunun `CLAUDE.md`'sine aktarılır; bu başlıkları ve blok işaretlerini değiştirme. `packs/reference-docs/` sadece okumak için: frame budget, pazar, Steam, ses, renk teorisi notları,
oyuna göre eklenecek paketler (`packages.md`, artık `plugin/skills/unity-package-management/references/select-packages.md`'yi gösteriyor) ve 2026 mağaza kuralları (`shipping-2026.md`).

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
| Tek dal akışı: her iş `main`'de, `area: özet` + `Verified:` commit biçimi, M/L işte puanlı review (her reviewer ≥9/10); her `git push` ve yayın aracı (`butler push`, `steamcmd`, `gh release`) onay ister, force push yasak | `project/CLAUDE.md`, `project/.claude/settings.json` |
| Git: LF, Unity Smart Merge (`.gitattributes` + `new-game.ps1` sürücüyü kaydeder), eksik `.meta`'yı reddeden pre-commit hook, isteğe bağlı LFS satırları | `project/.gitattributes`, `.githooks/` |
| İzinler; C# LSP, context7 ve gamekit eklentileri | `project/.claude/settings.json` |

### GameKit paketi (`com.yunusburkut.gamekit`)

| İçerik | Dosya |
|---|---|
| **GameKit > Set Up Project:** URP Mobile ve PC kalite seviyeleri, sadece Input System, Linear, IL2CPP ARM64, Android target API 36 ve "game" kategorisi, Nice Vibrations define'ı, Main sahnesi. Oyun klasörünü `Assets/<Game>/Core/<Game>.Core.asmdef`'ten bulur. Tekrar çalıştırmak şirket/ürün adını, bundle id'yi, URP asset'lerini ve kalite seviyelerini korur; pack'lerin `[ProjectSetupStep]` metotlarını da çalıştırır | `Editor/ProjectSetup.cs` |
| **GameKit > Build:** Windows / Android APK / Google Play AAB / iOS / WebGL, Development Build, itch.io için Brotli WebGL (ayarlar ProjectSetup ilk kurulumda yazılır; dev WebGL sıkıştırmasız) | `Editor/BuildMenu.cs`, `Editor/ProjectSetup.cs` |
| Claude için derleme, konsol, test, build logları (`Logs/agent/`); odak gerektirmeyen `refresh`, `compile ios/android/webgl`, `play-capture` | `Editor/AgentBridge.cs` |
| Çentik için `SafeAreaFitter`; Development Build'de kare süresi CSV'si (`FrameLog`, F3) | `Runtime/` |

### gamekit plugin'i

| İçerik | Nerede |
|---|---|
| `pipeline` skill'i: istem → PLAN.md'de spec kartı → plan → her birimde derleme kapısı → doğrulama → 10 üzerinden puanlı review (her reviewer ≥9) → teslim | `plugin/skills/pipeline/` |
| Diğer skill'ler (tam liste `plugin/skills/`, `test-all.ps1` her birinin frontmatter'ını kontrol eder): new-game (herhangi bir oturumdan yeni oyun), mimari, performans, debug, review, test, doğrulama, refactor-pass, editor CLI, platformlar, Feel (+ tarifler), game-feel, player-clarity, level-beat-review, launch-review, sync-template, visual-explainer, prototype (ayrı asmdef'te deneme, PROCEED / PIVOT / KILL kararı), genre-defaults (türe göre başlangıç ayarları) ve Unity'nin resmi Unity Agent Plugin'inden uyarlanan `unity-cli`, `ui-ugui`, `urp-postprocessing`, `unity-package-management` (her birinde Unity Companion License'lı `LICENSE.md`; template'e göre yerel düzeltmeler taşırlar, upstream'den güncellerken klasörü toptan değiştirme, farkı birleştir) | `plugin/skills/` |
| "Visual Clarity" output style'ı: Türkçe, görsel öncelikli, ASD-STE100 sade dil, QUICK / STANDARD / VISUAL EXPLAINER seviyeleri, dürüst doğrulama raporu; seçilince Concise'ın yerini alır | `plugin/output-styles/` |
| Agent'lar (tam liste `plugin/agents/`): scout (bağlam), builder (tek birim: yaz, kapı, commit), unity-reviewer, bug-hunter, perf-auditor, clarity-reviewer, design-critic, launch-auditor | `plugin/agents/` |
| `gk-bridge` komutu: AgentBridge isteğini gönderir, bekler, `PASS`/`FAIL`/`UNKNOWN` (exit 0/1/2) döner | `plugin/bin/` |
| `/gamekit:feature [istek]` workflow'u: kartı (yoksa önce yazar) gözetimsiz yapar, yalnız istenince | `plugin/workflows/` |
| Hook'lar: görev yönlendirici (S/M/L), Unity YAML koruma, Edit/Write ile düzenlenen `.json`/`.asmdef`/`.asmref` hâlâ geçerli JSON mu kontrolü (shell komutuyla yazılan dosyaya bakmaz), `.cs`/`.asmdef`/`.asmref` düzenlemesinden ve `git rm`/`git mv`'den sonra `refresh`, derleme hatası ya da derlenmemiş script varken turun bitmesini bir kez engelleyen Stop self-check, Blender MCP için `ensure-blender`: canlı bir çağrıdan önce kapalı Blender'ı `--online-mode` ile açıp add-on sunucusunu bekler (en çok 100 sn), MCP add-on'u o Blender sürümüne kurulu değilse çağrıyı engeller, eklenti `stdin` yamasını kaybettiyse `*_for_cli` çağrısını düzeltmesiyle birlikte engeller (doküman araçlarına dokunmaz), okuma-yalnız agent'larda (scout, bug-hunter, unity-reviewer, perf-auditor, clarity-reviewer, design-critic) durum değiştiren `git` komutunu ve `%TEMP%` dışına yazan `>`/`tee` yönlendirmesini engelleyen `guard-readonly-agent` (agent frontmatter'ı hook taşıyamadığı için söz yalnız prompt'ta kalmasın diye). Plugin kullanıcı ayarında açık olduğu için bu hook'lar her oturumda çalışır | `plugin/hooks/` |

Oyunda kullanım rehberi: [`project/REHBER.md`](project/REHBER.md) (yeni oyunlara kopyalanır; eski oyunlara `/gamekit:sync-template` getirir).

Plugin'de `version` bilerek yok: her commit yeni sürüm sayılır, `autoUpdate` ile oyunlara kendiliğinden gelir.
Plugin'ler kural dosyası taşıyamaz; `unity-games` kuralı `~/.claude/rules/` altında kalır.

## Global Claude katmanı (`~/.claude`, repoda değil)

Oyuna özgü olmayan kişisel parçalar: görev yönlendirici (`hooks/enhance-prompt.ps1` + `orchestrate` skill'i; Unity
projesinde susar, yerine gamekit'in yönlendiricisi çalışır),
`grill-me`, Sonnet'te çalışan `Explore` agent'ı, ADHD modu, `lean-code` ve `unity-games` kuralları, Blender
skill'leri. Kullanıcı ayarında gamekit plugin'i açıktır, böylece şablondan açılmamış oyunlar da onu alır.

Bu katman hiçbir repoda yok ve hiçbir script onu kurmaz; yeni bilgisayarda yedekten geri gelmeli. Eksikse hata
vermez, sessizce kaybolur: `/grill-me`, Unity dışı işlerin S/M/L yönlendiricisi, ADHD modu, Visual Clarity output
style'ı ve Blender → Unity export sözleşmesi (`unity-export`) gider. Taşınacaklar:

| Parça | Yer (`~/.claude/` altında) |
|---|---|
| Kullanıcı ayarları: iki hook'un kaydı (`hooks`: SessionStart → `adhd-mode.ps1`, UserPromptSubmit → `enhance-prompt.ps1`), `enabledPlugins` (gamekit, i-have-adhd, context7, csharp-lsp), `extraKnownMarketplaces`, `outputStyle: "gamekit:Visual Clarity"`. Dosya yoksa hook script'leri kopyalansa da hiç çalışmaz; yeni makinede zaten bir `settings.json` varsa bu anahtarları içine birleştir | `settings.json` |
| Kişisel kurallar ve yanıt biçimi | `CLAUDE.md`, `rules/lean-code.md`, `rules/unity-games.md` |
| Görev yönlendirici ve ADHD modu (ADHD modu `i-have-adhd` plugin'inin skill'ini okur; plugin yoksa yalnız temel kurallarla çalışır) | `hooks/enhance-prompt.ps1`, `hooks/adhd-mode.ps1` |
| Skill'ler | `skills/grill-me`, `skills/orchestrate`, `skills/blender-director`, `skills/blender-image-to-3d`, `skills/unity-export`, `skills/references`, `skills/synced` |
| Yedek Blender skill'leri (listeye girmez, director dosya olarak okur) | `spares/blender-skills/` |
| Sonnet'te çalışan `Explore` agent'ı | `agents/Explore.md` |

Yeni bir bilgisayarda: yukarıdaki parçaları yedekten `~/.claude/` altına kopyala, `gh auth login` (git push için
Git for Windows'un Credential Manager'ı kalsın, `gh auth setup-git` çalıştırma: aşağıdaki token'la çakışır), sonra

```powershell
claude plugin marketplace add yunusburkut/unity-game-template
claude plugin install gamekit@unity-game-template
claude plugin marketplace add ayghri/i-have-adhd
claude plugin install i-have-adhd@i-have-adhd
```

Plugin güncellemeleri: arka plandaki otomatik güncelleme (`autoUpdate`) git credential helper'ını kullanmaz; private
repo için ortamda token ister. `GITHUB_TOKEN` kullanıcı değişkenini, yalnız `unity-game-template` reposunda
**Contents: Read** izni olan fine-grained bir token yap ve Claude'u yeniden başlat. Ayrıca kullanıcı
`settings.json`'unda `extraKnownMarketplaces.unity-game-template` girdisine `"autoUpdate": true` ekle (şablondan açılan
oyunların `.claude/settings.json`'unda zaten var; şablondan açılmamış oyunlar bu kullanıcı girdisini kullanır). Token
yoksa güncelleme elle yapılır: `claude plugin update gamekit@unity-game-template`.

Token çakışması: `gh`, `GH_TOKEN`/`GITHUB_TOKEN` ortamda varken `gh auth login` girişini değil bu token'ı kullanır ve
`gh auth status` yine "logged in" der. Salt-okur token'la `gh repo create`, `gh secret set` 403 verir; git credential
helper'ı `gh` ise her push da düşer. Bu yüzden git push Credential Manager'dan gider, yazan `gh` komutları token'sız
çalışır: bash'te `env -u GITHUB_TOKEN -u GH_TOKEN gh repo create ...`, PowerShell'de aynı komut satırında önce
`$env:GITHUB_TOKEN = $null; $env:GH_TOKEN = $null`. Token'a yazma izni verme: otomatik güncelleme yalnız okur.

Blender 5.2:

1. `C:\Program Files\Blender Foundation\Blender 5.2` klasörünü kullanıcı `PATH`'ine ekle (kökteki `CLAUDE.md`,
   `test-all.ps1` ve skill'ler düz `blender` çağırır) ve `BLENDER_PATH` kullanıcı değişkenini
   `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` yap (Blender MCP'nin `*_for_cli` araçları ve
   `ensure-blender` hook'u Blender'ı bununla bulur); Claude'u yeniden başlat.
2. Canlı MCP araçları için Blender'da MCP add-on'unu kur ve aç (port 9876):
   `blender --command extension repo-add --name "Blender Lab" --url https://lab.blender.org/ lab`, sonra
   `blender --online-mode --command extension sync` ve `... extension install --enable lab.mcp`. Preferences →
   System → **Allow Online Access** açık olmalı; kapalıyken add-on sunucuyu başlatmaz (yalnızca localhost dinler,
   internete çıkmaz). Add-on kurulumu ve Allow Online Access her Blender major.minor sürümü (5.2, 5.3...) için
   ayrı ayrı tekrarlanır. Add-on'un Auto Start ayarı (varsayılan açık) sunucuyu Blender açıldıktan birkaç saniye
   sonra kendiliğinden başlatır; `ensure-blender` hook'u kapalı Blender'ı `--online-mode` ile açtığı için kayıtlı
   tercih ne olursa olsun online erişim açık olur, ama Auto Start kapalıysa sunucu yine başlamaz.
3. `~/.claude/skills` içinde Blender skill'lerinden yalnızca `blender-director`, `blender-image-to-3d` ve
   `unity-export` durur (yanlarındaki `grill-me`, `orchestrate`, `references`, `synced` da bilerek orada). Diğer ~90
   Blender skill'i `~/.claude/spares/blender-skills/` altındadır: skill listesine girmezler, director onları dosya
   olarak okur. Skill olarak dursalar, listeleme bütçesi çok erken taşar ve gamekit skill'lerinin açıklaması düşer.
   Taşınmaları taşmayı azaltır ama bitirmez: liste bütçesi (bağlam penceresinin ~%1'i) diğer plugin'lerle de
   paylaşılır; aşılınca bazı gamekit skill'leri açıklamasız listelenir ve kendiliğinden tetiklenmez (adıyla
   çağrılınca yine çalışır). `plugin\test-hooks.ps1` gamekit ve `~/.claude/skills` açıklamalarının toplamını bütçeye
   karşı ölçer; plugin'lerin payını sayamaz.
4. Headless Blender her zaman `blender --background --factory-startup --python-exit-code 1 --python <script>` ile
   çalışır (kökteki `CLAUDE.md` ve `test-all.ps1` ile aynı): `--python-exit-code 1` olmadan bir Python hatası exit 0
   döner, `--factory-startup` olmadan kullanıcının startup dosyası ve add-on'ları sonucu değiştirir.
5. Blender MCP eklentisine yerel yama (upstream'de yok): eklentinin
   `%LOCALAPPDATA%\Claude-Data\<profil>\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py`
   dosyasında `run_blender_cli` içindeki `subprocess.run(...)` çağrısına `stdin=subprocess.DEVNULL,` argümanını ekle
   ve Claude'u yeniden başlat. Yoksa arka plandaki Blender sunucunun stdio borusunu devralır ve her `*_for_cli` çağrısı
   "Request timed out" ile biter. Eklenti her güncellendiğinde yama silinir, yeniden ekle: `ensure-blender` hook'u
   yamasız bir `*_for_cli` çağrısını engelleyip bunu hatırlatır, `.\test-all.ps1` de yamanın yerinde olup olmadığını
   kontrol eder.

## Bilerek alınmayanlar

- Mixtrol'ün karaktere ve level kit'e özel Editor builder'ları ve ağ gecikmesi için yazılmış `FramePacing`: o oyuna
  bağlılar. Desen örneği olarak `packs/toon-art/examples/` içinde bir import postprocessor ve Blender script'leri var.
- PixelVolley'nin `LevelCatalog` / `LevelInspectorWindow` ve Magic Sort'un `AssetGen` / `PreviewCapture` araçları:
  oyuna özeller. Magic Sort'taki ekran yakalama fikri genelleştirilip `play-capture` oldu.
- PrimeTween, Localization ve IAP: manifest bilerek küçük; oyun ihtiyaç duyunca eklenir
  (`plugin/skills/unity-package-management/references/select-packages.md` kurulum satırlarını ve alınmayanları listeler). FishNet `coop-multiplayer`
  paketinin README'sinde, 2D paketleri `mobile-2d` paketiyle gelir.
- `learneter` ve `portfolio-site`: Unity projesi değiller.

## Eksikler

- Yeni bir bilgisayarda Unity 6000.6'ya Unity Hub'dan **Android Build Support** (SDK, NDK, OpenJDK ile), **iOS Build
  Support**, **Web Build Support** ve **Windows Build Support** modüllerini ekle. Eksik bir modülü `gk-bridge compile`
  ve GameKit > Build "module is not installed" diye söyler.
- iOS build bir Xcode projesi üretir; imzalama ve derleme Mac'te yapılır.

## Template'i güncellemek

| Değişen | Nereye | Oyunlara nasıl gider |
|---|---|---|
| Skill, agent, hook | `plugin/` | `main`'e girince kendiliğinden (`autoUpdate`; hemen istersen `claude plugin update gamekit@unity-game-template`) |
| Ortak Unity kodu | `packages/com.yunusburkut.gamekit/` | `package.json` sürümünü artır, `gamekit-vX.Y.Z` tag'i at ve push et; oyunun `Packages/manifest.json` içindeki `#gamekit-v...` kısmını yeni tag yap |
| İskelet, CLAUDE.md, ayarlar | `project/`, `packs/` | Yeni oyunlar hemen alır. Mevcut oyunda Claude'a `/gamekit:sync-template` de: oyunun son eşitlendiği template commit'inden beri değişenleri listeler, seçtiklerini patch olarak uygular (oyunun değiştirdiği yerler `.rej` olur, elle birleşir), GameKit tag'ini template'in `origin/main` manifest'inin gösterdiği yayınlanmış tag'e çeker (yeni GameKit sürümü oyunlara ancak `project/Packages/manifest.json` o tag'e alınınca gelir) ve `template: sync to unity-game-template@<sha>` commit'i atar |

Her değişiklikten sonra tek giriş `.\test-all.ps1`: Unity gerektirmeyen her kontrol (sözdizimi ve frontmatter,
Blender kuruluysa headless Python + FBX ve MCP yaması, sync-template hattı, global katmanın varlığı, pack birleştirme
denemesi, hook testleri, `claude plugin validate`). Tam liste ve süre tek yerde, betiğin yardım bloğunda:
`Get-Help .\test-all.ps1`. `-Full` sona `test-template.ps1`'i ekler.

`project/`, `packs/`, `packages/` veya `new-game.ps1` değişince `.\test-template.ps1` çalıştır (Unity'yi açar, birkaç dakika):
`%TEMP%`'te gerçek bir oyun açar, 0 derleme hatası, Main sahnesi, sync işareti ve GameKit kaynağını kontrol eder, sonra
siler. `-Packs mobile-2d` değişen paketi, `-Tests` oyunun EditMode ve PlayMode testlerini de çalıştırır. Bu repoda
Claude'un uyduğu kurallar kökteki `CLAUDE.md`'de.

GameKit'i tag atmadan denemek için: `.\new-game.ps1 -Name Deneme -LocalGameKit` (oyun paketi bu checkout'tan
`file:` ile alır). Mevcut bir oyunda aynısı: manifest'teki GameKit satırını
`"file:C:/GitHub/unity-game-template/packages/com.yunusburkut.gamekit"` yap, deneme bitince tag'e geri al.

Eski oyunlar (bu düzenden önce açılanlar) kendi `AgentBridge` / `BuildMenu` kopyalarını taşır. Geçiş için oyunda
`/gamekit:sync-template GameKit'e geçir` yaz: kopyaları siler, sahnenin GUID ile kullandığı bileşeni (`SafeAreaFitter` gibi;
taşınırsa "Missing Script" olur) bırakıp söyler. Plugin'i ise kullanıcı ayarından zaten alırlar.

## Teşekkür

Kontrol listelerinin bir kısmı (prototip kararı, denge, erişilebilirlik, HUD, yayın ve uzun süre testleri gibi) ve
`genre-defaults` tür sayfaları, Donchitos'un [Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
reposundan uyarlandı. MIT lisansı, metni aşağıda:

```text
MIT License

Copyright (c) 2026 Donchitos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
