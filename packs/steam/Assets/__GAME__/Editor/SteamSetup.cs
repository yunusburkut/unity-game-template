using System;
using System.IO;
using System.Text.RegularExpressions;
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
            // the step's first run is the one that still finds Android without the define; later runs keep a backend
            // the game chose by hand (ProjectSetup's written-once promise)
            bool firstRun = Array.IndexOf(PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.Android).Split(';'),
                "DISABLESTEAMWORKS") < 0;

            // Steamworks.NET itself compiles for Android too; one project-wide define turns it and the game's own Steam
            // code off on phones and the web
            foreach (var target in new[] { NamedBuildTarget.Android, NamedBuildTarget.iOS, NamedBuildTarget.WebGL })
                ProjectSetup.AddDefine(target, "DISABLESTEAMWORKS");

            // Steam gets IL2CPP: faster than Mono, and its game code does not decompile from plain DLLs. A local Windows
            // build then needs the Hub module "Windows Build Support (IL2CPP)" and Visual Studio's "Desktop development
            // with C++" workload; CI builds Windows on a Windows runner for this (ci-github's ci.yml)
            if (firstRun)
                PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.IL2CPP);
        }

        /// <summary>
        /// A Windows build for another store (itch.io): BuildMenu's Windows build with DISABLESTEAMWORKS added for this
        /// build only, so the Standalone defines never stay switched off for the next Steam build. Same output folder
        /// (Builds/Windows) as the Steam build. The Editor recompiles once afterwards, when the defines are put back.
        /// </summary>
        [MenuItem("GameKit/Build/Windows (no Steam, itch.io)")]
        static void WindowsWithoutSteam()
        {
            var defines = PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.Standalone);
            ProjectSetup.AddDefine(NamedBuildTarget.Standalone, "DISABLESTEAMWORKS");
            try { BuildMenu.Windows(); }
            finally { PlayerSettings.SetScriptingDefineSymbols(NamedBuildTarget.Standalone, defines); }
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

            // read from the source, not by reflection: with Android or WebGL active in the Editor, DISABLESTEAMWORKS
            // compiles SteamBootstrap out of the Editor domain while a Windows build is still being made
            var path = Array.Find(Array.ConvertAll(AssetDatabase.FindAssets("SteamBootstrap t:MonoScript"), AssetDatabase.GUIDToAssetPath),
                p => Path.GetFileName(p) == "SteamBootstrap.cs");
            var match = path == null ? Match.Empty
                : Regex.Match(File.ReadAllText(path), @"const\s+uint\s+AppId\s*=\s*(\d+)\s*;");
            if (!match.Success)
            {
                Debug.LogWarning("[Steam] SteamBootstrap.cs or its `const uint AppId = <number>;` line was not found; the App ID check is skipped.");
                return;
            }
            var codeId = uint.Parse(match.Groups[1].Value);

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
