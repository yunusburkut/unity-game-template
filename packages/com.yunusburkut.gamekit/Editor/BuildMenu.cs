using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace GameKit.Editor
{
    /// <summary>
    /// One build entry per target, writing its result to Logs/agent/build.log so an agent can read it.
    /// From the menu, from AgentBridge (write "build android" or "build aab dev" into Logs/agent/request.txt), or with
    /// the Editor closed: Unity -batchmode -quit -projectPath . -buildTarget Android -executeMethod GameKit.Editor.BuildMenu.Android
    /// (-buildTarget opens the project on that target, so the batch build skips a platform switch).
    /// In the Editor the active platform is switched back afterwards, so a build never leaves it on another target.
    /// File > Build Profiles > Development Build makes every entry here a development build (profiler attached).
    /// </summary>
    public static class BuildMenu
    {
        internal const string LogPath = "Logs/agent/build.log";

        [MenuItem("GameKit/Build/Windows")] public static void Windows() => Build(BuildTarget.StandaloneWindows64);
        [MenuItem("GameKit/Build/Android (APK)")] public static void Android() => Build(BuildTarget.Android);
        [MenuItem("GameKit/Build/Android (AAB, Google Play)")] public static void AndroidBundle() => Build(BuildTarget.Android, appBundle: true);
        [MenuItem("GameKit/Build/iOS (Xcode project)")] public static void IOS() => Build(BuildTarget.iOS);
        [MenuItem("GameKit/Build/WebGL")] public static void WebGL() => Build(BuildTarget.WebGL);

        /// <summary>The names TryParse takes, for help text (AgentBridge's Unknown request answer).</summary>
        public const string TargetNames = "windows|android|aab|ios|webgl";

        public static bool TryParse(string name, out BuildTarget target, out bool appBundle)
        {
            appBundle = false;
            switch (name.Trim().ToLowerInvariant())
            {
                case "windows": target = BuildTarget.StandaloneWindows64; return true;
                case "android": target = BuildTarget.Android; return true;
                case "aab": target = BuildTarget.Android; appBundle = true; return true;
                case "ios": target = BuildTarget.iOS; return true;
                case "webgl": target = BuildTarget.WebGL; return true;
                default: target = default; return false;
            }
        }

        /// <param name="askToSave">The menu asks to save unsaved scenes; the agent bridge (unfocused, no one to answer
        /// a dialog) fails instead.</param>
        public static void Build(BuildTarget target, bool appBundle = false, bool development = false, bool askToSave = true)
        {
            var group = BuildPipeline.GetBuildTargetGroup(target);
            if (!BuildPipeline.IsBuildTargetSupported(group, target))
            {
                Finish(target, "FAILED  " + target + ": its platform module is not installed (Unity Hub > Installs > Add modules).\n", false);
                return;
            }

            if (EditorUtility.scriptCompilationFailed)
            {
                Finish(target, "FAILED  " + target + ": scripts do not compile, see Logs/agent/compile.log.\n", false);
                return;
            }

            development |= EditorUserBuildSettings.development;
            if (target == BuildTarget.WebGL) SetWebGLCodeOptimization(development);
            AssetDatabase.SaveAssets();

            var scenes = new List<string>();
            foreach (var scene in EditorBuildSettings.scenes)
                if (scene.enabled) scenes.Add(scene.path);

            // BuildPlayer reads the scene files on disk, so unsaved edits would silently miss the build.
            var unsaved = new List<string>();
            for (int i = 0; i < EditorSceneManager.sceneCount; i++)
            {
                var open = EditorSceneManager.GetSceneAt(i);
                if (open.isDirty && scenes.Contains(open.path)) unsaved.Add(open.path);
            }
            if (unsaved.Count > 0 && !(askToSave && EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()))
            {
                Finish(target, "FAILED  " + target + ": unsaved scene(s) " + string.Join(", ", unsaved)
                    + "; save them and build again.\n", false);
                return;
            }

            var startTarget = EditorUserBuildSettings.activeBuildTarget;
            var startGroup = BuildPipeline.GetBuildTargetGroup(startTarget);
            bool startAppBundle = EditorUserBuildSettings.buildAppBundle;
            bool startCustomKeystore = PlayerSettings.Android.useCustomKeystore;
            var startCompression = PlayerSettings.WebGL.compressionFormat;

            bool debugSigned = DebugSigns(target, appBundle, startCustomKeystore, Application.isBatchMode,
                !string.IsNullOrEmpty(PlayerSettings.Android.keystorePass) &&
                !string.IsNullOrEmpty(PlayerSettings.Android.keyaliasPass));

            BuildReport report = null;
            string thrown = null;
            string symbols = null;
            var symbolSettings = appBundle ? AndroidDebugSymbols.Read() : null;
            try
            {
                if (target == BuildTarget.Android) EditorUserBuildSettings.buildAppBundle = appBundle;
                // a dev WebGL build is for quick local checks: uncompressed loads from any static server and skips the
                // slow Brotli pass; the project's own format (ProjectSetup: Brotli for itch.io) is put back below
                if (target == BuildTarget.WebGL && development)
                    PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;
                if (debugSigned) PlayerSettings.Android.useCustomKeystore = false;
                if (appBundle) symbols = AndroidDebugSymbols.ForStore(symbolSettings);
                report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = scenes.ToArray(),
                    locationPathName = OutputPath(target, appBundle),
                    target = target,
                    targetGroup = group,
                    options = development ? BuildOptions.Development | BuildOptions.ConnectWithProfiler : BuildOptions.None,
                });
            }
            catch (System.Exception e)
            {
                thrown = e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                EditorUserBuildSettings.buildAppBundle = startAppBundle;
                PlayerSettings.Android.useCustomKeystore = startCustomKeystore;
                PlayerSettings.WebGL.compressionFormat = startCompression;
                AndroidDebugSymbols.Restore(symbolSettings);
            }
            if (thrown != null)
            {
                // after the restore: Finish exits a batch run. Every caller (menu, -executeMethod, AgentBridge) gets the
                // same build.log contract: FAILED, never the previous build's text, and the Editor back on its own target
                SwitchBack(startGroup, startTarget, target);
                Finish(target, "FAILED  " + target + ": " + thrown + "\n", false);
                return;
            }

            var summary = report.summary;
            var text = new StringBuilder(1024);
            text.Append(summary.result).Append("  ").Append(target).Append(appBundle ? " (AAB)" : "").Append("  ")
                .Append(AgentBridge.Timestamp()).Append('\n');
            text.Append("output ").Append(summary.outputPath).Append('\n');
            text.Append("development ").Append(development ? "yes" : "no").Append('\n');
            if (target == BuildTarget.WebGL)
                text.Append("compression ").Append(development ? WebGLCompressionFormat.Disabled : startCompression)
                    .Append(development ? " (dev build)" : "").Append('\n');
            text.Append("size ").Append((summary.totalSize / (1024f * 1024f)).ToString("0.0")).Append(" MB, time ")
                .Append(summary.totalTime.TotalSeconds.ToString("0")).Append(" s\n");
            if (target == BuildTarget.Android)
            {
                text.Append("versionCode ").Append(PlayerSettings.Android.bundleVersionCode)
                    .Append(", targetSdk ").Append(PlayerSettings.Android.targetSdkVersion).Append('\n');
                // Play rejects a debug-signed bundle; the keystore passwords are not saved in the project, so a
                // fresh Editor session needs them typed in again (Player Settings > Publishing Settings)
                if (appBundle && !PlayerSettings.Android.useCustomKeystore)
                    text.Append("WARNING debug-signed: Google Play will reject this AAB, set a keystore in Publishing Settings\n");
                if (debugSigned)
                    text.Append("signing debug key: no keystore passwords in this session (fine for a test APK)\n");
                if (symbols != null) text.Append("debug symbols ").Append(symbols).Append('\n');
            }
            foreach (var step in report.steps)
            foreach (var message in step.messages)
                // Play blocks updates with a 4 KB-aligned native plug-in from 1 Feb 2027, and Unity only warns about it
                if (message.type == LogType.Error || message.type == LogType.Exception ||
                    (message.type == LogType.Warning && message.content.IndexOf("16 KB", System.StringComparison.OrdinalIgnoreCase) >= 0))
                    text.Append('[').Append(step.name).Append("] ").Append(message.content).Append('\n');

            SwitchBack(startGroup, startTarget, target);
            Finish(target, text.ToString(), summary.result == BuildResult.Succeeded);
        }

        /// <summary>
        /// True when an Android build signs with the debug key instead of the project's keystore. A batch run (CI) has
        /// no keystore passwords, and neither has an Editor session where no one typed them (Unity does not save
        /// them, so the agent's `build android` hits this): a test APK is debug-signed instead of failing at signing.
        /// The store AAB always keeps the release keystore.
        /// </summary>
        public static bool DebugSigns(BuildTarget target, bool appBundle, bool customKeystore, bool batch,
                                      bool passwordsTyped) =>
            target == BuildTarget.Android && !appBundle && customKeystore && (batch || !passwordsTyped);

        /// <summary>
        /// Play Console flags an AAB without native debug symbols, and IL2CPP crashes and ANRs then show up
        /// unsymbolicated in Android vitals. The store AAB carries the symbol table inside the bundle, where Play
        /// picks it up with the upload; a game that already asks for Full keeps it, and a separate zip it asked for
        /// stays too where the format is a flag set.
        /// The setting lives in the per-machine Android build settings, in the Android module's own DLL, so it is
        /// reached by reflection (a direct reference would stop this assembly compiling without that module), set for
        /// the build and put back after it.
        /// </summary>
        static class AndroidDebugSymbols
        {
            const BindingFlags Static = BindingFlags.Public | BindingFlags.Static;
            // UnityEditor.Android.UserBuildSettings.DebugSymbols (6000.6): level (Unity.Android.Types.DebugSymbolLevel:
            // None, SymbolTable, Full) and format (Unity.Android.Types.DebugSymbolFormat: Zip, IncludeInBundle, ...)
            static readonly System.Type Settings =
                System.Type.GetType("UnityEditor.Android.UserBuildSettings+DebugSymbols, UnityEditor.Android.Extensions");
            static PropertyInfo Level => Settings?.GetProperty("level", Static);
            static PropertyInfo Format => Settings?.GetProperty("format", Static);

            /// <summary>The current level and format, or null when the API is not there (no Android module).</summary>
            public static object[] Read() =>
                Level == null || Format == null ? null : new[] { Level.GetValue(null), Format.GetValue(null) };

            /// <summary>Sets the store defaults on top of <paramref name="start"/>; returns the build.log line.</summary>
            public static string ForStore(object[] start)
            {
                if (start == null) return "not set: UnityEditor.Android.UserBuildSettings.DebugSymbols not found";
                if (start[0].ToString() == "None") Level.SetValue(null, System.Enum.Parse(Level.PropertyType, "SymbolTable"));
                var format = Format.PropertyType;
                object inBundle = System.Enum.Parse(format, "IncludeInBundle");
                if (format.IsDefined(typeof(System.FlagsAttribute), false))
                    Format.SetValue(null, System.Enum.ToObject(format,
                        System.Convert.ToInt64(start[1]) | System.Convert.ToInt64(inBundle)));
                else Format.SetValue(null, inBundle);
                return Level.GetValue(null) + ", " + Format.GetValue(null);
            }

            public static void Restore(object[] start)
            {
                if (start == null) return;
                Level.SetValue(null, start[0]);
                Format.SetValue(null, start[1]);
            }
        }

        // a batch build exits right after, so switching back would only cost a reimport
        static void SwitchBack(BuildTargetGroup startGroup, BuildTarget startTarget, BuildTarget target)
        {
            if (startTarget != target && !Application.isBatchMode)
                EditorUserBuildSettings.SwitchActiveBuildTarget(startGroup, startTarget);
        }

        static string OutputPath(BuildTarget target, bool appBundle)
        {
            string product = PlayerSettings.productName;
            switch (target)
            {
                case BuildTarget.StandaloneWindows64: return "Builds/Windows/" + product + ".exe";
                case BuildTarget.Android: return "Builds/Android/" + product + (appBundle ? ".aab" : ".apk");
                case BuildTarget.iOS: return "Builds/iOS";
                case BuildTarget.WebGL: return "Builds/WebGL";
                default: return "Builds/" + target;
            }
        }

        /// <summary>
        /// The WebGL code optimization lives in the per-machine build settings (Library/, not committed), so a fresh
        /// clone would build with Unity's default; it is set on every WebGL build. Release builds get the size pass
        /// Magic Sort and Pixel Volley ship to itch.io with, dev builds the fastest build. The project-wide WebGL
        /// player settings (compression, template, stripping) are ProjectSetup's, written once, so a game's own
        /// choice there survives every build.
        /// </summary>
        static void SetWebGLCodeOptimization(bool development)
        {
            // UnityEditor.WebGL lives in the WebGL module's own DLL: a direct reference would stop this whole assembly
            // (AgentBridge included) compiling on a machine or CI image without that module
            var settings = System.Type.GetType("UnityEditor.WebGL.UserBuildSettings, UnityEditor.WebGL.Extensions");
            const BindingFlags Static = BindingFlags.Public | BindingFlags.Static;
            var property = settings?.GetProperty("codeOptimization", Static);
            var field = settings?.GetField("codeOptimization", Static);
            var type = property?.PropertyType ?? field?.FieldType;
            if (type != null)
            {
                // UnityEditor.WebGL.WasmCodeOptimization (6000.6): BuildTimes, RuntimeSpeed, RuntimeSpeedLTO, DiskSize,
                // DiskSizeLTO
                var value = System.Enum.Parse(type, development ? "BuildTimes" : "DiskSizeLTO");
                if (property != null) property.SetValue(null, value); else field.SetValue(null, value);
            }
            else Debug.LogWarning("[BuildMenu] WebGL code optimization not set: UnityEditor.WebGL.UserBuildSettings not found.");
        }

        static void Finish(BuildTarget target, string text, bool succeeded)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(LogPath));
            File.WriteAllText(LogPath, text);
            if (succeeded) Debug.Log("[BuildMenu] " + target + " build succeeded, see " + LogPath);
            else Debug.LogError("[BuildMenu] " + text);

            if (Application.isBatchMode && !succeeded) EditorApplication.Exit(1);
        }
    }
}
