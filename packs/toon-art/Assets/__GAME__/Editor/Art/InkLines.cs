using System;
using System.Linq;
using GameKit.Editor;
using Unity.Pipeline.Commands;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace __GAME__.Editor.Art
{
    /// <summary>
    /// Adds the inner ink lines (<c>__GAME__/InkLines</c>) as URP's own full screen pass on the PC tier's renderer,
    /// before the transparents so world labels stay clean; it asks for the depth and normals textures the shader reads.
    /// Opt-in: a look choice and a PC cost (9 depth and 5 normals reads a pixel), so ProjectSetup does not run it and the
    /// Mobile tier never gets it. Found by name, so a rerun updates the feature instead of adding a second one.
    /// </summary>
    internal static class InkLines
    {
        const string FeatureName = "Ink Lines";

        [MenuItem("__GAME__/Art/Add Ink Lines (PC tier)")]
        static void Menu() => Debug.Log("[toon-art] " + Add());

        [CliCommand("art", "ink-lines", "Add or update the Ink Lines full screen pass on the PC tier's URP renderer")]
        public static string Add()
        {
            string rendererPath = ProjectSetup.SettingsFolder + "/URP_PC_Renderer.asset";
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(rendererPath);
            if (data == null) return $"Refused: no {rendererPath} (run GameKit's ProjectSetup first).";

            string materialPath = ProjectSetup.Root + "/Game/Art/Materials/M_InkLines.mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (material == null)
            {
                material = new Material(Shader.Find("__GAME__/InkLines") ??
                                        throw new InvalidOperationException("__GAME__/InkLines not imported"));
                System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(materialPath));
                AssetDatabase.CreateAsset(material, materialPath);
            }

            var ink = data.rendererFeatures.OfType<FullScreenPassRendererFeature>().FirstOrDefault(f => f.name == FeatureName);
            if (ink == null)
            {
                // the same two lists the renderer's Inspector fills when a feature is added by hand
                ink = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                ink.name = FeatureName;
                AssetDatabase.AddObjectToAsset(ink, data);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(ink, out _, out long id);
                var so = new SerializedObject(data);
                SerializedProperty features = so.FindProperty("m_RendererFeatures");
                SerializedProperty map = so.FindProperty("m_RendererFeatureMap");
                features.arraySize++;
                features.GetArrayElementAtIndex(features.arraySize - 1).objectReferenceValue = ink;
                map.arraySize++;
                map.GetArrayElementAtIndex(map.arraySize - 1).longValue = id;
                so.ApplyModifiedPropertiesWithoutUndo();
            }

            ink.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingTransparents;
            ink.fetchColorBuffer = true;
            ink.requirements = ScriptableRenderPassInput.Depth | ScriptableRenderPassInput.Normal;
            ink.passMaterial = material;
            ink.passIndex = 0;
            ink.SetActive(true);
            EditorUtility.SetDirty(ink);
            data.SetDirty();
            AssetDatabase.SaveAssetIfDirty(data);
            return $"Ink Lines on {rendererPath}, material {materialPath} (tune its Width, Depth Edge, Normal Edge, Fade).";
        }
    }
}
