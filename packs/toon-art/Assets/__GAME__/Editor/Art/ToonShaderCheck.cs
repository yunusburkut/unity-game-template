using GameKit.Editor;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace __GAME__.Editor.Art
{
    /// <summary>
    /// Compiles every pass of <c>__GAME__/Toon</c> for a few keyword sets and logs each compiler error. Unity compiles
    /// shaders lazily, so a broken pass (for example after a URP include changes) otherwise shows up only as a pink
    /// object in Play Mode. ProjectSetup runs it when a game is made; it ends with "[toon-art] Toon shader OK" or
    /// "[toon-art] Toon shader: N error(s)", which test-template.ps1 reads from Logs\setup.log.
    /// </summary>
    internal static class ToonShaderCheck
    {
        // the default variant plus the global keywords the forward and outline passes branch on; a keyword the
        // shader does not declare is an error too, so a dropped #pragma is caught as well
        static readonly string[][] KeywordSets =
        {
            new string[0],
            new[] { "_MAIN_LIGHT_SHADOWS_CASCADE", "_ADDITIONAL_LIGHTS", "_ADDITIONAL_LIGHT_SHADOWS", "_SHADOWS_SOFT",
                    "_LIGHT_LAYERS", "LOD_FADE_CROSSFADE" },
            new[] { "_MAIN_LIGHT_SHADOWS_SCREEN", "_ADDITIONAL_LIGHTS", "_CLUSTER_LIGHT_LOOP" },
            new[] { "_ADDITIONAL_LIGHTS_VERTEX" },
        };

        [ProjectSetupStep]
        [MenuItem("__GAME__/Art/Check Toon Shader")]
        public static void Run()
        {
            Shader shader = ToonShader.Shader;
            if (shader == null)
            {
                Debug.LogError("[toon-art] Toon shader: 1 error(s). __GAME__/Toon not found (not imported, or it failed to parse)");
                return;
            }

            int errors = 0;
            var material = new Material(shader);
            try
            {
                foreach (string[] set in KeywordSets)
                {
                    foreach (LocalKeyword k in material.enabledKeywords) material.SetKeyword(k, false);
                    foreach (string name in set)
                    {
                        var keyword = new LocalKeyword(shader, name);
                        if (!keyword.isValid)
                        {
                            Debug.LogError($"[toon-art] Toon shader declares no keyword {name}");
                            errors++;
                            continue;
                        }
                        material.SetKeyword(keyword, true);
                    }
                    for (int pass = 0; pass < material.passCount; pass++) ShaderUtil.CompilePass(material, pass, true);
                }
            }
            finally
            {
                Object.DestroyImmediate(material);
            }

            foreach (ShaderMessage m in ShaderUtil.GetShaderMessages(shader))
            {
                if (m.severity != ShaderCompilerMessageSeverity.Error) continue;
                Debug.LogError($"[toon-art] Toon shader: {m.message} ({m.file}:{m.line}, {m.platform})");
                errors++;
            }

            if (errors == 0) Debug.Log("[toon-art] Toon shader OK");
            else Debug.LogError($"[toon-art] Toon shader: {errors} error(s)");
        }
    }
}
