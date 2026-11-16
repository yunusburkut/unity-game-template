# ci-github

GitHub Actions ile bulutta test ve build ([GameCI](https://game.ci), MIT). Paket eklenince oyuna
`.github/workflows/ci.yml` gelir:

1. **test**: `main`'e her push'ta ve her PR'da EditMode + PlayMode testleri (`game-ci/unity-test-runner` v4).
   Sadece Markdown (`*.md`, `docs/`) değişen commit'ler, ör. PLAN.md, testi çalıştırmaz.
2. **compile**: testlerle aynı anda Android ve iOS player script'lerini derler, build almadan
   (`GameKit.Editor.AgentBridge.CompilePlayerScriptsBatch`, GameKit 0.1.3 ve sonrası). `#if UNITY_ANDROID` /
   `#if UNITY_IOS` kodu ve `DISABLESTEAMWORKS` burada kırılır, tag build'inde değil. Çıkış kodu 0 geçti, 1 derleme
   hatası (job düşer), 2 imajda o platform modülü yok (uyarıyla atlanır, geçti sayılmaz). Rapor
   `Logs/agent/compile-player.log`, `Compile-<platform>` artifact'ı olarak iner.
3. **build**: `v*` tag'inde ya da elle çalıştırınca (**Actions > CI > Run workflow**), testler ve compile geçince
   Windows, Android (APK) ve WebGL build'i (`game-ci/unity-builder` v6), `BuildMenu` üzerinden; menüdeki ve agent
   bridge'deki ayarların aynısı. `Builds/` ve `build.log` artifact olarak iner. Her push'ta build alınmaz: agent
   commit'i başına üç Unity build'i private repo'nun Actions dakikalarını bitirir. WebGL'e özgü kodu değiştirdiysen
   tag atmadan önce workflow'u elle çalıştır: WebGL derleme hataları sadece build'de görünür.
4. **itch.io**: `v*` tag'i atınca (`git tag v0.3; git push origin v0.3`) WebGL build'i butler ile itch.io'ya gider.

Windows build'i Windows runner'da alınır (Linux runner'ın iki katı dakika yer); böylece Player Settings'teki scripting
backend'i (Mono ya da IL2CPP) aynen kullanılır. Linux runner yalnızca Mono Windows build'i alabilir. iOS kapalı
gelir: Mac'in yoksa `ci.yml`'deki iOS matrix satırını ve sondaki `ios` job'unu yorumdan çıkar. Linux runner Xcode
projesini yazar, `v*` tag'inde `macos-latest` runner'ı (Linux'un on katı dakika) App Store Connect API key'iyle otomatik
imzalar ve TestFlight'a yükler. Her yüklemeden önce Player Settings'te iOS build numarasını artır; uygulamanın App Store
Connect kaydı bundle id'siyle önceden açılmış olmalı.

## Kurulum (GitHub > Settings > Secrets and variables > Actions)

| Ad | Tür | Ne |
|---|---|---|
| `UNITY_LICENSE` | secret | Personal lisans `.ulf` dosyasının içeriği ([game.ci/docs/github/activation](https://game.ci/docs/github/activation)) |
| `UNITY_EMAIL`, `UNITY_PASSWORD` | secret | Unity hesabı |
| `GAMEKIT_TOKEN` | secret | GameKit `unity-game-template` repo'sundan gelir ve o repo private: GitHub > Settings > Developer settings > **Fine-grained token**, Repository access: yalnızca `unity-game-template`, Permissions: **Contents: Read-only**. Yoksa Package Manager GameKit'i çekemez ve her job ilk adımda düşer. Süresi dolunca yenile |
| `ITCH_GAME` | variable | `kullanici/oyun` (küçük harf); boşsa itch adımı atlanır |
| `BUTLER_API_KEY` | secret | itch.io > Settings > API keys |
| `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_KEY_P8` | secret | Yalnızca `ios` job'u açıksa: App Store Connect > Users and Access > Integrations, **Admin** rolünde API key (bulutta yönetilen dağıtım imzası bunu ister); `_P8` indirilen `.p8` dosyasının içeriği |
| `APPLE_TEAM_ID` | variable | Yalnızca `ios` job'u açıksa: Apple Developer > Membership'teki Team ID |

Secret'ları terminalden de girebilirsin (`gh secret set UNITY_LICENSE < Unity_v6000.x.ulf`, variable için
`gh variable set`); ortamda `GITHUB_TOKEN`/`GH_TOKEN` varken `gh` onu kullanır ve salt-okur token 403 verir. Komutu
token'sız çalıştır: bash'te `env -u GITHUB_TOKEN -u GH_TOKEN gh secret set ...`, PowerShell'de aynı satırda önce
`$env:GITHUB_TOKEN = $null; $env:GH_TOKEN = $null`.

Unity hesabı ve lisans yalnızca GameCI adımlarına verilir, başka action ya da script onları görmez. Üçüncü parti
action'lar commit SHA'sına sabitli (yorumda tag'i yazar), butler da sabit bir sürümde; güncellemek için yeni tag'in
SHA'sını `gh api repos/<sahip>/<repo>/commits/<tag> --jq .sha` ile al ve yorumdaki tag'i de değiştir.

Feel oyunun repo'sunda commit'li durur, checkout onu da getirir; bu yüzden repo **private kalmalı**. Library cache'i de
derlenmiş Feel'i tutar. İlk itch push'undan sonra itch sayfasında html5 kanalını bir kez "Playable in browser" yap.

Android'in Play Store'a gidecek imzalı AAB'si CI'da değil, yerelde alınır (**GameKit > Build > Android (AAB, Google Play)**):
keystore repoya girmez.

## CLAUDE.md'ye eklenecek satır

```
- CI: `.github/workflows/ci.yml` (GameCI) runs the tests and compiles the Android and iOS player scripts (no build)
  on every push to main that changes more than Markdown; a `v*` tag or a manual run (workflow_dispatch) also builds
  Windows, Android and WebGL through BuildMenu, and a `v*` tag pushes WebGL to itch.io. Before tagging a change to
  WebGL-only code, run the workflow by hand. Keep BuildMenu batch-safe (no dialogs, exit 1 on failure) and
  AgentBridge.CompilePlayerScriptsBatch's exit codes (0 OK, 1 error, 2 module missing) as the compile job reads them.
```
