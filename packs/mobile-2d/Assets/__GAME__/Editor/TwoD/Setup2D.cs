using GameKit.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace __GAME__.Editor
{
    /// <summary>
    /// The mobile-2d pack's setup step, run by ProjectSetup after its own: both URP assets render through one 2D
    /// Renderer (sprites, Light2D, sorting layers) and the Mobile tier drops MSAA, the Editor starts in 2D mode
    /// (textures import as sprites, the Scene view is 2D), and Main gets an orthographic camera and a global 2D light
    /// instead of the 3D sun.
    /// Safe to run again: a tier whose default renderer is already a 2D renderer is left as it is, and Main is
    /// converted only while it has neither a Light2D nor an orthographic camera, so later tuning of the renderer
    /// lists, MSAA, the camera and the lights survives a rerun of Set Up Project.
    /// </summary>
    static class Setup2D
    {
        static string RendererPath => ProjectSetup.SettingsFolder + "/URP_2D_Renderer.asset";
        const string UrpPackage = "Packages/com.unity.render-pipelines.universal";

        [ProjectSetupStep]
        public static void Run()
        {
            var renderer = AssetDatabase.LoadAssetAtPath<Renderer2DData>(RendererPath);
            if (renderer == null)
            {
                // what URP's own Create > 2D Renderer menu does (Renderer2DMenus.CreateRendererAsset)
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
                int index = serialized.FindProperty("m_DefaultRendererIndex").intValue;
                if (index < list.arraySize && list.GetArrayElementAtIndex(index).objectReferenceValue is Renderer2DData)
                    continue; // already 2D: the tier's renderer list is the game's to tune from here on

                list.arraySize = 1;
                list.GetArrayElementAtIndex(0).objectReferenceValue = renderer;
                serialized.FindProperty("m_DefaultRendererIndex").intValue = 0;
                // MSAA barely helps alpha-edged sprites and costs tile-GPU bandwidth; Unity's 2D URP setup ships
                // with it off. PC keeps ProjectSetup's value: the game decides there.
                if (tier == "Mobile") serialized.FindProperty("m_MSAA").intValue = (int)MsaaQuality.Disabled;
                serialized.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(pipeline);
            }

            EditorSettings.defaultBehaviorMode = EditorBehaviorMode.Mode2D;
            if (SetUpScene())
                Debug.Log("[Setup2D] Done: 2D Renderer on both tiers, Editor in 2D mode, Main has an orthographic camera.");
            else
                Debug.LogWarning("[Setup2D] 2D Renderer and 2D mode applied; Main left as it is (missing, or it has "
                    + "unsaved changes that were not saved). Save Main and run Set Up Project again to finish it.");
        }

        /// <summary>
        /// Converts Main once: 3D lights out, camera orthographic, a global Light2D in. Main is opened additively
        /// when it is not loaded, so the open scenes and their unsaved edits stay as they are.
        /// </summary>
        static bool SetUpScene()
        {
            if (!System.IO.File.Exists(ProjectSetup.ScenePath)) return false;

            var scene = SceneManager.GetSceneByPath(ProjectSetup.ScenePath);
            bool opened = !scene.isLoaded;
            if (opened)
                scene = EditorSceneManager.OpenScene(ProjectSetup.ScenePath, OpenSceneMode.Additive);
            else if (scene.isDirty && !Application.isBatchMode
                     && (!ProjectSetup.SaveOpenScenesFirst() || scene.isDirty))
                return false; // saving Main below would also write edits the user chose not to keep

            // converted once Main has a Light2D or an orthographic camera: a game that later drops the global light
            // (unlit sprites) keeps its tuned camera, and one that later goes perspective (parallax) keeps its Light2D
            var roots = scene.GetRootGameObjects();
            bool converted = false;
            foreach (var root in roots)
            {
                if (root.GetComponentInChildren<Light2D>(true) != null) converted = true;
                foreach (var cam in root.GetComponentsInChildren<Camera>(true))
                    if (cam.orthographic) converted = true;
            }

            if (!converted)
            {
                foreach (var root in roots)
                    foreach (var light in root.GetComponentsInChildren<Light>(true))
                    {
                        if (light == null) continue; // its GameObject went with an earlier parent
                        // the template's sun stands alone; a Light on anything else loses only the component.
                        // URP adds UniversalAdditionalLightData ([RequireComponent(typeof(Light))]) once the light
                        // has rendered: it does not count against "alone", and it goes first so the Light can go
                        bool alone = light.transform.childCount == 0;
                        foreach (var component in light.GetComponents<Component>())
                            if (!(component is Transform || component is Light || component is UniversalAdditionalLightData))
                                alone = false;
                        if (alone)
                        {
                            Object.DestroyImmediate(light.gameObject);
                            continue;
                        }
                        if (light.TryGetComponent(out UniversalAdditionalLightData data)) Object.DestroyImmediate(data);
                        Object.DestroyImmediate(light);
                    }

                Camera camera = null;
                foreach (var root in roots)
                    if (camera == null) camera = root.GetComponentInChildren<Camera>(true);
                if (camera != null)
                {
                    camera.orthographic = true;
                    camera.orthographicSize = 5f;
                    camera.transform.SetPositionAndRotation(new Vector3(0f, 0f, -10f), Quaternion.identity);
                    camera.clearFlags = CameraClearFlags.SolidColor;
                }

                var light2D = new GameObject("Global Light 2D").AddComponent<Light2D>();
                light2D.lightType = Light2D.LightType.Global;
                SceneManager.MoveGameObjectToScene(light2D.gameObject, scene);
                EditorSceneManager.SaveScene(scene);
            }

            if (opened) EditorSceneManager.CloseScene(scene, true);
            return true;
        }
    }
}
