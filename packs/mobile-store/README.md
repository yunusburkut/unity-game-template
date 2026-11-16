# mobile-store

Google Play ve App Store'da yayınlanacak mobil oyunlar için: mağaza puan isteği ve yerel bildirimler. Paket eklenince:

1. `Packages/manifest.json` içine OpenUPM registry'si (`com.google` scope'u) ve şunlar eklenir:
   - **Google Play In-App Review** `com.google.play.review` 1.8.4 (Apache-2.0). Play Core ve External Dependency
     Manager'ı da çeker. Son sürüm Şubat 2025'te çıktı: target API 36 ile ilk build'de telefonda dene.
   - **Unity Mobile Notifications** `com.unity.mobile.notifications` 2.5.0: Android ve iOS yerel bildirimleri.
   - Unity'nin yerleşik **Asset Bundle** ve **UnityWebRequestAssetBundle** modülleri (`com.unity.modules.assetbundle`,
     `com.unity.modules.unitywebrequestassetbundle`): Play Core'un `Google.Play.Common`
     kodu onlarsız derlenmez.
2. `Game/Store/StoreReview.cs` (kendi asmdef'i `__GAME__.Store`): `StoreReview.Request(this)` Android'de Play'in,
   iOS'ta StoreKit'in puan penceresini ister. iOS tarafı Unity'nin kendi `Device.RequestStoreReview()`'u, paket istemez.
3. `new-game.ps1`, `__GAME__.Game.asmdef` içindeki `references`'a `"__GAME__.Store"`'u ekler.
4. `Editor/Store/NotificationDefaults.cs` (bir `[ProjectSetupStep]`, her **Set Up Project**'te çalışır, log'a
   `[mobile-store] Done:` yazar) **Project Settings > Mobile Notifications** ayarlarını paketin kuralına çeker:
   - **iOS > Request Authorization on App Launch** kapalı. Paket bunu açık getirir; açık kalırsa izin penceresi ilk
     açılışta, oyuncu bir şey görmeden çıkar ve iOS'ta reddedilen izin bir daha sorulamaz.
   - **Android > Schedule at exact time**: hiçbir seçenek işaretli değil, yani zamanlama **inexact** ve manifest'e
     exact alarm ya da pil optimizasyonu izni eklenmez. Bu izinler Play politikasında kısıtlı; oyun bildirimine
     gerekmez. Android'de 2.5.0'ın açılışta izin isteyen bir kutusu yok: izni yalnızca oyunun kendi
     `PermissionRequest`'i sorar (aşağıda 3. adım).
   Exact alarm gerçekten gereken bir oyun bu adımdaki `ExactSchedulingOption` satırını değiştirir ve nedenini
   `CLAUDE.md`'sine yazar; yoksa Set Up Project ayarı geri alır.

## Elle yapılacaklar

1. Paket oyuna başka yoldan geldiyse (sync, elle kopya) `Assets/__GAME__/Game/__GAME__.Game.asmdef` içindeki
   `references`'a `"__GAME__.Store"` ekle; `new-game.ps1` ile açılan oyunda zaten vardır. Bildirim kodu yazacaksan
   `"Unity.Notifications.Android"` ve `"Unity.Notifications.iOS"`'u her durumda sen ekle.
2. Unity açılınca External Dependency Manager Android kütüphanelerini çözer (**Assets > External Dependency Manager >
   Android Resolver > Force Resolve**). Android build'i almadan önce bir kez çalıştır. `StoreReview.cs`'in Play
   Review kodu `#if UNITY_ANDROID && !UNITY_EDITOR` altında: Editor ve template testleri onu derlemez, ilk Android
   build'i (ya da ci-github paketinin Android job'u) derler. Bu dosyayı değiştirdiysen bir Android build'i al.
3. Android 13+ bildirim izni ister: ilk bildirimi planlamadan önce `Unity.Notifications.Android.PermissionRequest`
   (iOS'ta `AuthorizationRequest`) ile sor, oyuncu bir değer gördükten sonra, ilk açılışta değil.
4. Puan isteğini bir kazançtan sonra çağır. Android'de bölüm başında `StoreReview.Prepare(this)` çağırırsan pencere
   beklemeden çıkar. `host` sahne değişince yok olmayan bir nesne olsun (ör. `DontDestroyOnLoad` bootstrap); yok
   olursa istek sessizce durur. Play ve Apple pencereyi sınırlar; Play'de test için internal test track'i kullan
   (yerel APK'da pencere çıkmaz).

## CLAUDE.md'ye eklenecek satır

Bu README oyuna kopyalanmaz: satır oyunun `CLAUDE.md`'sinde yoksa ekle, yoksa agent'lar `StoreReview`'u bilmez.

```
- Store rating: `__GAME__.Store.StoreReview.Request(host)` after a win, never after a loss or on first launch; it may
  show nothing. On Android call `StoreReview.Prepare(host)` at level start; `host` must outlive the flow (a
  DontDestroyOnLoad object). Game code that calls it needs `"__GAME__.Store"` in `__GAME__.Game.asmdef` references;
  add it if it is missing. Notifications: com.unity.mobile.notifications with inexact scheduling and iOS
  authorization-on-app-launch off, both set by `Editor/Store/NotificationDefaults.cs` on every Set Up Project (change
  them there, not in Project Settings); ask permission (`PermissionRequest` / `AuthorizationRequest`) after the player
  has seen value, not on first launch. Notification code references `"Unity.Notifications.Android"` and
  `"Unity.Notifications.iOS"` in its asmdef (add them if missing); those assemblies exist only on Android, iOS and the
  Editor while `__GAME__.Game` also builds for PC and WebGL, so every Android call sits under
  `#if UNITY_ANDROID && !UNITY_EDITOR` and every iOS call under `#if UNITY_IOS && !UNITY_EDITOR`, as in
  `StoreReview.cs`. Those branches compile only in an Android or iOS build: build one after changing them.
```
