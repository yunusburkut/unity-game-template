# coop-multiplayer

2–4 oyunculu online co-op oyunlar için. Mixtrol'den alındı; ağ yığını olarak **FishNet** (FishyUnityTransport +
Unity Relay, host + client, dedicated server yok) varsayılır. Başka bir ağ kütüphanesi kullanacaksan
`networking.md`'yi o kütüphaneye göre yeniden yaz.

## Ekledikleri

| Parça | Ne işe yarar |
|---|---|
| `packages.json` | FishNet 4.7.3 ve FishyUnityTransport (commit'e sabit git paketleri), `com.unity.services.multiplayer` 2.3.3 (Relay + kimlik doğrulama), `com.unity.transport` 6.6.0, Multiplayer Play Mode 3.0.0; `new-game.ps1` bunları `Packages/manifest.json`'a, `gameReferences`'taki altı assembly'yi `__GAME__.Game.asmdef`'e ekler |
| `.claude/rules/networking.md` | Genel FishNet sözleşmesi: yetki, oturum yaşam döngüsü, SyncType'lar, çevrimdışı `NetworkBehaviour`; yalnız frontmatter'ındaki yollar (`Game/Net/**`, `Game/Prefabs/Net/**`, `docs/network-testing.md`) açılınca yüklenir |
| `docs/networking-mixtrol-example.md` | Mixtrol'ün sözleşmeyi nasıl uyguladığı (tahmin edilen kopyalar, mekanizma listesi, oda ekranı, tek PC testi): kural değil, örnek; ihtiyaç olunca okunur |
| `docs/design-audit.md` | Oyunun korpusa göre denetim defteri: boş gelir, ilk denetim doldurur (satır biçimi başlığında) |
| `.claude/skills/coop-chaos-design` | Bir co-op mekaniği girsin mi: kaos, komedi, klip, griefing, hata katmanı |
| `.claude/skills/mechanic-forge` | Tasarım korpusuyla mekanik / oda / bölüm üretme ve mutasyon |
| `.claude/agents/net-auditor.md` | Ağ değişikliğini kurallara göre denetler (salt okunur) |
| `.claude/agents/idea-forge.md` | Korpusu kendi bağlamında çalıştırıp mekanik kartları döndürür |
| `docs/design-corpus/` | Sosyal sabotaj co-op tasarım korpusu: `grammar.md`, `generator.md` ve 4 kaynak PDF (~1.5 MB) |
| `Assets/__GAME__/Editor/CoopSetup.cs` | Kurulum adımı: `runInBackground` açık; odağı kaybeden host donmaz, iki build tek makinede test edilir |
| `docs/*.md` | Co-op mekanik oyun kitabı, referans oyun incelemeleri, bölüm tasarımı, zorluk ritmi, iki makinede ağ testi |

## Bilmen gerekenler

- `docs/` altındaki her şey **Mixtrol için yazıldı** ve olduğu gibi kopyalandı: referans malzeme, kural değil.
  Skill'ler ve kural dosyası hafifçe genelleştirildi (yollar `__GAME__`, MIX/Linear numaraları silindi); içlerindeki
  Mixtrol örnekleri (tuşlar, cihazlar, bölümler) senin oyununun gerçekleriyle değiştirilmeli. Mixtrol'e özgü
  sınıf, sahne ve menü adları `docs/networking-mixtrol-example.md`'de toplandı; kural dosyası yalnız genel FishNet
  kurallarını ve rolleri (oturum sahibi, spawner, mekanizma listesi) taşır.
- `docs/difficulty-rhythm.md` Mixtrol'ün tam araştırma taslağıdır; oyunda geçerli DR01–DR28 `gamekit:level-beat-review`
  içindeki damıtılmış kopyadır ve çelişkide o kazanır.
- Paketler `packages.json`'ın `dependencies`'inden, `__GAME__.Game.asmdef`'in altı FishNet / UGS referansı da
  `gameReferences`'ından gelir: `new-game.ps1` ikisini de yalnız bu paket seçildiğinde ekler, FishNet'siz oyunların
  asmdef'i değişmez. Elle eklenen tek şey `__GAME__.Editor.asmdef`'e `FishNet.Runtime`'dır, o da bir Editor betiği ağ
  tiplerine dokunduğunda (aşağıdaki Networking bloğu).
- WebGL ve mobil: WebGL istemcisi Relay'e yalnız `wss` ile bağlanır, telefonda arka plana düşen host oturumu bitirir;
  kurallar `networking.md`'nin Platforms bölümünde.
- Ağ kodu `Assets/__GAME__/Game/Net/` altında durur ki kural dosyası onunla yüklensin.
- `net-auditor` CLAUDE.md'de bir **Networking** bölümü bekler. Şunu ekle:

```markdown
## Networking

FishNet over Unity Relay, host + client. `.claude/rules/networking.md` is the contract; `net-auditor` checks a change
against it. Every networked object works offline (no session), on the host and on a remote client. Networked code
lives in `Assets/__GAME__/Game/Net/`. Authority: characters are their owner's, the world is the host's (change this
line if __GAME__ splits it differently). `__GAME__.Game.asmdef` already references `FishNet.Runtime`,
`FishyUnityTransport`, `Unity.Networking.Transport`, `Unity.Services.Core`, `Unity.Services.Authentication` and
`Unity.Services.Multiplayer` (new-game adds them); `__GAME__.Editor.asmdef` gets `FishNet.Runtime` by hand when an
Editor script touches network types. A missing one fails as CS0246 on `FishNet`.

In this co-op game, "is this mechanic fun / should we build it" goes to the `coop-chaos-design` skill first;
`gamekit:prototype` only when the gate ships the card with a row that needs a spike. A batch of ideas is the
`idea-forge` agent, one card worked in the chat is `mechanic-forge`.
```
