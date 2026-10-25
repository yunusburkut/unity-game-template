# Ses — ne gerek, nereye takılır

GDD'nin "Ses ve his" bölümünün karşılığı bugün **dört klip** (`SFX_Checkpoint`, `SFX_Death`, geçici `SFX_Dash` ve `SFX_Jump`) ve
sahnelerde **hiç `AudioSource` yok**. Bu belge eksiğin tamamını, her klibin hangi kod satırında
tetiklendiğiyle birlikte sayar — böylece klipler geldiğinde iş sadece Inspector'da bağlamaya iner.

Juice zaten Feel ile kurulu: tetikleme noktalarının çoğunda bir `MMF_Player` alanı
var ve boş bırakılınca sessizce hiçbir şey yapıyor. Ses bir `MMF_Sound` (ya da
`MMF_MMSoundManagerSound`) geri bildirimi olarak **o oynatıcının içine** eklenir; o noktalarda yeni
kod gerekmez. İstisnalar: `Door`'un alanı yok; tutma/bırakma, kurtarma, kazan gerilimi ve doğuş
korumasının bitişinin tetiği yok (aşağıda **oynatıcı yok** / **tetik yok** diye işaretli).

## Altyapı

1. **`MMSoundManager`** sahneye konur (`Assets/Feel/MMTools/Core/MMAudio/MMSoundManager/`). Hazır bir
   prefab yok, obje elle kurulur. Havuz ve kanallar (Sfx / UI / Music) bunun içindir.
2. Klipler `Assets/Mixtrol/Game/Audio/` altına, adlandırma `SFX_<Ne>.wav`.
3. `AudioListener` dört sahnenin dördünde de var (kameranın üstünde).

## Klip listesi

Kural: **bir etki ne kadar yüksek sesliyse o kadar nadir olmalı.** Sütunlardaki "sıklık" bunun
ölçüsü; saniyede birkaç kez çalan bir klip kısa, sönük ve varyasyonlu olmalı.

### Karakter — `PlayerFeel` (karakter prefab'ı)

| Klip | Oynatıcı | Tetikleyen | Sıklık | Not |
| --- | --- | --- | --- | --- |
| `SFX_Jump` | `jump` | `MovementState.JumpTriggered` | çok sık | Kısa, kuru. **Bağlı, geçici** (MIX-292): Feel demosunun zıplaması (`MMFeedbacksDemoJump`), baştaki 80 ms sessizliği kesilmiş ve yükseltilmiş, 0.2 s; ±1 yarım ton, ses 0.30–0.36 |
| `SFX_Land` | `land` | `Landed` | çok sık | **Şimdilik yok** (2026-10-04, kullanıcı kaldırttı; geçici bir kick denenmişti, MIX-292). Gelirse: `PlayerFeel.Report` zaten `land.PlayFeedbacks(position, intensity)` çağırıyor ve `intensity = LandingIntensity(state.LandingSpeed)`. Ses seviyesini/pitch'ini bu yoğunluğa bağla — yumuşak iniş ile sert iniş tek klip, iki his |
| `SFX_Dash` | `dashStart` | `DashTriggered` | sık | **Bağlı, geçici** (MIX-221 tur 9): Feel demosunun woosh'u (`FeelDuckWoosh`, 0.18 s), ±1 yarım ton, ses 0.45–0.55. Gerçek klip gelince yalnız dosya değişir |
| `SFX_DashEnd` | `dashEnd` | dash biter | sık | Çok sönük ya da hiç; atılmanın sesi başındadır |
| `SFX_WallBump` | `wallBump` | duvara çarpma | orta | |
| `SFX_Respawn` | `respawn` | yeniden doğuş | seyrek | |

Zıplamanın *tepesi* için ayrı bir oynatıcı yok. GDD "kalkış, tepe, iniş" diyor; tepe sesi istenirse
`MovementState` zaten apex'i biliyor, ama önce kalkış ve iniş oturtulsun — tepe, üçü arasında en az
okunan.

### Takas — `ControlSwapView` (karakter prefab'ı)

| Klip | Oynatıcı | Tetikleyen | Not |
| --- | --- | --- | --- |
| **`SFX_Radio`** | `radioFeedback` | telsiz eldeyken ilk kare (`UpdateRadio`, `asking && !_wasAsking`) | **Oyunun imza sesi.** Cızırtı duyulduğunda ortak bir şey istiyor demektir — ekrana bakmayan oyuncu bunu duyup ortağına dönmeli. Kısa, telsiz cızırtısı, karakterin konumundan 3D |
| `SFX_SwapPuff` | `swapPuff` | takas kapısı yeni hareket dağıttı | Puf; simgenin değiştiğinin duyulan hali |

### Taşınan obje — `CoCarriedObject` (`CarryCauldron.prefab`)

| Klip | Oynatıcı | Tetikleyen | Not |
| --- | --- | --- | --- |
| ~~`SFX_Spill`~~ | — | — | Kalktı (2026-09-28, MIX-274): kazanın sıvısı koddan söküldü, dökülme yok |

### Kovalayan tehlike — `ChasingHazard`

| Klip | Oynatıcı | Tetikleyen | Not |
| --- | --- | --- | --- |
| **`SFX_ChaseWarn`** | `warnedFeedback` | başlangıç çizgisi geçildi, duvar titriyor | GDD'nin "tehlike yaklaştığında ses tek başına yeterli uyarı olmalı" maddesinin ilk yarısı |
| `SFX_ChaseRelease` | `releasedFeedback` | duvar yürümeye başladı | Sürekli bir uğultu ister: bu tek atışlık bir oynatıcı, sürekli ses için duvarın üstünde döngülü bir kaynak gerekir |
| `SFX_ChaseCaught` | `caughtFeedback` | yakaladı | Ölüm sesiyle çakışmasın |

### Mekanizmalar

| Klip | Bileşen · oynatıcı | Not |
| --- | --- | --- |
| `SFX_PlateDown` / `SFX_PlateUp` | `PressurePlate` · `pressedFeedback` / `releasedFeedback` | Devir teslim anının zamanlayıcısı; iki ses belirgin biçimde farklı olmalı |
| `SFX_DoorOpen` / `SFX_DoorClose` | `Door` — **oynatıcı yok** | Kapının MMF_Player alanı yok. İstenirse eklenir; plakanın sesi kapıyı zaten haber veriyor |
| `SFX_FloorCrack` / `SFX_FloorCollapse` / `SFX_FloorRestore` | `CrumblingFloor` · `crackedFeedback` / `collapsedFeedback` / `restoredFeedback` | Çatlama sesi **uyarıdır**, çökme sonuçtur |
| `SFX_Seesaw` | `Seesaw` · `creakFeedback`, `slammedFeedback` | Gıcırtı sürekli, çarpma tek atış |
| `SFX_PushStart` / `SFX_PushLand` | `Pushable` · `startedFeedback` / `landedFeedback` | |
| `SFX_LaunchPad` | `LaunchPad` · `firedFeedback` | |
| `SFX_Hazard` | `Hazard` · `touched` | |
| `SFX_Decoy` | `DecoyCheckpoint` · `mocked` | Sönen bir şey, alaycı düşen bir ton. **Bu klip olmadan sahte checkpoint bir hatadan ayırt edilemez** |
| `SFX_Checkpoint` ✅ | `Checkpoint` · `reached` | Var |
| `SFX_Death` ✅ | `RespawnFeel` · `died` | Var |
| `SFX_Goal` | `LevelGoal` · `reachedFeedback` | Bölümün en nadir ve en büyük sesi. Host bitişi onayladığında çalar, yerel tetikte değil |

### Tasarım korpusundan gelenler (2026-09-22)

Bunlar `docs/design-corpus` ile eklendi (kimlikler `.claude/skills/game-feel/references/feedback-stack.md`'de).
Çoğunun henüz oynatıcı alanı yok; eklenince bu tabloya yazılır.

| Klip | Nereye | Korpus | Not |
| --- | --- | --- | --- |
| `SFX_Grab` / `SFX_Release` | taşıma: `CoCarriedObject`, `Carryable` — **oynatıcı yok** | FP16 | Tutma kilitlenir, bırakma farklı bir imza: sahiplik hiçbir zaman belirsiz kalmaz |
| `SFX_Save` | kurtarma / yakalama anı (kademe-1) — **tetik yok** | FP08, FP09, FR09 | Kurtarma hata kadar duyulur; ölümden kısa ve daha parlak |
| `SFX_SwapOut` / `SFX_SwapIn` | `ControlSwapView` — hareketi veren ve alan gövde | FP28 | Eş ama zıt iki ses; bugünkü `SFX_SwapPuff`'ın iki yarısı |
| `SFX_GraceEnd` | doğuştan sonra dokunulmazlığın bitişi — **tetik yok** | FS7 | Bugün 1 sn'lik koruma ne görülüyor ne duyuluyor |

**Kural (FR14):** rutin eylem (zıplama, iniş, atılma) kısa ve sönük; nadir olay (hedef, takım kurtarışı,
ölüm) belirgin. Aynı sesi iki farklı olay sınıfına verme (FX04).

## Bitti sayılma ölçütü

GDD'nin ses maddeleri:

1. ✅ Hareketin her anı seslenir, inişin şiddeti düşüş hızına göre değişir → `PlayerFeel`.
2. ✅ Telsiz cızırtısı duyulunca ortak bir şey istiyor demektir → `SFX_Radio`.
3. ✅ Yaklaşan tehlike ekrana bakmayan oyuncuya ses ile anlatılır → `SFX_ChaseWarn`.
4. ✅ Juice Feel ile kurulur → zaten kurulu.

Dördü de sağlandığında `docs/gdd.md` yol haritasındaki **Ses** aşaması ✅ olur.
