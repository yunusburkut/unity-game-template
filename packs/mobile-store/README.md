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

## Elle yapılacaklar

1. `Assets/__GAME__/Game/__GAME__.Game.asmdef` içindeki `references`'a `"__GAME__.Store"` ekle (bildirim kodu
   yazacaksan `"Unity.Notifications.Android"` ve `"Unity.Notifications.iOS"` de).
2. Unity açılınca External Dependency Manager Android kütüphanelerini çözer (**Assets > External Dependency Manager >
   Android Resolver > Force Resolve**). Android build'i almadan önce bir kez çalıştır.
3. **Project Settings > Mobile Notifications > Android**: zamanlamayı **inexact** seç. Exact alarm izni Play
   politikasında kısıtlı; oyun bildirimine gerekmez.
4. Aynı sayfada **Android > Request Permission on App Launch** ve **iOS > Request Authorization on App Launch**
   kutularını kapat. Paket bunları açık getirir; açık kalırsa izin penceresi ilk açılışta, oyuncu bir şey görmeden
   çıkar ve iOS'ta reddedilen izin bir daha sorulamaz.
5. Android 13+ bildirim izni ister: ilk bildirimi planlamadan önce `Unity.Notifications.Android.PermissionRequest`
   (iOS'ta `AuthorizationRequest`) ile sor, oyuncu bir değer gördükten sonra, ilk açılışta değil.
6. Puan isteğini bir kazançtan sonra çağır. Android'de bölüm başında `StoreReview.Prepare(this)` çağırırsan pencere
   beklemeden çıkar. `host` sahne değişince yok olmayan bir nesne olsun (ör. `DontDestroyOnLoad` bootstrap); yok
   olursa istek sessizce durur. Play ve Apple pencereyi sınırlar; Play'de test için internal test track'i kullan
   (yerel APK'da pencere çıkmaz).

## CLAUDE.md'ye eklenecek satır

Bu README oyuna kopyalanmaz: satır oyunun `CLAUDE.md`'sinde yoksa ekle, yoksa agent'lar `StoreReview`'u bilmez.

```
- Store rating: `__GAME__.Store.StoreReview.Request(host)` after a win, never after a loss or on first launch; it may
  show nothing. On Android call `StoreReview.Prepare(host)` at level start; `host` must outlive the flow (a
  DontDestroyOnLoad object). Game code that calls it needs `"__GAME__.Store"` in `__GAME__.Game.asmdef` references;
  add it if it is missing. Notifications: com.unity.mobile.notifications with inexact scheduling and the
  permission-on-app-launch toggles off; ask permission after the player has seen value, not on first launch.
```
