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
   commit'le: Editor'de Steam'i bu numarayla başlatır, build'e girmez. Aşağıdaki CI job'u App ID'yi de bu dosyadan
   okur. İki sayı farklıysa Windows build'i (`SteamAppIdCheck`, `Editor/SteamSetup.cs`) hata verip durur; dosya
   yoksa sadece uyarır.
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

Steam'e giden build, `ci.yml`'nin Windows runner'da aldığı Windows build'idir ve Player Settings'teki scripting
backend'ini kullanır. Steam'e **IL2CPP** gönder: **Player Settings > Windows > Scripting Backend = IL2CPP**
(Mono'ya göre daha hızlı, DLL'leri kolayca decompile edilmez). IL2CPP build'inin yanına çıkan
`*_BackUpThisFolder_ButDontShipItWithYourPlayer` ve `*_BurstDebugInformation_DoNotShip` klasörleri oyuncuya gitmez;
job onları yüklemeden önce siler.

```yaml
  steam:
    needs: build
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      # App ID'nin tek kaynağı steam_appid.txt (SteamBootstrap.AppId ile aynı olmalı)
      - uses: actions/checkout@v7
        with:
          sparse-checkout: steam_appid.txt
          sparse-checkout-cone-mode: false
      - id: app
        run: echo "id=$(tr -d '[:space:]' < steam_appid.txt)" >> "$GITHUB_OUTPUT"
      - uses: actions/download-artifact@v8
        with:
          name: Build-StandaloneWindows64
          path: artifact
      # IL2CPP ve Burst'ün "gönderme" klasörleri
      - run: rm -rf artifact/Builds/Windows/*_ButDontShipItWithYourPlayer artifact/Builds/Windows/*_DoNotShip
      - uses: game-ci/steam-deploy@87f8a362c6a8a7dbde08099e4c05da88877f7113 # v3.2.2
        with:
          username: ${{ secrets.STEAM_USERNAME }}
          configVdf: ${{ secrets.STEAM_CONFIG_VDF }}
          appId: ${{ steps.app.outputs.id }}
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
