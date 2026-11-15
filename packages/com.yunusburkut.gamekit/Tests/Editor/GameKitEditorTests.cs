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

        [Test]
        public void TargetNames_AllParse()
        {
            foreach (string name in BuildMenu.TargetNames.Split('|'))
                Assert.IsTrue(BuildMenu.TryParse(name, out _, out _), name);
        }
    }

    public class SafeAreaFitterTests
    {
        [Test]
        public void Anchors_FullScreen_IsUnit()
        {
            var a = SafeAreaFitter.Anchors(new Rect(0, 0, 1080, 1920), 1080, 1920);
            Assert.AreEqual(Vector2.zero, a.min);
            Assert.AreEqual(Vector2.one, a.max);
        }

        [Test]
        public void Anchors_NotchAndHomeIndicator()
        {
            // portrait phone: 132 px notch at the top, 102 px home indicator at the bottom
            var a = SafeAreaFitter.Anchors(new Rect(0, 102, 1170, 2532 - 132 - 102), 1170, 2532);
            Assert.AreEqual(0f, a.xMin, 1e-6f);
            Assert.AreEqual(1f, a.xMax, 1e-6f);
            Assert.AreEqual(102f / 2532f, a.yMin, 1e-6f);
            Assert.AreEqual((2532f - 132f) / 2532f, a.yMax, 1e-6f);
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
