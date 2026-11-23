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
    /// object in Play Mode. The passes this shader writes itself (ForwardLit, Outline) are also compiled for the phone
    /// and WebGL graphics APIs (GLES3, Vulkan, Metal) of every installed build module, in the variants the Mobile tier
    /// runs and a Forward+ one with LOD cross-fade; the URP pass files the others include are URP/Lit's own. ProjectSetup runs it when a game is made; it
    /// ends with "[toon-art] Toon shader OK" or "[toon-art] Toon shader: N error(s)", which test-template.ps1 reads
    /// from Logs\setup.log.
    /// </summary>
    internal static class ToonShaderCheck
    {
        // ProjectSetup's Mobile tier (one cascade, hard shadows, Forward), which phones and WebGL default to; declared
        // first, because static fields initialise in order
        static readonly string[] MobileTier = { "_MAIN_LIGHT_SHADOWS", "_ADDITIONAL_LIGHTS" };

        // the default variant plus the global keywords the forward and outline passes branch on; a keyword the
        // shader does not declare is an error too, so a dropped #pragma is caught as well
        static readonly string[][] KeywordSets =
        {
            new string[0],
            new[] { "_MAIN_LIGHT_SHADOWS_CASCADE", "_ADDITIONAL_LIGHTS", "_ADDITIONAL_LIGHT_SHADOWS", "_SHADOWS_SOFT",
                    "_LIGHT_LAYERS", "LOD_FADE_CROSSFADE" },
            new[] { "_MAIN_LIGHT_SHADOWS_SCREEN", "_ADDITIONAL_LIGHTS", "_CLUSTER_LIGHT_LOOP", "_DBUFFER_MRT1",
                    "PROBE_VOLUMES_L2" },
            new[] { "_MAIN_LIGHT_SHADOWS_CASCADE", "_SHADOWS_SOFT_LOW", "_SCREEN_SPACE_OCCLUSION", "_DBUFFER_MRT3",
                    "PROBE_VOLUMES_L1" },
            new[] { "_ADDITIONAL_LIGHTS_VERTEX" },
            MobileTier,
            new[] { "_WEAR", "_MAIN_LIGHT_SHADOWS_CASCADE" },   // the painted wear (Toon.shader Wear)
        };

        // the variants compiled for each device API: what the Mobile tier runs, with and without its lights, and a
        // Forward+ renderer with LOD cross-fade (URP sets _CLUSTER_LIGHT_LOOP there instead of _ADDITIONAL_LIGHTS, and
        // its uint cluster loop is the code most likely to hit a GLSL ES or Metal limit)
        static readonly string[][] DeviceKeywordSets =
        {
            new string[0], MobileTier, new[] { "_ADDITIONAL_LIGHTS_VERTEX" }, new[] { "_WEAR" },
            new[] { "_MAIN_LIGHT_SHADOWS", "_CLUSTER_LIGHT_LOOP", "LOD_FADE_CROSSFADE" },
        };

        static readonly (ShaderCompilerPlatform api, BuildTargetGroup group, BuildTarget target)[] DeviceApis =
        {
            (ShaderCompilerPlatform.GLES3x, BuildTargetGroup.WebGL, BuildTarget.WebGL),
            (ShaderCompilerPlatform.GLES3x, BuildTargetGroup.Android, BuildTarget.Android),
            (ShaderCompilerPlatform.Vulkan, BuildTargetGroup.Android, BuildTarget.Android),
            (ShaderCompilerPlatform.Metal, BuildTargetGroup.iOS, BuildTarget.iOS),
        };

        static readonly string[] OwnPasses = { "ForwardLit", "Outline" };

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

            errors += CompileForDevices(shader, out string apis);

            if (errors == 0) Debug.Log($"[toon-art] Toon shader OK (device APIs: {apis})");
            else Debug.LogError($"[toon-art] Toon shader: {errors} error(s)");
        }

        // GLSL ES and Metal limits (loops, precision, uint use) fail only there, so the Editor's D3D compile misses
        // them; a target whose build module is not installed is skipped and the summary names what was compiled
        static int CompileForDevices(Shader shader, out string apis)
        {
            int errors = 0;
            apis = "";
            ShaderData.Subshader subshader = ShaderUtil.GetShaderData(shader).ActiveSubshader;
            foreach (var (api, group, target) in DeviceApis)
            {
                if (!BuildPipeline.IsBuildTargetSupported(group, target)) continue;
                apis += (apis.Length > 0 ? ", " : "") + $"{api}/{target}";
                for (int i = 0; i < subshader.PassCount; i++)
                {
                    ShaderData.Pass pass = subshader.GetPass(i);
                    if (System.Array.IndexOf(OwnPasses, pass.Name) < 0) continue;
                    foreach (string[] set in DeviceKeywordSets)
                    foreach (ShaderType stage in new[] { ShaderType.Vertex, ShaderType.Fragment })
                    {
                        if (!pass.HasShaderStage(stage)) continue;
                        ShaderData.VariantCompileInfo info = pass.CompileVariant(stage, set, api, target);
                        foreach (ShaderMessage m in info.Messages)
                        {
                            if (m.severity != ShaderCompilerMessageSeverity.Error) continue;
                            Debug.LogError($"[toon-art] Toon shader ({pass.Name}, {api}/{target}, " +
                                           $"[{string.Join(" ", set)}]): {m.message} ({m.file}:{m.line})");
                            errors++;
                        }
                    }
                }
            }
            if (apis.Length == 0) apis = "none installed";
            return errors;
        }
    }
}
