using GameKit.Editor;
using Unity.Notifications;
using UnityEngine;

namespace __GAME__.Editor
{
    /// <summary>
    /// The mobile-store pack's setup step, run by ProjectSetup after its own: Mobile Notifications 2.5.0 ships iOS
    /// "Request Authorization on App Launch" on, which shows the one-shot iOS prompt before the player has seen any
    /// value (a denial cannot be asked again). This turns it off and keeps Android on inexact scheduling with no
    /// exact-alarm or battery-optimisation permission in the manifest (both are restricted by Play policy). Android has
    /// no launch toggle in this package: POST_NOTIFICATIONS is asked only by the game's own PermissionRequest.
    /// It applies the pack's rule on every run, so Set Up Project puts it back; a game that really needs exact alarms
    /// changes the ExactSchedulingOption line here and says why in its CLAUDE.md.
    /// </summary>
    static class NotificationDefaults
    {
        [ProjectSetupStep]
        public static void Run()
        {
            // the package's own editor API: writes ProjectSettings/NotificationsSettings.asset when a value changes
            NotificationSettings.iOSSettings.RequestAuthorizationOnAppLaunch = false;
            NotificationSettings.AndroidSettings.ExactSchedulingOption = 0;

            bool iosOff = !NotificationSettings.iOSSettings.RequestAuthorizationOnAppLaunch;
            bool inexact = NotificationSettings.AndroidSettings.ExactSchedulingOption == 0;
            if (iosOff && inexact)
                Debug.Log("[mobile-store] Done: iOS authorization on app launch off, Android scheduling inexact.");
            else
                Debug.LogWarning("[mobile-store] Notification settings did not stick (iOS launch authorization off: "
                    + iosOff + ", Android inexact: " + inexact + "). Set them in Project Settings > Mobile "
                    + "Notifications and run Set Up Project again.");
        }
    }
}
