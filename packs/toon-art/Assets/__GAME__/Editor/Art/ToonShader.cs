using UnityEditor;
using UnityEngine;

namespace __GAME__.Editor.Art
{
    /// <summary>
    /// The game's lit shader, <c>__GAME__/Toon</c>. It reads URP/Lit's property names (_BaseMap, _BaseColor,
    /// _Smoothness), so a builder that used to make a Lit material swaps the shader and keeps its colours. The outline
    /// is a second pass that a material without one must switch off, or every piece would draw twice: hence one entry
    /// point for the switch.
    /// </summary>
    internal static class ToonShader
    {
        const string OutlinePass = "SRPDefaultUnlit";
        static readonly int OutlineId = Shader.PropertyToID("_Outline");

        public static Shader Shader => Shader.Find("__GAME__/Toon");

        /// <summary>Puts the material on the toon shader with the outline on or off.</summary>
        public static void Apply(Material material, bool outline = true)
        {
            Shader toon = Shader;
            // A fresh clone may import a model before the shader: that material stays as it was until a reimport.
            if (toon == null)
            {
                Debug.LogWarning($"__GAME__/Toon not imported yet; {material.name} keeps {material.shader.name}");
                return;
            }
            if (material.shader != toon) material.shader = toon;
            material.SetFloat(OutlineId, outline ? 1f : 0f);
            SyncOutline(material);
        }

        public static void SyncOutline(Material material) =>
            material.SetShaderPassEnabled(OutlinePass, material.GetFloat(OutlineId) > 0.5f);
    }

    /// <summary>
    /// The default Inspector, plus the outline toggle driving its pass. Unity calls ValidateMaterial after an Inspector
    /// change, an Undo, a preset, Copy/Paste values and a material import, so a material never keeps a stale pass state
    /// until someone opens it (URP's own shader GUIs set their keywords the same way).
    /// </summary>
    internal sealed class ToonShaderGUI : ShaderGUI
    {
        public override void ValidateMaterial(Material material) => ToonShader.SyncOutline(material);
    }
}
