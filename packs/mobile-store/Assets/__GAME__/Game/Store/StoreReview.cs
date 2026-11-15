using UnityEngine;
#if UNITY_ANDROID && !UNITY_EDITOR
using System.Collections;
using Google.Play.Review;
#endif

namespace __GAME__.Store
{
    /// <summary>
    /// Asks the store for its native rating prompt: Google Play In-App Review on Android, StoreKit on iOS.
    /// Call it after a win or a finished session, never after a loss or on the first launch (launch-review). Both
    /// stores rate-limit the prompt and may show nothing, so never gate anything on it or show a "rate us" button
    /// that calls it.
    /// On Android the request round trip is slow, so Google's guidance is to fetch the review info ahead of time:
    /// call <see cref="Prepare"/> when the level starts, then <see cref="Request"/> at the win. Request alone also
    /// works; it fetches first, and the prompt comes later.
    /// </summary>
    public static class StoreReview
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        static ReviewManager manager;
        static PlayReviewInfo info;
        static bool preparing;
#endif

        /// <summary>Fetches the Android review info so a later Request shows the prompt without the wait. Does
        /// nothing on iOS and in the Editor.</summary>
        /// <param name="host">Runs the Android coroutine. It must stay alive until the fetch ends: a
        /// DontDestroyOnLoad object such as the game's bootstrap, not a screen that the next scene destroys.</param>
        public static void Prepare(MonoBehaviour host)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (info == null && !preparing) host.StartCoroutine(PrepareAndroid());
#endif
        }

        /// <param name="host">Runs the Android coroutine. It must stay alive until the prompt has launched (a
        /// stopped coroutine shows nothing and logs nothing): a DontDestroyOnLoad object such as the game's
        /// bootstrap, not the win screen when a scene change follows.</param>
        public static void Request(MonoBehaviour host)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            host.StartCoroutine(RequestAndroid());
#elif UNITY_IOS && !UNITY_EDITOR
            UnityEngine.iOS.Device.RequestStoreReview();
#else
            Debug.Log("[StoreReview] a phone would ask for a store rating now");
#endif
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        static IEnumerator PrepareAndroid()
        {
            preparing = true;
            manager ??= new ReviewManager();
            var request = manager.RequestReviewFlow();
            yield return request;
            info = request.Error == ReviewErrorCode.NoError ? request.GetResult() : null; // no prompt is normal
            preparing = false;
        }

        static IEnumerator RequestAndroid()
        {
            // a Prepare still in flight is not waited for: its host may have died, leaving preparing set
            if (info == null) yield return PrepareAndroid();
            if (info == null) yield break;
            var launch = info;
            info = null; // the info is good for one launch and goes stale; fetch a fresh one next time
            yield return manager.LaunchReviewFlow(launch);
        }
#endif
    }
}
