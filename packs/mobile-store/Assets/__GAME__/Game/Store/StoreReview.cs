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
    /// </summary>
    public static class StoreReview
    {
        /// <param name="host">Runs the Android request coroutine; any active MonoBehaviour will do.</param>
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
        static IEnumerator RequestAndroid()
        {
            var manager = new ReviewManager();
            var request = manager.RequestReviewFlow();
            yield return request;
            if (request.Error != ReviewErrorCode.NoError) yield break; // no prompt is a normal outcome
            yield return manager.LaunchReviewFlow(request.GetResult());
        }
#endif
    }
}
