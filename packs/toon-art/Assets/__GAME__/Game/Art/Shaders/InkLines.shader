// Inner ink lines, drawn once over the opaque scene by a renderer's "Ink Lines" full screen pass (the
// __GAME__/Art/Add Ink Lines menu, Editor/Art/InkLines.cs) before the transparents, so world labels stay clean. The
// Toon outline draws only the silhouette; this adds the lines inside it. A pixel turns to ink where one surface passes
// in front of another (the second difference of 1/depth, which is zero across any flat face, so a ground seen at a
// grazing angle stays clean) or where the surface folds by more than _NormalEdge (panel seams, bevels, limb
// overlaps). The ink leans 20% toward the scene colour like the Toon outline, and the lines fade out between
// _FadeStart and _FadeEnd so far hills do not fill with them. The sky is skipped. Cost: 9 depth and 5 normals reads a
// pixel plus the depth and normals prepasses it asks for, so it is a PC-tier pass, not a phone one.
Shader "__GAME__/InkLines"
{
    Properties
    {
        _InkColor("Ink", Color) = (0.106, 0.114, 0.122, 1)
        _Width("Width, 1080p pixels", Range(0.5, 3)) = 1
        _DepthEdge("Depth Edge", Range(0.005, 0.5)) = 0.06
        _NormalEdge("Normal Edge", Range(0.05, 1)) = 0.35
        _FadeStart("Fade Start, m", Float) = 25
        _FadeEnd("Fade End, m", Float) = 90
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off
        Blend Off

        Pass
        {
            Name "InkLines"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareNormalsTexture.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _InkColor;
                float _Width;
                float _DepthEdge;
                float _NormalEdge;
                float _FadeStart;
                float _FadeEnd;
            CBUFFER_END

            float InverseDepth(float2 uv)
            {
                return 1.0 / LinearEyeDepth(SampleSceneDepth(uv), _ZBufferParams);
            }

            half Fold(float3 normal, float2 uv)
            {
                return 1.0 - dot(normal, SampleSceneNormals(uv));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float2 uv = input.texcoord;
                half4 scene = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_PointClamp, uv);
                float raw = SampleSceneDepth(uv);
                #if UNITY_REVERSED_Z
                    if (raw <= 0.0) return scene;
                #else
                    if (raw >= 1.0) return scene;
                #endif

                float eye = LinearEyeDepth(raw, _ZBufferParams);
                float2 texel = _Width * (_ScreenParams.y / 1080.0) / _ScreenParams.xy;
                float2 dx = float2(texel.x, 0.0);
                float2 dy = float2(0.0, texel.y);

                float centre = 1.0 / eye;
                float depthEdge = (abs(InverseDepth(uv - dx) + InverseDepth(uv + dx) - 2.0 * centre) +
                                   abs(InverseDepth(uv - dy) + InverseDepth(uv + dy) - 2.0 * centre)) / centre;
                float3 normal = SampleSceneNormals(uv);
                half fold = max(max(Fold(normal, uv - dx), Fold(normal, uv + dx)),
                                max(Fold(normal, uv - dy), Fold(normal, uv + dy)));

                half edge = max(smoothstep(_DepthEdge, _DepthEdge * 1.5, depthEdge),
                                smoothstep(_NormalEdge, _NormalEdge * 1.2, fold));
                // the taps stay a texel apart, so a far stroke is drawn by its coverage instead of growing thinner;
                // orthographic objects keep the same projected size at every depth
                float coverage = lerp(rcp(max(eye, 1.0)), 1.0, unity_OrthoParams.w);
                edge *= coverage;
                edge *= 1.0 - saturate((eye - _FadeStart) / (_FadeEnd - _FadeStart));
                half3 ink = lerp(_InkColor.rgb, scene.rgb, 0.2);
                return half4(lerp(scene.rgb, ink, edge), scene.a);
            }
            ENDHLSL
        }
    }
}
