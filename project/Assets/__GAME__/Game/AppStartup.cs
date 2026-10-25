using UnityEngine;

namespace __GAME__.Game
{
    /// <summary>Platform defaults applied before the first scene loads.</summary>
    static class AppStartup
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Configure()
        {
#if UNITY_ANDROID || UNITY_IOS
            // Phones default to 30 fps and ignore vSyncCount
            Application.targetFrameRate = 60;
#endif
        }
    }
}
