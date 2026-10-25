using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace __GAME__.Editor
{
    /// <summary>
    /// One build entry per target, writing its result to Logs/agent/build.log so an agent can read it.
    /// From the menu, from AgentBridge (write "build android" into Logs/agent/request.txt), or with the Editor
    /// closed: Unity -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.BuildMenu.Android
    /// The active platform is switched back afterwards, so a build never leaves the Editor on another target.
    /// </summary>
    public static class BuildMenu
    {
        const string LogPath = "Logs/agent/build.log";

        [MenuItem("__GAME__/Build/Windows")] public static void Windows() => Build(BuildTarget.StandaloneWindows64);
        [MenuItem("__GAME__/Build/Android (APK)")] public static void Android() => Build(BuildTarget.Android);
        [MenuItem("__GAME__/Build/iOS (Xcode project)")] public static void IOS() => Build(BuildTarget.iOS);
        [MenuItem("__GAME__/Build/WebGL")] public static void WebGL() => Build(BuildTarget.WebGL);

        public static bool TryParse(string name, out BuildTarget target)
        {
            switch (name.Trim().ToLowerInvariant())
            {
                case "windows": target = BuildTarget.StandaloneWindows64; return true;
                case "android": target = BuildTarget.Android; return true;
                case "ios": target = BuildTarget.iOS; return true;
                case "webgl": target = BuildTarget.WebGL; return true;
                default: target = default; return false;
            }
        }

        public static void Build(BuildTarget target)
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

            var startTarget = EditorUserBuildSettings.activeBuildTarget;
            var startGroup = BuildPipeline.GetBuildTargetGroup(startTarget);

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes.ToArray(),
                locationPathName = OutputPath(target),
                target = target,
                targetGroup = group,
                options = BuildOptions.None,
            });

            var summary = report.summary;
            var text = new StringBuilder(1024);
            text.Append(summary.result).Append("  ").Append(target).Append("  ").Append(System.DateTime.Now.ToString("HH:mm:ss")).Append('\n');
            text.Append("output ").Append(summary.outputPath).Append('\n');
            text.Append("size ").Append((summary.totalSize / (1024f * 1024f)).ToString("0.0")).Append(" MB, time ")
                .Append(summary.totalTime.TotalSeconds.ToString("0")).Append(" s\n");
            foreach (var step in report.steps)
            foreach (var message in step.messages)
                if (message.type == LogType.Error || message.type == LogType.Exception)
                    text.Append('[').Append(step.name).Append("] ").Append(message.content).Append('\n');

            if (startTarget != target)
                EditorUserBuildSettings.SwitchActiveBuildTarget(startGroup, startTarget);

            Finish(target, text.ToString(), summary.result == BuildResult.Succeeded);
        }

        static string OutputPath(BuildTarget target)
        {
            string product = PlayerSettings.productName;
            switch (target)
            {
                case BuildTarget.StandaloneWindows64: return "Builds/Windows/" + product + ".exe";
                case BuildTarget.Android: return "Builds/Android/" + product + ".apk";
                case BuildTarget.iOS: return "Builds/iOS";
                case BuildTarget.WebGL: return "Builds/WebGL";
                default: return "Builds/" + target;
            }
        }

        /// <summary>The size pass Magic Sort and Pixel Volley ship to itch.io with.</summary>
        static void ConfigureWebGL()
        {
            // itch.io serves .unityweb files without a Content-Encoding header and gzips plain files itself
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;
            PlayerSettings.WebGL.decompressionFallback = false;
            PlayerSettings.WebGL.dataCaching = true;
            // full-window canvas, so the game fills the itch.io viewport and any iframe it is embedded in
            PlayerSettings.WebGL.template = "PROJECT:Responsive";
            // the first load is dominated by the download
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.WebGL, ManagedStrippingLevel.High);
            UnityEditor.WebGL.UserBuildSettings.codeOptimization = UnityEditor.WebGL.WasmCodeOptimization.DiskSizeLTO;

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
