using NUnit.Framework;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace GameKit.Editor.Tests
{
    public class BuildMenuTests
    {
        [TestCase("windows", BuildTarget.StandaloneWindows64, false)]
        [TestCase("android", BuildTarget.Android, false)]
        [TestCase("aab", BuildTarget.Android, true)]
        [TestCase("ios", BuildTarget.iOS, false)]
        [TestCase("webgl", BuildTarget.WebGL, false)]
        [TestCase("  WebGL ", BuildTarget.WebGL, false)]
        public void TryParse_KnownName(string name, BuildTarget expected, bool expectedBundle)
        {
            Assert.IsTrue(BuildMenu.TryParse(name, out var target, out bool appBundle));
            Assert.AreEqual(expected, target);
            Assert.AreEqual(expectedBundle, appBundle);
        }

        [TestCase("")]
        [TestCase("linux")]
        [TestCase("apk")]
        public void TryParse_UnknownName(string name)
        {
            Assert.IsFalse(BuildMenu.TryParse(name, out _, out bool appBundle));
            Assert.IsFalse(appBundle);
        }

        // target, appBundle, customKeystore, batch, passwordsTyped -> debug-signed
        [TestCase(BuildTarget.Android, false, true, true, true, true)]     // CI: no passwords in a batch run
        [TestCase(BuildTarget.Android, false, true, false, false, true)]   // Editor session, passwords not typed
        [TestCase(BuildTarget.Android, false, true, false, true, false)]   // passwords typed: the release keystore
        [TestCase(BuildTarget.Android, false, false, true, false, false)]  // no keystore set: already debug-signed
        [TestCase(BuildTarget.Android, true, true, true, false, false)]    // the store AAB never falls back
        [TestCase(BuildTarget.Android, true, true, false, false, false)]
        [TestCase(BuildTarget.iOS, false, true, true, false, false)]
        public void DebugSigns(BuildTarget target, bool appBundle, bool customKeystore, bool batch, bool typed, bool expected) =>
            Assert.AreEqual(expected, BuildMenu.DebugSigns(target, appBundle, customKeystore, batch, typed));

        [Test]
        public void TargetNames_AllParse()
        {
            foreach (string name in BuildMenu.TargetNames.Split('|'))
                Assert.IsTrue(BuildMenu.TryParse(name, out _, out _), name);
        }

        // the type string and enum member names are reflection: a Unity API move shows up here, not as a Play warning
        [Test]
        public void AndroidDebugSymbols_StoreSettingsRoundTrip()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android, BuildTarget.Android))
            {
                StringAssert.StartsWith("not set", BuildMenu.AndroidDebugSymbols.ForStore(null));
                Assert.Ignore("Android module not installed");
            }
            var start = BuildMenu.AndroidDebugSymbols.Read();
            Assert.IsNotNull(start, "UnityEditor.Android.UserBuildSettings.DebugSymbols not found");
            try
            {
                string line = BuildMenu.AndroidDebugSymbols.ForStore(start);
                StringAssert.DoesNotStartWith("not set", line);
                StringAssert.Contains("IncludeInBundle", line);
                StringAssert.DoesNotStartWith("None", line);
            }
            finally
            {
                BuildMenu.AndroidDebugSymbols.Restore(start);
            }
            var restored = BuildMenu.AndroidDebugSymbols.Read();
            Assert.AreEqual(start[0], restored[0]);
            Assert.AreEqual(start[1], restored[1]);
        }
    }

    public class SafeAreaFitterTests
    {
        [Test]
        public void Anchors_FullScreen_IsUnit()
        {
            var a = SafeAreaFitter.Anchors(new Rect(0, 0, 1080, 1920), new Rect(0, 0, 1080, 1920));
            Assert.AreEqual(Vector2.zero, a.min);
            Assert.AreEqual(Vector2.one, a.max);
        }

        [Test]
        public void Anchors_NotchAndHomeIndicator()
        {
            // portrait phone: 132 px notch at the top, 102 px home indicator at the bottom
            var a = SafeAreaFitter.Anchors(new Rect(0, 102, 1170, 2532 - 132 - 102), new Rect(0, 0, 1170, 2532));
            Assert.AreEqual(0f, a.xMin, 1e-6f);
            Assert.AreEqual(1f, a.xMax, 1e-6f);
            Assert.AreEqual(102f / 2532f, a.yMin, 1e-6f);
            Assert.AreEqual((2532f - 132f) / 2532f, a.yMax, 1e-6f);
        }

        [Test]
        public void Anchors_LetterboxedCamera_IgnoresInsetInsideTheBars()
        {
            // landscape phone 2532 x 1170: 132 px notch left and right, 63 px bottom inset; 16:9 camera pillarboxed to 2080 px at x 226
            var a = SafeAreaFitter.Anchors(Rect.MinMaxRect(132, 63, 2532 - 132, 1170), new Rect(226, 0, 2080, 1170));
            Assert.AreEqual(0f, a.xMin, 1e-6f);
            Assert.AreEqual(1f, a.xMax, 1e-6f);
            Assert.AreEqual(63f / 1170f, a.yMin, 1e-6f);
            Assert.AreEqual(1f, a.yMax, 1e-6f);
        }
    }

    public class FrameLogTests
    {
        static float P99(float[] ring, int next, int count) => FrameLog.P99(ring, next, count, new float[ring.Length]);

        [Test]
        public void P99_Empty_IsZero() => Assert.AreEqual(0f, P99(new float[8], 0, 0));

        [Test]
        public void P99_OneFrame_IsThatFrame() => Assert.AreEqual(7f, P99(new[] { 99f, 7f, 99f, 99f }, 2, 1));

        [Test]
        public void P99_NoWrap_ReadsOnlyTheNewestFrames()
        {
            // 1..10 just written at 0..9; the 99 after them is older data outside the window
            var ring = new float[16];
            for (int i = 0; i < ring.Length; i++) ring[i] = i < 10 ? i + 1 : 99f;
            Assert.AreEqual(10f, P99(ring, 10, 10)); // n = 10: index min(9, 9)
            Assert.AreEqual(5f, P99(ring, 5, 5));
        }

        [Test]
        public void P99_Wrapped_TakesBothEnds()
        {
            // newest 6 frames at 5, 6, 7, 0, 1, 2; slots 3 and 4 hold older frames that must not count
            var ring = new[] { 4f, 5f, 6f, 500f, 500f, 1f, 2f, 3f };
            Assert.AreEqual(6f, P99(ring, 3, 6));
        }

        [Test]
        public void P99_Full_IsTheSecondWorstOf200()
        {
            // 200 frames 1..200 written starting at slot 50, so the ring wraps; index (int)(200 * 0.99) = 198
            var ring = new float[200];
            for (int i = 0; i < 200; i++) ring[(50 + i) % 200] = i + 1;
            Assert.AreEqual(199f, P99(ring, 50, 200));
            Assert.AreEqual(199f, P99(ring, 50, 4096)); // a count over the capacity is the whole ring
        }
    }

    public class ProjectSetupTests
    {
        const string Define = "GAMEKIT_TEST_DEFINE";

        [Test]
        public void AddDefine_AddsOnce_KeepsOthers()
        {
            // a target that is not active, so changing its defines starts no recompile
            var active = NamedBuildTarget.FromBuildTargetGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
            var target = active == NamedBuildTarget.iOS ? NamedBuildTarget.Android : NamedBuildTarget.iOS;
            string original = PlayerSettings.GetScriptingDefineSymbols(target);
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(target, "A;B");
                ProjectSetup.AddDefine(target, Define);
                ProjectSetup.AddDefine(target, Define);
                Assert.AreEqual("A;B;" + Define, PlayerSettings.GetScriptingDefineSymbols(target));

                PlayerSettings.SetScriptingDefineSymbols(target, "");
                ProjectSetup.AddDefine(target, Define);
                Assert.AreEqual(Define, PlayerSettings.GetScriptingDefineSymbols(target));
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(target, original);
            }
        }

        /// <summary>
        /// Runs Set Up Project again on this project, as a user would from the menu, and checks the promise in
        /// ProjectSetup's summary: the tiers and the URP assets the first run wrote are left as they were.
        /// </summary>
        [Test]
        public void Rerun_KeepsTiersAndUrpAssets()
        {
            string folder = ProjectSetup.SettingsFolder;
            var mobile = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(folder + "/URP_Mobile.asset");
            var pc = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(folder + "/URP_PC.asset");
            if (mobile == null || pc == null) Assert.Ignore("Set Up Project has not run on this project yet.");

            string[] levelsBefore = QualitySettings.names;
            object[] mobileBefore = Shadows(mobile);
            object[] pcBefore = Shadows(pc);

            ProjectSetup.Run();

            Assert.AreEqual(0, ProjectSetup.Warnings, "Set Up Project skipped settings: see its warnings in the Console");
            CollectionAssert.AreEqual(levelsBefore, QualitySettings.names);
            Assert.AreEqual("Mobile", QualitySettings.names[0]);
            Assert.AreEqual("PC", QualitySettings.names[1]);
            CollectionAssert.AreEqual(mobileBefore, Shadows(mobile));
            CollectionAssert.AreEqual(pcBefore, Shadows(pc));
            Assert.IsNotNull(GraphicsSettings.defaultRenderPipeline);

            foreach (string tier in new[] { "Mobile", "PC" })
            {
                var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(folder + "/URP_" + tier + "_Renderer.asset");
                Assert.IsNotNull(renderer, tier + " renderer");
                Assert.IsNotNull(renderer.postProcessData, tier + " renderer has no post-process data: Volume effects are skipped");
            }
        }

        /// <summary>
        /// What the first run writes, read back on the game test-template.ps1 just made (GameKit's tests run only
        /// there): a field a Unity or URP update renamed shows up here, not as a silently degraded new game.
        /// </summary>
        [Test]
        public void FirstRun_WroteTheDefaults()
        {
            string folder = ProjectSetup.SettingsFolder;
            var mobile = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(folder + "/URP_Mobile.asset");
            var pc = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(folder + "/URP_PC.asset");
            if (mobile == null || pc == null) Assert.Ignore("Set Up Project has not run on this project yet.");

            Assert.AreEqual(WebGLCompressionFormat.Brotli, PlayerSettings.WebGL.compressionFormat);
            Assert.AreEqual("PROJECT:Responsive", PlayerSettings.WebGL.template);
            Assert.AreEqual(ManagedStrippingLevel.High, PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.WebGL));
            Assert.AreEqual(FullScreenMode.Windowed, PlayerSettings.fullScreenMode);
            Assert.IsTrue(PlayerSettings.resizableWindow);
            Assert.IsTrue(GraphicsSettings.TryGetRenderPipelineSettings<URPShaderStrippingSetting>(out var stripping),
                "URP shader stripping settings not found");
            Assert.IsTrue(stripping.stripUnusedPostProcessingVariants);

            var player = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            Assert.AreEqual(1, player.FindProperty("activeInputHandler")?.intValue, "Input System only");

            // ConfigurePlayer and ConfigureEditor: what Google Play requires and the fast Play Mode
            Assert.AreEqual(ColorSpace.Linear, PlayerSettings.colorSpace);
            Assert.AreEqual(ScriptingImplementation.IL2CPP, PlayerSettings.GetScriptingBackend(NamedBuildTarget.Android));
            Assert.AreEqual(AndroidArchitecture.ARM64, PlayerSettings.Android.targetArchitectures);
            Assert.GreaterOrEqual((int)PlayerSettings.Android.targetSdkVersion, (int)AndroidSdkVersions.AndroidApiLevel36);
            Assert.AreEqual("game", PlayerSettings.Android.appCategory);
            Assert.IsTrue(EditorSettings.enterPlayModeOptionsEnabled);
            Assert.AreEqual(EnterPlayModeOptions.DisableDomainReload | EnterPlayModeOptions.DisableSceneReload,
                EditorSettings.enterPlayModeOptions);
            // test-template.ps1 makes its game through new-game.ps1, which passes -gameCompany
            if (PlayerSettings.companyName != "DefaultCompany")
            {
                string id = "com." + PlayerSettings.companyName.ToLowerInvariant() + "." + PlayerSettings.productName.ToLowerInvariant();
                Assert.AreEqual(id, PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.Android));
                Assert.AreEqual(id, PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.iOS));
                Assert.AreEqual(id, PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.Standalone));
            }
            Assert.IsNotEmpty(EditorBuildSettings.scenes, "no scene in the build");
            Assert.AreEqual(ProjectSetup.ScenePath, EditorBuildSettings.scenes[0].path, "Main is not the first build scene");

            Assert.AreEqual(1024, mobile.mainLightShadowmapResolution);
            Assert.AreEqual(2048, pc.mainLightShadowmapResolution);
            Assert.IsFalse(mobile.supportsSoftShadows);
            Assert.IsTrue(pc.supportsSoftShadows);

            var quality = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/QualitySettings.asset")[0]);
            var levels = quality.FindProperty("m_QualitySettings");
            Assert.AreEqual(2, levels.arraySize, "quality levels");
            var mobileLevel = levels.GetArrayElementAtIndex(0);
            var pcLevel = levels.GetArrayElementAtIndex(1);
            Assert.AreEqual(0, mobileLevel.FindPropertyRelative("vSyncCount")?.intValue, "Mobile vSyncCount");
            Assert.AreEqual(1, pcLevel.FindPropertyRelative("vSyncCount")?.intValue, "PC vSyncCount");
            Assert.AreEqual(1f, mobileLevel.FindPropertyRelative("lodBias")?.floatValue, "Mobile lodBias");
            Assert.AreEqual(1.5f, pcLevel.FindPropertyRelative("lodBias")?.floatValue, "PC lodBias");
            Assert.AreEqual(mobile, mobileLevel.FindPropertyRelative("customRenderPipeline")?.objectReferenceValue, "Mobile pipeline");
            Assert.AreEqual(pc, pcLevel.FindPropertyRelative("customRenderPipeline")?.objectReferenceValue, "PC pipeline");

            var perPlatform = quality.FindProperty("m_PerPlatformDefaultQuality");
            Assert.IsNotNull(perPlatform, "m_PerPlatformDefaultQuality");
            // Unity lists only some platforms (a project made on 6000.6 had no WebGL or iPhone entry), so each entry
            // that is there is checked: desktop on PC (1), everything else on Mobile (0)
            bool sawStandalone = false;
            for (int i = 0; i < perPlatform.arraySize; i++)
            {
                var entry = perPlatform.GetArrayElementAtIndex(i);
                string platform = entry.FindPropertyRelative("first").stringValue;
                bool desktop = platform == "Standalone" || platform == "Server";
                sawStandalone |= platform == "Standalone";
                Assert.AreEqual(desktop ? 1 : 0, entry.FindPropertyRelative("second").intValue, platform);
            }
            Assert.IsTrue(sawStandalone, "no Standalone entry in the per-platform default quality");
        }

        static object[] Shadows(UniversalRenderPipelineAsset pipeline)
        {
            var serialized = new SerializedObject(pipeline);
            return new object[]
            {
                pipeline.shadowDistance, pipeline.shadowCascadeCount, pipeline.msaaSampleCount, pipeline.supportsHDR,
                serialized.FindProperty("m_MainLightShadowmapResolution")?.intValue,
                serialized.FindProperty("m_SoftShadowsSupported")?.boolValue,
            };
        }
    }
}
