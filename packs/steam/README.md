# steam

Steam'de satılacak PC oyunları için. Paket eklenince:

1. `Packages/manifest.json` içine **Steamworks.NET** (`2025.165.0`, Steamworks SDK 1.65, MIT) git URL'siyle eklenir.
2. `Game/Steam/SteamBootstrap.cs` (kendi asmdef'i `__GAME__.Steam`): ilk sahneden önce `SteamAPI.Init`, her karede
   `RunCallbacks`, çıkışta `Shutdown`. Sahneye bir şey koymak gerekmez. Editor'de Steam kapalıysa oyun çalışmaya
   devam eder; Steam özellikleri `SteamBootstrap.Initialized` ile kontrol edilir.
3. `ProjectSetup` sonrası `SteamSetup` çalışır: Android, iOS ve WebGL için `DISABLESTEAMWORKS` define'ı. Telefon ve
   web build'leri Steam kodunu hiç derlemez.

Gerçek App ID girildikten sonra, Steam dışından açılan (exe'ye çift tıklanan) bir Windows build'i Steam'i başlatır,
oyunu Steam üzerinden yeniden açar ve kendisi kapanır. App ID hâlâ `480` iken bu atlanır (yoksa Steam oyunun yerine
Spacewar'ı açardı): build normal açılır; Steam özellikleri ancak exe'nin yanına `steam_appid.txt` koyarsan (Steam açıkken) çalışır. itch.io gibi başka bir mağazaya gidecek Windows build'i için **Player Settings > Scripting
Define Symbols (Windows)** içine `DISABLESTEAMWORKS` ekle, build'i al, sonra geri sil.

## Elle yapılacaklar

1. Steamworks'ten App ID al. `SteamBootstrap.AppId` içindeki `480`'i (Valve'in Spacewar test uygulaması) değiştir.
2. Proje kökündeki `steam_appid.txt` dosyasına aynı sayıyı yaz (Steamworks.NET ilk açılışta 480 ile oluşturur) ve
   commit'le: Editor'de Steam'i bu numarayla başlatır, build'e girmez.
3. Oyun kodu Steam'i kullanacaksa `Assets/__GAME__/Game/__GAME__.Game.asmdef` içindeki `references`'a
   `"__GAME__.Steam"` (Steamworks API'sini doğrudan çağıracaksa `"com.rlabrecque.steamworks.net"` de) ekle; bu çağrıları
   `#if !DISABLESTEAMWORKS` içinde tut.
4. Achievement, istatistik, overlay, cloud save: Steamworks.NET'in `SteamUserStats`, `SteamFriends`,
   `SteamRemoteStorage` API'leri; her çağrıdan önce `SteamBootstrap.Initialized`.

## Build'i Steam'e yüklemek (isteğe bağlı CI)

`ci-github` paketiyle birlikte, Windows build'ini tag'lerde Steam'e gönderen bir job
([game-ci/steam-deploy](https://github.com/game-ci/steam-deploy) v3, MIT). `ci.yml`'deki `jobs:` altına ekle.
Secret'lar: `STEAM_USERNAME`, `STEAM_CONFIG_VDF` (steamcmd ile bir kez giriş yapıp `config/config.vdf`'in base64'ü);
2FA'lı ayrı bir build hesabı kullan.

```yaml
  steam:
    needs: build
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v8
        with:
          name: Build-StandaloneWindows64
          path: artifact
      - uses: game-ci/steam-deploy@v3
        with:
          username: ${{ secrets.STEAM_USERNAME }}
          configVdf: ${{ secrets.STEAM_CONFIG_VDF }}
          appId: 480            # TODO: App ID
          buildDescription: ${{ github.ref_name }}
          rootPath: artifact/Builds
          depot1Path: Windows   # depot ID'si appId + 1 değilse steam-deploy belgesindeki firstDepotIdOverride
          releaseBranch: beta
```

## CLAUDE.md'ye eklenecek satır

```
- Steam (PC only): Steamworks.NET, started by `Game/Steam/SteamBootstrap`. Guard every Steam call with
  `SteamBootstrap.Initialized` and keep Steam code behind `#if !DISABLESTEAMWORKS`; phones and WebGL never compile it.
  `__GAME__.Game.asmdef` references `__GAME__.Steam`.
```
