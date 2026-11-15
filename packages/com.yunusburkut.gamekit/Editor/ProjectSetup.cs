using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace GameKit.Editor
{
    /// <summary>Marks a public static parameterless method that ProjectSetup.Run calls after its own steps.</summary>
    [System.AttributeUsage(System.AttributeTargets.Method)]
    public sealed class ProjectSetupStepAttribute : System.Attribute { }

    /// <summary>
    /// Configures a fresh project for PC (Windows), mobile (Android, iOS) and WebGL: a URP asset and a quality
    /// level per tier (Mobile, PC), the Input System only, linear colour, IL2CPP ARM64 on Android, Play Mode
    /// without domain or scene reload, a resizable PC window, the WebGL size pass and URP post-processing
    /// stripping, and an empty Main
    /// scene in the build. Safe to run again: the identity, the build defaults, the URP assets and the quality
    /// levels are written only the first time, so later tuning survives (a pack's
    /// [ProjectSetupStep] keeps the same promise; mobile-2d converts each renderer list and Main only once).
    /// new-game.ps1 runs it once:
    /// Unity -batchmode -quit -projectPath . -executeMethod GameKit.Editor.ProjectSetup.Run -gameCompany &lt;company&gt;
    /// </summary>
    public static class ProjectSetup
    {
        /// <summary>The game's folder, Assets/&lt;Game&gt;: the one holding Core/&lt;Game&gt;.Core.asmdef (the template layout).</summary>
        public static string Root
        {
            get
            {
                foreach (string dir in Directory.GetDirectories("Assets"))
                {
                    string game = Path.GetFileName(dir);
                    if (File.Exists(Path.Combine(dir, "Core", game + ".Core.asmdef"))) return "Assets/" + game;
                }
                throw new System.InvalidOperationException(
                    "GameKit expects the unity-game-template layout: no Assets/<Game>/Core/<Game>.Core.asmdef found.");
            }
        }

        public static string SettingsFolder => Root + "/Settings";
        public static string ScenePath => Root + "/Scenes/Main.unity";

        const int MobileLevel = 0;
        const int PcLevel = 1;

        [MenuItem("GameKit/Set Up Project")]
        public static void Run()
        {
            Directory.CreateDirectory(SettingsFolder);
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            AssetDatabase.Refresh();

            bool fresh = PlayerSettings.companyName == "DefaultCompany";
            ConfigurePlayer();
            ConfigureEditor();

            var mobile = CreatePipeline("Mobile", hdr: false, msaa: 2, shadowResolution: 1024, cascades: 1,
                                        softShadows: false, shadowDistance: 25f);
            var pc = CreatePipeline("PC", hdr: true, msaa: 4, shadowResolution: 2048, cascades: 2,
                                    softShadows: true, shadowDistance: 50f);
            ConfigureQuality(mobile, pc);
            // after ConfigureQuality: the stripping setting lives in URP's global settings, there once URP is active
            if (fresh) ConfigureBuildDefaults();

            bool mainReady = CreateMainScene();

            // packs from the template's packs\ add their own steps (mobile-2d swaps in the 2D renderer); they run last
            foreach (var step in TypeCache.GetMethodsWithAttribute<ProjectSetupStepAttribute>())
                step.Invoke(null, null);

            AssetDatabase.SaveAssets();
            if (mainReady)
                Debug.Log("[ProjectSetup] Done: Mobile and PC quality tiers, Input System only, Main scene in the build.");
            else
                Debug.LogWarning("[ProjectSetup] Done except Main: it was not created or added to the build. "
                    + "Run Set Up Project again and save the open scenes when asked.");
        }

        static void ConfigurePlayer()
        {
            // only on a fresh project: a rerun must not undo a renamed product or a store-registered bundle id
            if (PlayerSettings.companyName == "DefaultCompany")
            {
                string company = CommandLineValue("-gameCompany");
                if (company == null)
                {
                    Debug.LogWarning("[ProjectSetup] Company, product and bundle id not set: run with -gameCompany <name> "
                        + "(new-game.ps1 does) or set them in Player Settings.");
                }
                else
                {
                    string product = Path.GetFileName(Root);
                    PlayerSettings.companyName = company;
                    PlayerSettings.productName = product;

                    string id = "com." + company.ToLowerInvariant() + "." + product.ToLowerInvariant();
                    PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Standalone, id);
                    PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, id);
                    PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, id);
                }
            }

            PlayerSettings.colorSpace = ColorSpace.Linear;
            // Google Play requires 64-bit; ARMv7 only adds build time
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            // Google Play has required target API 36 since 31 Aug 2026. Auto means "the newest SDK on this machine",
            // which may be older. The requirement moves up every August: raise this line with it.
            if (PlayerSettings.Android.targetSdkVersion < AndroidSdkVersions.AndroidApiLevel36)
                PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevel36;
            // Android 16 ignores the orientation lock on tablets and foldables unless the app says it is a game
            PlayerSettings.Android.appCategory = "game";
            PlayerSettings.SplashScreen.show = false;

            // 1 = Input System only. No public setter; Unity reads it at startup, so it takes effect on the
            // next Editor launch.
            var player = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            Set(player, "activeInputHandler", p => p.intValue = 1);
            player.ApplyModifiedPropertiesWithoutUndo();

            // Feel writes this define only for the target active when the Editor loads; without it on Android and
            // iOS every MMF_NV haptic feedback is stripped from the phone build
            if (Directory.Exists("Assets/Feel/NiceVibrations"))
                foreach (var target in new[] { NamedBuildTarget.Standalone, NamedBuildTarget.Android, NamedBuildTarget.iOS, NamedBuildTarget.WebGL })
                    AddDefine(target, "MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED");
        }

        /// <summary>
        /// Project-wide build settings, written on a fresh project only, so a game that changes one later (a host
        /// without Content-Encoding headers, a lower stripping level after a reflection crash) keeps its choice.
        /// The WebGL part is the size pass Magic Sort and Pixel Volley ship to itch.io with; BuildMenu sets the
        /// per-machine WebGL code optimization on each build.
        /// </summary>
        static void ConfigureBuildDefaults()
        {
            // itch.io serves .br files with Content-Encoding: br, so the browser decompresses them natively and no
            // JavaScript decompressor ships. A host that does not set that header needs decompressionFallback = true.
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
            PlayerSettings.WebGL.decompressionFallback = false;
            PlayerSettings.WebGL.dataCaching = true;
            // full-window canvas, so the game fills the itch.io viewport and any iframe it is embedded in
            PlayerSettings.WebGL.template = "PROJECT:Responsive";
            // the first load is dominated by the download. Code reached only by reflection needs a link.xml entry.
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.WebGL, ManagedStrippingLevel.High);

            // PC: a resizable window in the phone's orientation, so the desktop build shows the same framing as the
            // phone and the player can resize it (Unity's default opens full screen at the desktop resolution).
            // Written once from the orientation set at this point; a game that locks another orientation later sets
            // these two sizes with it (platform-targets).
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.resizableWindow = true;
            bool portrait = PlayerSettings.defaultInterfaceOrientation == UIOrientation.Portrait
                         || PlayerSettings.defaultInterfaceOrientation == UIOrientation.PortraitUpsideDown;
            PlayerSettings.defaultScreenWidth = portrait ? 540 : 1280;
            PlayerSettings.defaultScreenHeight = portrait ? 960 : 720;

            // Every target, so builds of one commit match whichever target was built first. URP keeps the post
            // effects some VolumeProfile asset in the project uses (scenes are not scanned): an override added only
            // from code needs a profile asset that holds it, or this setting turned off.
            if (GraphicsSettings.TryGetRenderPipelineSettings<URPShaderStrippingSetting>(out var stripping))
                stripping.stripUnusedPostProcessingVariants = true;
            else
                Debug.LogWarning("[ProjectSetup] URP shader stripping settings not found: unused post-processing "
                    + "variants are kept (Project Settings > Graphics > URP > Strip Unused Post Processing Variants).");
        }

        static string CommandLineValue(string name)
        {
            string[] args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, name);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : null;
        }

        /// <summary>Adds a scripting define for one target, once. Packs call it from their own setup steps.</summary>
        public static void AddDefine(NamedBuildTarget target, string define)
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
                                            ScriptableObject.CreateInstance<UniversalRendererData>, out _);
            // without the post-process data the renderer skips every Volume effect, bloom included
            if (rendererData.postProcessData == null)
            {
                rendererData.postProcessData = AssetDatabase.LoadAssetAtPath<PostProcessData>(
                    "Packages/com.unity.render-pipelines.universal/Runtime/Data/PostProcessData.asset");
                EditorUtility.SetDirty(rendererData);
            }

            var pipeline = LoadOrCreate(SettingsFolder + "/URP_" + tier + ".asset",
                                        () => UniversalRenderPipelineAsset.Create(rendererData), out bool created);
            if (!created) return pipeline; // the tier is the game's to tune from here on

            pipeline.supportsHDR = hdr;
            pipeline.msaaSampleCount = msaa;
            pipeline.shadowDistance = shadowDistance;
            pipeline.shadowCascadeCount = cascades;

            // the shadow resolution and soft shadows have no public setters
            var serialized = new SerializedObject(pipeline);
            Set(serialized, "m_MainLightShadowmapResolution", p => p.intValue = shadowResolution);
            Set(serialized, "m_SoftShadowsSupported", p => p.boolValue = softShadows);
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(pipeline);
            return pipeline;
        }

        /// <summary>
        /// Two quality levels, Mobile (0) and PC (1), each pointing at its URP asset. Phones and WebGL default
        /// to Mobile, desktop to PC. A game that wants more tiers adds them here, not by hand.
        /// Written once: a project whose level 0 is already "Mobile" keeps its own tuning, except a pipeline
        /// reference left empty (a deleted URP asset that the rerun created again) is pointed at the tier's asset.
        /// </summary>
        static void ConfigureQuality(UniversalRenderPipelineAsset mobile, UniversalRenderPipelineAsset pc)
        {
            var quality = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/QualitySettings.asset")[0]);
            var levels = quality.FindProperty("m_QualitySettings");
            if (levels.arraySize > 0 && levels.GetArrayElementAtIndex(MobileLevel).FindPropertyRelative("name").stringValue == "Mobile")
            {
                // without these the game silently falls back to the Built-in pipeline (pink materials)
                if (GraphicsSettings.defaultRenderPipeline == null) GraphicsSettings.defaultRenderPipeline = pc;
                RepointIfEmpty(levels.GetArrayElementAtIndex(MobileLevel), mobile);
                if (levels.arraySize > PcLevel) RepointIfEmpty(levels.GetArrayElementAtIndex(PcLevel), pc);
                quality.ApplyModifiedPropertiesWithoutUndo();
                return;
            }

            GraphicsSettings.defaultRenderPipeline = pc;

            // Unity's defaults start at "Very Low" and "Low"; every field that matters is written below, so what
            // those levels carried (half-resolution textures, lodBias 0.3) does not leak into the tiers
            while (levels.arraySize < 2) levels.InsertArrayElementAtIndex(levels.arraySize);
            while (levels.arraySize > 2) levels.DeleteArrayElementAtIndex(levels.arraySize - 1);

            var level = levels.GetArrayElementAtIndex(MobileLevel);
            SetLevel(level, "Mobile", mobile, vSyncCount: 0, skinWeights: 2, lodBias: 1f, anisotropic: 0,
                     reflectionProbes: false, raycastBudget: 64);
            level = levels.GetArrayElementAtIndex(PcLevel);
            SetLevel(level, "PC", pc, vSyncCount: 1, skinWeights: 4, lodBias: 1.5f, anisotropic: 1,
                     reflectionProbes: true, raycastBudget: 256);
            quality.FindProperty("m_CurrentQuality").intValue = PcLevel;

            var perPlatform = quality.FindProperty("m_PerPlatformDefaultQuality");
            if (perPlatform == null) Debug.LogWarning("[ProjectSetup] m_PerPlatformDefaultQuality not found: set each "
                + "platform's default quality level by hand (Project Settings > Quality).");
            else
            for (int i = 0; i < perPlatform.arraySize; i++)
            {
                var entry = perPlatform.GetArrayElementAtIndex(i);
                string platform = entry.FindPropertyRelative("first").stringValue;
                bool desktop = platform == "Standalone" || platform == "Server";
                entry.FindPropertyRelative("second").intValue = desktop ? PcLevel : MobileLevel;
            }

            quality.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetLevel(SerializedProperty level, string name, RenderPipelineAsset pipeline, int vSyncCount,
                             int skinWeights, float lodBias, int anisotropic, bool reflectionProbes, int raycastBudget)
        {
            Set(level, "name", p => p.stringValue = name);
            Set(level, "customRenderPipeline", p => p.objectReferenceValue = pipeline);
            // ignored on phones, which run at Application.targetFrameRate (AppStartup)
            Set(level, "vSyncCount", p => p.intValue = vSyncCount);
            Set(level, "globalTextureMipmapLimit", p => p.intValue = 0); // full-resolution textures
            Set(level, "skinWeights", p => p.intValue = skinWeights);
            Set(level, "lodBias", p => p.floatValue = lodBias);
            Set(level, "anisotropicTextures", p => p.intValue = anisotropic);
            Set(level, "realtimeReflectionProbes", p => p.boolValue = reflectionProbes);
            Set(level, "particleRaycastBudget", p => p.intValue = raycastBudget);
            Set(level, "enableLODCrossFade", p => p.boolValue = true);
        }

        static void RepointIfEmpty(SerializedProperty level, RenderPipelineAsset pipeline)
        {
            var reference = level.FindPropertyRelative("customRenderPipeline");
            if (reference != null && reference.objectReferenceValue == null) reference.objectReferenceValue = pipeline;
        }

        // A Unity or URP update can rename a serialized field. Warn and go on, so one renamed field does not stop the
        // setup halfway with the rest of the tier unwritten.
        static void Set(SerializedObject owner, string name, System.Action<SerializedProperty> write) =>
            Write(owner.FindProperty(name), name, write);

        static void Set(SerializedProperty owner, string name, System.Action<SerializedProperty> write) =>
            Write(owner.FindPropertyRelative(name), name, write);

        static void Write(SerializedProperty property, string name, System.Action<SerializedProperty> write)
        {
            if (property != null) write(property);
            else Debug.LogWarning("[ProjectSetup] serialized field " + name + " not found (renamed by a Unity or URP "
                + "update?): set it by hand and update ProjectSetup.");
        }

        /// <summary>Call before replacing the open scenes: asks to save unsaved edits (no dialog in batch mode).
        /// False means the user cancelled.</summary>
        public static bool SaveOpenScenesFirst() =>
            Application.isBatchMode || EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo();

        /// <summary>False when the user cancelled the save prompt, so Main is neither created nor in the build.</summary>
        static bool CreateMainScene()
        {
            if (!File.Exists(ScenePath))
            {
                if (!SaveOpenScenesFirst()) return false;
                var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }

            foreach (var entry in EditorBuildSettings.scenes)
                if (entry.path == ScenePath) return true;

            var scenes = new EditorBuildSettingsScene[EditorBuildSettings.scenes.Length + 1];
            scenes[0] = new EditorBuildSettingsScene(ScenePath, true);
            EditorBuildSettings.scenes.CopyTo(scenes, 1);
            EditorBuildSettings.scenes = scenes;
            return true;
        }

        static T LoadOrCreate<T>(string path, System.Func<T> create, out bool created) where T : Object
        {
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            created = asset == null;
            if (!created) return asset;

            asset = create();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }
    }
}
