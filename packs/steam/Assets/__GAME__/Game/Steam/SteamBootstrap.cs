// DISABLESTEAMWORKS is set for Android, iOS and WebGL by SteamSetup, so phone and web builds compile none of this.
#if !DISABLESTEAMWORKS
using Steamworks;
using UnityEngine;

namespace __GAME__.Steam
{
    /// <summary>
    /// Starts the Steam API before the first scene and keeps its callbacks pumping; no scene object needed.
    /// Steam features (achievements, overlay, cloud saves) check <see cref="Initialized"/> first, so the game still
    /// runs in the Editor when Steam is closed. Once the real App ID is set, a desktop build started outside Steam
    /// relaunches through Steam and quits; a Windows build for another store (itch.io) comes from
    /// GameKit/Build/Windows (no Steam) instead, which compiles this out with DISABLESTEAMWORKS (Editor/SteamSetup.cs).
    /// </summary>
    public sealed class SteamBootstrap : MonoBehaviour
    {
        // TODO: the game's App ID from Steamworks. 480 is Valve's Spacewar test app. steam_appid.txt in the project
        // root holds the same number for Editor runs and the CI Steam job; commit it. SteamAppIdCheck (Editor) fails a
        // desktop build when the two differ. It reads this line from the source text: keep it `const uint AppId = <number>;`.
        const uint AppId = 480;
#if !UNITY_EDITOR
        // static readonly, not const: two consts would fold the relaunch check below into unreachable code (CS0162)
        static readonly uint TestAppId = 480;
#endif

        public static bool Initialized { get; private set; }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetStatics() => Initialized = false;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Create()
        {
            // steam_api64.dll / libsteam_api.so missing (a stripped build, an unsupported platform): the first Steam call
            // throws, as in Steamworks.NET's reference SteamManager; the game runs on without Steam
            try
            {
#if !UNITY_EDITOR
                // started outside Steam (double-clicked exe): Steam relaunches the game through itself and this copy
                // quits. Not while the App ID is still the test app: Steam would launch Spacewar instead of this game.
                if (AppId != TestAppId && SteamAPI.RestartAppIfNecessary(new AppId_t(AppId)))
                {
                    Application.Quit();
                    return;
                }
#endif
                // InitEx, not Init: its message names the real cause (Steam closed, wrong App ID, app not owned)
                Initialized = SteamAPI.InitEx(out var error) == ESteamAPIInitResult.k_ESteamAPIInitResult_OK;
                if (!Initialized)
                {
                    Debug.LogWarning($"[Steam] SteamAPI.InitEx failed: {error}. Steam features are off.");
                    return;
                }
            }
            catch (System.DllNotFoundException e)
            {
                Debug.LogWarning($"[Steam] The Steam API library is missing ({e.Message}). Steam features are off.");
                return;
            }

            var host = new GameObject("Steam");
            DontDestroyOnLoad(host);
            host.AddComponent<SteamBootstrap>();
        }

        void Update() => SteamAPI.RunCallbacks();

        void OnDestroy()
        {
            if (!Initialized) return;
            SteamAPI.Shutdown();
            Initialized = false;
        }
    }
}
#endif
