using System;
using System.IO;
using System.Reflection;
using GameKit.Editor;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

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

    /// <summary>
    /// Fails a desktop build whose SteamBootstrap.AppId differs from steam_appid.txt in the project root: the Editor
    /// starts Steam with the file's number, the build relaunches through the constant's, and the CI Steam job uploads
    /// to the file's. A missing file only warns (it is created on the first Editor run with Steam).
    /// </summary>
    sealed class SteamAppIdCheck : IPreprocessBuildWithReport
    {
        const string AppIdFile = "steam_appid.txt";

        public int callbackOrder => 0;

        public void OnPreprocessBuild(BuildReport report)
        {
            if (report.summary.platformGroup != BuildTargetGroup.Standalone) return;
            if (Array.IndexOf(PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.Standalone).Split(';'), "DISABLESTEAMWORKS") >= 0) return;

            // read by reflection: the Editor assembly does not reference __GAME__.Steam
            var field = Type.GetType("__GAME__.Steam.SteamBootstrap, __GAME__.Steam")
                ?.GetField("AppId", BindingFlags.NonPublic | BindingFlags.Static);
            if (field == null) return;
            var codeId = (uint)field.GetRawConstantValue();

            if (!File.Exists(AppIdFile))
            {
                Debug.LogWarning($"[Steam] {AppIdFile} is missing from the project root; SteamBootstrap.AppId is {codeId}. Create it with that number and commit it.");
                return;
            }
            var text = File.ReadAllText(AppIdFile).Trim();
            if (!uint.TryParse(text, out var fileId) || fileId != codeId)
                throw new BuildFailedException($"[Steam] SteamBootstrap.AppId is {codeId} but {AppIdFile} says '{text}'. Set both to the game's App ID.");
        }
    }
}
