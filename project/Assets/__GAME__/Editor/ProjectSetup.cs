using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace __GAME__.Editor
{
    /// <summary>
    /// Configures a fresh project for PC (Windows), mobile (Android, iOS) and WebGL: a URP asset and a quality
    /// level per tier (Mobile, PC), the Input System only, linear colour, IL2CPP ARM64 on Android, Play Mode
    /// without domain or scene reload, and an empty Main scene in the build. Safe to run again; it reuses what
    /// is already there and does not touch the game's own content.
    /// new-game.ps1 runs it once:
    /// Unity -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.ProjectSetup.Run
    /// </summary>
    public static class ProjectSetup
    {
        const string Root = "Assets/__GAME__";
        const string SettingsFolder = Root + "/Settings";
        const string ScenePath = Root + "/Scenes/Main.unity";
        const string CompanyName = "__COMPANY__";
        const string ProductName = "__GAME__";

        const int MobileLevel = 0;
        const int PcLevel = 1;

        [MenuItem("__GAME__/Set Up Project")]
        public static void Run()
        {
            Directory.CreateDirectory(SettingsFolder);
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            AssetDatabase.Refresh();

            ConfigurePlayer();
            ConfigureEditor();

            var mobile = CreatePipeline("Mobile", hdr: false, msaa: 2, shadowResolution: 1024, cascades: 1,
                                        softShadows: false, shadowDistance: 25f);
            var pc = CreatePipeline("PC", hdr: true, msaa: 4, shadowResolution: 2048, cascades: 2,
                                    softShadows: true, shadowDistance: 50f);
            ConfigureQuality(mobile, pc);

            CreateMainScene();
            AssetDatabase.SaveAssets();
            Debug.Log("[ProjectSetup] Done: Mobile and PC quality tiers, Input System only, Main scene in the build.");
        }

        static void ConfigurePlayer()
        {
            PlayerSettings.companyName = CompanyName;
            PlayerSettings.productName = ProductName;

            string id = "com." + CompanyName.ToLowerInvariant() + "." + ProductName.ToLowerInvariant();
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Standalone, id);
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, id);
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, id);

            PlayerSettings.colorSpace = ColorSpace.Linear;
            // Google Play requires 64-bit; ARMv7 only adds build time
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.SplashScreen.show = false;

            // 1 = Input System only. No public setter; Unity reads it at startup, so it takes effect on the
            // next Editor launch.
            var player = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            player.FindProperty("activeInputHandler").intValue = 1;
            player.ApplyModifiedPropertiesWithoutUndo();

            // Feel writes this define only for the target active when the Editor loads; without it on Android and
            // iOS every MMF_NV haptic feedback is stripped from the phone build
            if (Directory.Exists("Assets/Feel/NiceVibrations"))
                foreach (var target in new[] { NamedBuildTarget.Standalone, NamedBuildTarget.Android, NamedBuildTarget.iOS, NamedBuildTarget.WebGL })
                    AddDefine(target, "MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED");
        }

        static void AddDefine(NamedBuildTarget target, string define)
        {
            string defines = PlayerSettings.GetScriptingDefineSymbols(target);
            if (System.Array.IndexOf(defines.Split(';'), define) >= 0) return;
            PlayerSettings.SetScriptingDefineSymbols(target, defines.Length == 0 ? define : defines + ";" + define);
        }

        static void ConfigureEditor()
        {
            // Fast iteration: every mutable static needs a SubsystemRegistration reset (see CLAUDE.md)
            EditorSettings.enterPlayModeOptionsEnabled = true;
            EditorSettings.enterPlayModeOptions =
                EnterPlayModeOptions.DisableDomainReload | EnterPlayModeOptions.DisableSceneReload;
        }

        static UniversalRenderPipelineAsset CreatePipeline(string tier, bool hdr, int msaa, int shadowResolution,
                                                           int cascades, bool softShadows, float shadowDistance)
        {
            var rendererData = LoadOrCreate(SettingsFolder + "/URP_" + tier + "_Renderer.asset",
                                            ScriptableObject.CreateInstance<UniversalRendererData>);
            // without the post-process data the renderer skips every Volume effect, bloom included
            rendererData.postProcessData = AssetDatabase.LoadAssetAtPath<PostProcessData>(
                "Packages/com.unity.render-pipelines.universal/Runtime/Data/PostProcessData.asset");
            EditorUtility.SetDirty(rendererData);

            var pipeline = LoadOrCreate(SettingsFolder + "/URP_" + tier + ".asset",
                                        () => UniversalRenderPipelineAsset.Create(rendererData));
            pipeline.supportsHDR = hdr;
            pipeline.msaaSampleCount = msaa;
            pipeline.shadowDistance = shadowDistance;
            pipeline.shadowCascadeCount = cascades;

            // the shadow resolution and soft shadows have no public setters
            var serialized = new SerializedObject(pipeline);
            serialized.FindProperty("m_MainLightShadowmapResolution").intValue = shadowResolution;
            serialized.FindProperty("m_SoftShadowsSupported").boolValue = softShadows;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(pipeline);
            return pipeline;
        }

        /// <summary>
        /// Two quality levels, Mobile (0) and PC (1), each pointing at its URP asset. Phones and WebGL default
        /// to Mobile, desktop to PC. A game that wants more tiers adds them here, not by hand.
        /// </summary>
        static void ConfigureQuality(UniversalRenderPipelineAsset mobile, UniversalRenderPipelineAsset pc)
        {
            GraphicsSettings.defaultRenderPipeline = pc;

            var quality = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/QualitySettings.asset")[0]);
            var levels = quality.FindProperty("m_QualitySettings");
            // the inserted element copies the one before it, so every field we do not set keeps a sane value
            while (levels.arraySize < 2) levels.InsertArrayElementAtIndex(levels.arraySize);
            while (levels.arraySize > 2) levels.DeleteArrayElementAtIndex(levels.arraySize - 1);

            SetLevel(levels.GetArrayElementAtIndex(MobileLevel), "Mobile", mobile, vSyncCount: 0);
            SetLevel(levels.GetArrayElementAtIndex(PcLevel), "PC", pc, vSyncCount: 1);
            quality.FindProperty("m_CurrentQuality").intValue = PcLevel;

            var perPlatform = quality.FindProperty("m_PerPlatformDefaultQuality");
            for (int i = 0; i < perPlatform.arraySize; i++)
            {
                var entry = perPlatform.GetArrayElementAtIndex(i);
                string platform = entry.FindPropertyRelative("first").stringValue;
                bool desktop = platform == "Standalone" || platform == "Server";
                entry.FindPropertyRelative("second").intValue = desktop ? PcLevel : MobileLevel;
            }

            quality.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetLevel(SerializedProperty level, string name, RenderPipelineAsset pipeline, int vSyncCount)
        {
            level.FindPropertyRelative("name").stringValue = name;
            level.FindPropertyRelative("customRenderPipeline").objectReferenceValue = pipeline;
            // ignored on phones, which run at Application.targetFrameRate (AppStartup)
            level.FindPropertyRelative("vSyncCount").intValue = vSyncCount;
        }

        static void CreateMainScene()
        {
            if (!File.Exists(ScenePath))
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }

            foreach (var entry in EditorBuildSettings.scenes)
                if (entry.path == ScenePath) return;

            var scenes = new EditorBuildSettingsScene[EditorBuildSettings.scenes.Length + 1];
            scenes[0] = new EditorBuildSettingsScene(ScenePath, true);
            EditorBuildSettings.scenes.CopyTo(scenes, 1);
            EditorBuildSettings.scenes = scenes;
        }

        static T LoadOrCreate<T>(string path, System.Func<T> create) where T : Object
        {
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null) return asset;

            asset = create();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }
    }
}
