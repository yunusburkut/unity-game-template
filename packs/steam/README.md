# steam

Steam'de satılacak PC oyunları için. Paket eklenince:

1. `Packages/manifest.json` içine **Steamworks.NET** (`2025.165.0`, Steamworks SDK 1.65, MIT) git URL'siyle eklenir.
2. `Game/Steam/SteamBootstrap.cs` (kendi asmdef'i `__GAME__.Steam`): ilk sahneden önce `SteamAPI.Init`, her karede
   `RunCallbacks`, çıkışta `Shutdown`. Sahneye bir şey koymak gerekmez. Editor'de Steam kapalıysa oyun çalışmaya
   devam eder; Steam özellikleri `SteamBootstrap.Initialized` ile kontrol edilir.
3. `ProjectSetup` sonrası `SteamSetup` çalışır: Android, iOS ve WebGL için `DISABLESTEAMWORKS` define'ı (telefon ve
   web build'leri Steam kodunu hiç derlemez) ve ilk çalışmada PC için **IL2CPP** (aşağıda, Steam'e yükleme).
4. `new-game.ps1`, `__GAME__.Game.asmdef` içindeki `references`'a `"__GAME__.Steam"`'i ekler.

Gerçek App ID girildikten sonra, Steam dışından açılan (exe'ye çift tıklanan) bir Windows build'i Steam'i başlatır,
oyunu Steam üzerinden yeniden açar ve kendisi kapanır. App ID hâlâ `480` iken bu atlanır (yoksa Steam oyunun yerine
Spacewar'ı açardı): build normal açılır; Steam özellikleri ancak exe'nin yanına `steam_appid.txt` koyarsan (Steam açıkken) çalışır. itch.io gibi başka bir mağazaya gidecek Windows build'i **GameKit > Build > Windows (no Steam, itch.io)**
ile alınır: `DISABLESTEAMWORKS` yalnızca o build için eklenir, sonra Player Settings eski haline döner (çıktı yine
`Builds/Windows`).

## Elle yapılacaklar

1. Steamworks'ten App ID al. `SteamBootstrap.AppId` içindeki `480`'i (Valve'in Spacewar test uygulaması) değiştir.
2. Proje kökündeki `steam_appid.txt` dosyasına aynı sayıyı yaz (Steamworks.NET ilk açılışta 480 ile oluşturur) ve
   commit'le: Editor'de Steam'i bu numarayla başlatır, build'e girmez. Aşağıdaki CI job'u App ID'yi de bu dosyadan
   okur. İki sayı farklıysa Windows build'i (`SteamAppIdCheck`, `Editor/SteamSetup.cs`) hata verip durur; dosya
   yoksa sadece uyarır.
3. Paket oyuna başka yoldan geldiyse (sync, elle kopya) `Assets/__GAME__/Game/__GAME__.Game.asmdef` içindeki
   `references`'a `"__GAME__.Steam"` ekle; `new-game.ps1` ile açılan oyunda zaten vardır. Oyun kodu Steamworks
   API'sini doğrudan çağıracaksa `"com.rlabrecque.steamworks.net"`'i her durumda sen ekle; bu çağrıları
   `#if !DISABLESTEAMWORKS` içinde tut.
4. Achievement, istatistik, overlay, cloud save: Steamworks.NET'in `SteamUserStats`, `SteamFriends`,
   `SteamRemoteStorage` API'leri; her çağrıdan önce `SteamBootstrap.Initialized`.

### Achievement ve istatistik

Steam çağrıları `Game/Steam/` içinde (asmdef `__GAME__.Steam`) küçük bir statik sınıfta durur, ör.
`SteamStats.Unlock("ACH_FIRST_WIN")`; oyun kodu Steamworks API'sine değil ona seslenir. Bu asmdef her platformda
derlenir, Steamworks kodu derlenmez: metot gövdesini `#if !DISABLESTEAMWORKS` içine al, böylece telefonda ve WebGL'de
çağrı boş metottur ve çağıran yerde `#if` gerekmez. Gövde önce `if (!SteamBootstrap.Initialized) return;` der
(Editor'de Steam kapalıysa, oyun Steam'siz açıldıysa sessizce atlar). Sıra:

- Achievement: `SteamUserStats.SetAchievement("ACH_...")`, ardından `SteamUserStats.StoreStats()`. `SetAchievement`
  yalnız yerelde işaretler; Steam'e gönderen ve overlay bildirimini gösteren `StoreStats`'tır.
- İstatistik: `SteamUserStats.SetStat("STAT_...", değer)` (int ya da float, Steamworks'teki tanımla aynı tip), sonra
  `StoreStats()`; her karede değil, anlamlı anlarda (bölüm sonu, menüye dönüş, çıkış): Steam bu çağrıyı sınırlar.
- Okuma için ayrıca istek gerekmez: Steamworks SDK 1.61'den beri (bu paketteki 1.65 dahil) kullanıcının
  istatistikleri `SteamAPI.InitEx` ile hazır gelir, `RequestCurrentStats` yoktur.
- Adlar (`ACH_...`, `STAT_...`) Steamworks > **Stats & Achievements** sayfasındakiyle birebir aynı olmalı ve o sayfa
  **Publish** edilmiş olmalı; yoksa çağrı `false` döner. Test için `SteamUserStats.ResetAllStats(true)`, yalnız
  geliştirme build'inde.

## Build'i Steam'e yüklemek (isteğe bağlı CI)

`ci-github` paketiyle birlikte, Windows build'ini tag'lerde Steam'e gönderen bir job
([game-ci/steam-deploy](https://github.com/game-ci/steam-deploy) v3, MIT). Job, `ci-github` paketinin `ci.yml`'sinin
sonunda yorum satırı olarak durur (tek kaynak orası; `test-all` yorumdaki `steam:` bloğunun da
indirdiği artifact'ı build matrix'inin yüklediğini ve yollarının `BuildMenu`'nün `Builds/Windows` çıktısıyla eşleştiğini
denetler, ama YAML'ını çalıştırmaz); açmak için `steam:` bloğunun başındaki `# ` işaretlerini kaldır. Açınca artifact adını
(`Build-StandaloneWindows64`, matrix'in `targetPlatform`'u) ve `artifact/Builds/Windows` yolunu (`BuildMenu`'nün
Windows çıktısı) bir kez kontrol et. `steam_appid.txt` hâlâ `480` ise job, yüklemeye geçmeden bunu söyleyip durur.
Secret'lar: `STEAM_USERNAME`, `STEAM_CONFIG_VDF` (steamcmd ile bir kez giriş yapıp `config/config.vdf`'in base64'ü);
2FA'lı ayrı bir build hesabı kullan. Job build'i `beta` branch'inde canlıya alır: ilk tag'den önce Steamworks'te
**App Admin > SteamPipe > Builds** sayfasında `beta` branch'ini aç; build'i default branch'e almak o sayfada elle
yapılır. Job tüm build matrix'ini bekler: Android ya da WebGL kırılırsa Windows build'i hazır olsa da Steam job'u
atlanır; o bacağı düzeltip **Re-run failed jobs** de.

Steam'e giden build, `ci.yml`'nin Windows runner'da aldığı Windows build'idir ve Player Settings'teki scripting
backend'ini kullanır. Steam'e **IL2CPP** gider (Mono'ya göre daha hızlı, DLL'leri kolayca decompile edilmez):
`SteamSetup` ilk çalışmada **Player Settings > Windows > Scripting Backend**'i IL2CPP yapar, sonraki çalışmalar
oyunun seçimine dokunmaz. Yerel Windows build'i için Unity Hub'da **Windows Build Support (IL2CPP)** modülü ve
Visual Studio'nun **Desktop development with C++** iş yükü gerekir. IL2CPP build'inin yanına çıkan
`*_BackUpThisFolder_ButDontShipItWithYourPlayer` ve `*_BurstDebugInformation_DoNotShip` klasörleri oyuncuya gitmez;
job onları yüklemeden önce siler. Depot ID'si `appId + 1` değilse steam-deploy belgesindeki `firstDepotIdOverride`.

## CLAUDE.md'ye eklenecek satır

```
- Steam (PC only): Steamworks.NET, started by `Game/Steam/SteamBootstrap`. Guard every Steam call with
  `SteamBootstrap.Initialized` and keep Steam code behind `#if !DISABLESTEAMWORKS`; phones and WebGL never compile it.
  `__GAME__.Game.asmdef` already references `"__GAME__.Steam"`; code that calls the Steamworks API directly first adds
  `"com.rlabrecque.steamworks.net"` there. A Windows build for itch.io is GameKit > Build > Windows (no Steam, itch.io).
- Steam achievements and stats: one static class in `Game/Steam` (e.g. `SteamStats.Unlock("ACH_X")`) that game code
  calls; each method body sits in `#if !DISABLESTEAMWORKS` (a no-op on phones and WebGL) and starts with
  `if (!SteamBootstrap.Initialized) return;`. `SetAchievement` / `SetStat` then `StoreStats()` (only that uploads and
  shows the popup), at meaningful moments, not every frame. No `RequestCurrentStats` (gone since SDK 1.61). Names
  match the published Steamworks Stats & Achievements page.
- Steam routing: where Steamworks API code goes (achievements, Steam Cloud saves, overlay, rich presence) is
  `gamekit:unity-architecture` (a Game-side adapter in `Game/Steam`; Core never references Steamworks); store page,
  depots, builds and uploads are `gamekit:launch-review`.
```
