# ci-github

GitHub Actions ile bulutta test ve build ([GameCI](https://game.ci), MIT). Paket eklenince oyuna
`.github/workflows/ci.yml` gelir:

1. **test**: `main`'e her push'ta ve her PR'da EditMode + PlayMode testleri (`game-ci/unity-test-runner@v4`).
2. **build**: testler geçince Windows, Android (APK) ve WebGL build'i (`game-ci/unity-builder@v6`), `BuildMenu`
   üzerinden; menüdeki ve agent bridge'deki ayarların aynısı. `Builds/` ve `build.log` artifact olarak iner.
3. **itch.io**: `v*` tag'i atınca (`git tag v0.3; git push origin v0.3`) WebGL build'i butler ile itch.io'ya gider.

Linux runner'da Windows build'i Mono'dur (IL2CPP için Windows runner gerekir). iOS build'i burada yok: Xcode projesi
Mac'te derlenir.

## Kurulum (GitHub > Settings > Secrets and variables > Actions)

| Ad | Tür | Ne |
|---|---|---|
| `UNITY_LICENSE` | secret | Personal lisans `.ulf` dosyasının içeriği ([game.ci/docs/github/activation](https://game.ci/docs/github/activation)) |
| `UNITY_EMAIL`, `UNITY_PASSWORD` | secret | Unity hesabı |
| `ITCH_GAME` | variable | `kullanici/oyun` (küçük harf); boşsa itch adımı atlanır |
| `BUTLER_API_KEY` | secret | itch.io > Settings > API keys |

Feel oyunun repo'sunda commit'li durur, checkout onu da getirir; bu yüzden repo **private kalmalı**. Library cache'i de
derlenmiş Feel'i tutar. İlk itch push'undan sonra itch sayfasında html5 kanalını bir kez "Playable in browser" yap.

Android'in Play Store'a gidecek imzalı AAB'si CI'da değil, yerelde alınır (**GameKit > Build > Android (AAB, Google Play)**):
keystore repoya girmez.

## CLAUDE.md'ye eklenecek satır

```
- CI: `.github/workflows/ci.yml` (GameCI) runs the tests and builds Windows, Android and WebGL through BuildMenu on
  every push to main; a `v*` tag pushes WebGL to itch.io. Keep BuildMenu batch-safe: no dialogs, exit 1 on failure.
```
