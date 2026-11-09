using UnityEditor.Build;

namespace __GAME__.Editor
{
    /// <summary>The steam pack's setup step, run by ProjectSetup after its own.</summary>
    static class SteamSetup
    {
        [ProjectSetupStep]
        public static void Run()
        {
            // Steamworks.NET itself compiles for Android too; one project-wide define turns it and the game's own Steam
            // code off on phones and the web
            foreach (var target in new[] { NamedBuildTarget.Android, NamedBuildTarget.iOS, NamedBuildTarget.WebGL })
                ProjectSetup.AddDefine(target, "DISABLESTEAMWORKS");
        }
    }
}
