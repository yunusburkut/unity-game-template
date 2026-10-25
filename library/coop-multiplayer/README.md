# coop-multiplayer

2–4 oyunculu online co-op oyunlar için. Mixtrol'den alındı; ağ yığını olarak **FishNet** (FishyUnityTransport +
Unity Relay, host + client, dedicated server yok) varsayılır. Başka bir ağ kütüphanesi kullanacaksan
`networking.md`'yi o kütüphaneye göre yeniden yaz.

## Ekledikleri

| Parça | Ne işe yarar |
|---|---|
| `.claude/rules/networking.md` | FishNet sözleşmesi: yetki, oturum yaşam döngüsü, SyncType'lar, çevrimdışı `NetworkBehaviour` |
| `.claude/skills/coop-chaos-design` | Bir co-op mekaniği girsin mi: kaos, komedi, klip, griefing, hata katmanı |
| `.claude/skills/mechanic-forge` | Tasarım korpusuyla mekanik / oda / bölüm üretme ve mutasyon |
| `.claude/agents/net-auditor.md` | Ağ değişikliğini kurallara göre denetler (salt okunur) |
| `.claude/agents/idea-forge.md` | Korpusu kendi bağlamında çalıştırıp mekanik kartları döndürür |
| `docs/design-corpus/` | Sosyal sabotaj co-op tasarım korpusu: `grammar.md`, `generator.md` ve 4 kaynak PDF (~1.5 MB) |
| `docs/*.md` | Co-op mekanik oyun kitabı, referans oyun incelemeleri, bölüm tasarımı, zorluk ritmi, iki makinede ağ testi |

## Bilmen gerekenler

- `docs/` altındaki her şey **Mixtrol için yazıldı** ve olduğu gibi kopyalandı: referans malzeme, kural değil.
  Skill'ler ve kural dosyası hafifçe genelleştirildi (yollar `__GAME__`, MIX/Linear numaraları silindi); içlerindeki
  Mixtrol örnekleri (tuşlar, cihazlar, bölümler) senin oyununun gerçekleriyle değiştirilmeli.
- Paket FishNet'i kurmaz. `Packages/manifest.json`'a FishNet ve FishyUnityTransport'u, `Game` asmdef'ine
  referanslarını sen ekle.
- `net-auditor` CLAUDE.md'de bir **Networking** bölümü bekler. Şunu ekle:

```markdown
## Networking

FishNet over Unity Relay, host + client. `.claude/rules/networking.md` is the contract; `net-auditor` checks a change
against it. Every networked object works offline (no session), on the host and on a remote client.
```
