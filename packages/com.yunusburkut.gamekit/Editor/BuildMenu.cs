using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

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

            if (target == BuildTarget.WebGL) ConfigureWebGL();
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
            development |= EditorUserBuildSettings.development;

            BuildReport report;
            try
            {
                if (target == BuildTarget.Android) EditorUserBuildSettings.buildAppBundle = appBundle;
                // a batch run (CI) has no keystore passwords, so a test APK is debug-signed instead of failing; the
                // store AAB keeps the release keystore
                if (target == BuildTarget.Android && !appBundle && Application.isBatchMode)
                    PlayerSettings.Android.useCustomKeystore = false;
                report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = scenes.ToArray(),
                    locationPathName = OutputPath(target, appBundle),
                    target = target,
                    targetGroup = group,
                    options = development ? BuildOptions.Development | BuildOptions.ConnectWithProfiler : BuildOptions.None,
                });
            }
            finally
            {
                EditorUserBuildSettings.buildAppBundle = startAppBundle;
                PlayerSettings.Android.useCustomKeystore = startCustomKeystore;
            }

            var summary = report.summary;
            var text = new StringBuilder(1024);
            text.Append(summary.result).Append("  ").Append(target).Append(appBundle ? " (AAB)" : "").Append("  ")
                .Append(AgentBridge.Timestamp()).Append('\n');
            text.Append("output ").Append(summary.outputPath).Append('\n');
            text.Append("development ").Append(development ? "yes" : "no").Append('\n');
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
            }
            foreach (var step in report.steps)
            foreach (var message in step.messages)
                // Play blocks updates with a 4 KB-aligned native plug-in from 1 Feb 2027, and Unity only warns about it
                if (message.type == LogType.Error || message.type == LogType.Exception ||
                    (message.type == LogType.Warning && message.content.IndexOf("16 KB", System.StringComparison.OrdinalIgnoreCase) >= 0))
                    text.Append('[').Append(step.name).Append("] ").Append(message.content).Append('\n');

            // a batch build exits right after, so switching back would only cost a reimport
            if (startTarget != target && !Application.isBatchMode)
                EditorUserBuildSettings.SwitchActiveBuildTarget(startGroup, startTarget);

            Finish(target, text.ToString(), summary.result == BuildResult.Succeeded);
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

        /// <summary>The size pass Magic Sort and Pixel Volley ship to itch.io with.</summary>
        static void ConfigureWebGL()
        {
            // itch.io serves .br files with Content-Encoding: br, so the browser decompresses them natively and no
            // JavaScript decompressor ships. A host that does not set that header needs decompressionFallback = true.
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
            PlayerSettings.WebGL.decompressionFallback = false;
            PlayerSettings.WebGL.dataCaching = true;
            // full-window canvas, so the game fills the itch.io viewport and any iframe it is embedded in
            PlayerSettings.WebGL.template = "PROJECT:Responsive";
            // the first load is dominated by the download
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.WebGL, ManagedStrippingLevel.High);
            // UnityEditor.WebGL lives in the WebGL module's own DLL: a direct reference would stop this whole assembly
            // (AgentBridge included) compiling on a machine or CI image without that module
            var settings = System.Type.GetType("UnityEditor.WebGL.UserBuildSettings, UnityEditor.WebGL.Extensions");
            const BindingFlags Static = BindingFlags.Public | BindingFlags.Static;
            var property = settings?.GetProperty("codeOptimization", Static);
            var field = settings?.GetField("codeOptimization", Static);
            var type = property?.PropertyType ?? field?.FieldType;
            if (type != null)
            {
                var value = System.Enum.Parse(type, "DiskSizeLTO");
                if (property != null) property.SetValue(null, value); else field.SetValue(null, value);
            }
            else Debug.LogWarning("[BuildMenu] WebGL code optimization not set: UnityEditor.WebGL.UserBuildSettings not found.");

            var stripping = GraphicsSettings.GetRenderPipelineSettings<URPShaderStrippingSetting>();
            stripping.stripUnusedPostProcessingVariants = true;
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
