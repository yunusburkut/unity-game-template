using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace __GAME__.Editor
{
    /// <summary>
    /// The mobile-2d pack's setup step, run by ProjectSetup after its own: both URP assets render through one 2D
    /// Renderer (sprites, Light2D, sorting layers), the Editor starts in 2D mode (textures import as sprites, the
    /// Scene view is 2D), and Main gets an orthographic camera and a global 2D light instead of the 3D sun.
    /// Safe to run again.
    /// </summary>
    static class Setup2D
    {
        const string RendererPath = ProjectSetup.SettingsFolder + "/URP_2D_Renderer.asset";
        const string UrpPackage = "Packages/com.unity.render-pipelines.universal";

        [ProjectSetupStep]
        public static void Run()
        {
            var renderer = AssetDatabase.LoadAssetAtPath<Renderer2DData>(RendererPath);
            if (renderer == null)
            {
                // what URP's own Create > 2D Renderer menu does
                renderer = ScriptableObject.CreateInstance<Renderer2DData>();
                AssetDatabase.CreateAsset(renderer, RendererPath);
                ResourceReloader.ReloadAllNullIn(renderer, UrpPackage);

                // the property is internal; without the data the renderer skips every Volume effect
                var serialized = new SerializedObject(renderer);
                serialized.FindProperty("m_PostProcessData").objectReferenceValue =
                    AssetDatabase.LoadAssetAtPath<PostProcessData>(UrpPackage + "/Runtime/Data/PostProcessData.asset");
                serialized.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(renderer);
            }

            foreach (string tier in new[] { "Mobile", "PC" })
            {
                var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    ProjectSetup.SettingsFolder + "/URP_" + tier + ".asset");
                var serialized = new SerializedObject(pipeline);
                var list = serialized.FindProperty("m_RendererDataList");
                list.arraySize = 1;
                list.GetArrayElementAtIndex(0).objectReferenceValue = renderer;
                serialized.FindProperty("m_DefaultRendererIndex").intValue = 0;
                serialized.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(pipeline);
            }

            EditorSettings.defaultBehaviorMode = EditorBehaviorMode.Mode2D;
            SetUpScene();
            Debug.Log("[Setup2D] Done: 2D Renderer on both tiers, Editor in 2D mode, Main has an orthographic camera.");
        }

        static void SetUpScene()
        {
            var scene = EditorSceneManager.OpenScene(ProjectSetup.ScenePath, OpenSceneMode.Single);

            foreach (var light in Object.FindObjectsByType<Light>(FindObjectsInactive.Include))
                Object.DestroyImmediate(light.gameObject);

            var camera = Object.FindFirstObjectByType<Camera>();
            if (camera != null)
            {
                camera.orthographic = true;
                camera.orthographicSize = 5f;
                camera.transform.SetPositionAndRotation(new Vector3(0f, 0f, -10f), Quaternion.identity);
                camera.clearFlags = CameraClearFlags.SolidColor;
            }

            if (Object.FindFirstObjectByType<Light2D>() == null)
            {
                var light = new GameObject("Global Light 2D").AddComponent<Light2D>();
                light.lightType = Light2D.LightType.Global;
            }

            EditorSceneManager.SaveScene(scene);
        }
    }
}
