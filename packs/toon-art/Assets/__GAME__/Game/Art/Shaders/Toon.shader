// The look of the casual top charts, drawn like a cartoon: two crisp bands of light and shade with a cool,
// saturated tint on the shade side, sun shadows cut to the same hard edge, a sharp glossy spot and a thin light rim
// on smooth surfaces, a little contact shading where things meet the ground, and an ink outline in a darker shade of
// the surface's own color. Both bands scale with the main light (the shade tint is a ratio of the lit side), so dusk,
// night and interiors darken as a whole. Smoothness drives the spot and the rim together, so 0 gives a matte ground and 0.6 a
// plastic bag. The outline is an inverted hull pushed out by a fixed number of pixels (at 1080p, so it reads the same
// on a phone and a monitor) along the smoothed normal OutlineNormalsPostprocessor bakes into the tangent, so
// hard-edged and skinned models get an unbroken line too. A material without an outline has that pass switched off
// (ToonShader.Apply / the Outline toggle), so it pays no second draw. Merged from Pixel Volley (lighting) and Mixtrol
// (outline).
//
// Lighting: the real main light with its shadows (cascades, soft shadows and the fade at the shadow distance), point
// and spot lights banded the same way (Forward and Forward+, with their shadows), light layers, fog, ambient from
// the light probes / SH or the Adaptive Probe Volumes, SSAO (darkening both bands and the ambient) and DBuffer decals
// (on the surface colour). Baked lightmaps and shadowmask are not sampled: toon objects are lit in real time and
// take baked light through probes; the Meta pass still gives the lightmapper their albedo for bounce. Passes:
// ForwardLit, Outline (SRPDefaultUnlit), ShadowCaster, DepthOnly, DepthNormals (the normals SSAO and decals read),
// MotionVectors (TAA, STP, motion blur) and Meta. SRP batcher, GPU instancing, the GPU Resident Drawer (DOTS
// instancing) and LOD cross-fade are supported.
// The outline is drawn in the opaque list, which depth priming switches to ZTest Equal: keep the renderer's Depth
// Priming Mode on Disabled (the URP default), or the outline vanishes.
Shader "__GAME__/Toon"
{
    Properties
    {
        [MainTexture] _BaseMap("Base Map", 2D) = "white" {}
        [MainColor] _BaseColor("Base Color", Color) = (1, 1, 1, 1)
        _Smoothness("Smoothness", Range(0, 1)) = 0.3

        [Header(Bands)]
        _ShadeColor("Shade Tint", Color) = (0.62, 0.62, 0.86, 1)
        _ShadeSaturation("Shade Saturation", Range(0, 2)) = 1.3
        _RampOffset("Band Edge", Range(-1, 1)) = 0.05
        _RampSoftness("Band Softness", Range(0.001, 0.5)) = 0.035
        _AmbientStrength("Ambient", Range(0, 1)) = 0.18

        [Header(Gloss)]
        _SpecularStrength("Spot", Range(0, 2)) = 0.85
        _RimStrength("Rim", Range(0, 1)) = 0.5
        _RimEdge("Rim Edge", Range(0, 1)) = 0.62

        [Header(Contact)]
        _ContactShade("Contact Shade", Range(0, 1)) = 0.3
        _GroundY("Ground Height (world Y)", Float) = -0.06
        _ContactHeight("Contact Height", Float) = 0.25

        [Header(Outline)]
        [ToggleUI] _Outline("Outline", Float) = 1
        _OutlineColor("Outline Tint", Color) = (0.36, 0.3, 0.46, 1)
        _OutlineWidth("Outline Width, 1080p pixels", Range(0, 8)) = 1.5
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        // The URP pass files included below (ShadowCaster, DepthOnly, DepthNormals, Meta) read _BaseMap, _BaseMap_ST
        // and _BaseColor from here, the names URP/Lit uses.
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _Smoothness;
            half4 _ShadeColor;
            half _ShadeSaturation;
            half _RampOffset;
            half _RampSoftness;
            half _AmbientStrength;
            half _SpecularStrength;
            half _RimStrength;
            half _RimEdge;
            half _ContactShade;
            float _GroundY;
            float _ContactHeight;
            half _Outline;
            half4 _OutlineColor;
            float _OutlineWidth;
        CBUFFER_END

        TEXTURE2D(_BaseMap);
        SAMPLER(sampler_BaseMap);
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            // SSAO (any mode), DBuffer decals and Adaptive Probe Volumes; stripped when the URP asset has none of them
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _DBUFFER_MRT1 _DBUFFER_MRT2 _DBUFFER_MRT3
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/ProbeVolumeVariants.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #pragma multi_compile_instancing
            #pragma instancing_options renderinglayer
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #if defined(LOD_FADE_CROSSFADE)
                #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/LODCrossFade.hlsl"
            #endif

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half fogFactor : TEXCOORD3;
                #if defined(_MAIN_LIGHT_SHADOWS_SCREEN)
                    float4 shadowCoord : TEXCOORD4;
                #endif
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                VertexPositionInputs position = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = position.positionCS;
                output.positionWS = position.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.fogFactor = ComputeFogFactor(position.positionCS.z);
                #if defined(_MAIN_LIGHT_SHADOWS_SCREEN)
                    output.shadowCoord = GetShadowCoord(position);
                #endif
                return output;
            }

            // a point or spot light: the same band as the sun, scaled by its falloff and its shadow
            half3 AdditionalToon(Light light, half3 albedo, half3 normal, uint meshRenderingLayers)
            {
                #if defined(_LIGHT_LAYERS)
                    if (!IsMatchingLightLayer(light.layerMask, meshRenderingLayers)) return 0;
                #endif
                half band = smoothstep(_RampOffset - _RampSoftness, _RampOffset + _RampSoftness, dot(normal, light.direction));
                return albedo * light.color * (band * light.distanceAttenuation * light.shadowAttenuation);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                #if defined(LOD_FADE_CROSSFADE)
                    LODFadeCrossFade(input.positionCS);
                #endif
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb * _BaseColor.rgb;
                #if defined(_DBUFFER)
                    ApplyDecalToBaseColor(input.positionCS, albedo);    // DBuffer decals tint the surface colour
                #endif
                half3 normal = normalize(input.normalWS);
                half3 view = GetWorldSpaceNormalizeViewDir(input.positionWS);
                float2 screenUV = GetNormalizedScreenSpaceUV(input.positionCS);
                // 1 without the SSAO keyword; with it, creases darken in both bands and in the ambient
                AmbientOcclusionFactor ao = GetScreenSpaceAmbientOcclusion(screenUV);
                uint meshRenderingLayers = 0;
                #if defined(_LIGHT_LAYERS)
                    meshRenderingLayers = GetMeshRenderingLayer();
                #endif

                #if defined(_MAIN_LIGHT_SHADOWS_SCREEN)
                    float4 shadowCoord = input.shadowCoord;
                #else
                    float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                #endif
                // this overload fades the shadow out toward the shadow distance; no shadowmask is sampled (see top)
                half4 shadowMask = half4(1, 1, 1, 1);
                Light light = GetMainLight(shadowCoord, input.positionWS, shadowMask);
                half mainOn = light.distanceAttenuation;
                #if defined(_LIGHT_LAYERS)
                    if (!IsMatchingLightLayer(light.layerMask, meshRenderingLayers)) mainOn = 0;
                #endif
                half facing = dot(normal, light.direction);
                // two flat bands with a narrow edge between them, and shadows cut to the same edge
                half band = smoothstep(_RampOffset - _RampSoftness, _RampOffset + _RampSoftness, facing);
                half shadow = smoothstep(0.3, 0.7, light.shadowAttenuation);
                half lit = band * shadow * mainOn;

                // the shade keeps its color: richer and cooler instead of grayer. Both bands take the main light, so
                // the tint is a ratio of the lit side: a dim sun dims the shade with it, and with the main light off
                // (or on another light layer) only the ambient and the point and spot lights remain
                half3 shadeAlbedo = lerp(Luminance(albedo).xxx, albedo, _ShadeSaturation) * _ShadeColor.rgb;
                half3 color = lerp(shadeAlbedo * ao.indirectAmbientOcclusion,
                                   albedo * ao.directAmbientOcclusion, lit) * (light.color * mainOn);
                // ambient from the light probes, or from the Adaptive Probe Volumes when the URP asset uses them
                #if defined(PROBE_VOLUMES_L1) || defined(PROBE_VOLUMES_L2)
                    half3 ambient = SampleProbeVolumePixel(half3(0, 0, 0), GetAbsolutePositionWS(input.positionWS),
                                                           normal, view, input.positionCS.xy);
                #else
                    half3 ambient = SampleSH(normal);
                #endif
                color += albedo * ambient * (_AmbientStrength * ao.indirectAmbientOcclusion);

                // point and spot lights; a per-vertex setting on the URP asset is lit per pixel too, for the band
                #if defined(_ADDITIONAL_LIGHTS) || defined(_ADDITIONAL_LIGHTS_VERTEX)
                    InputData inputData = (InputData)0;     // LIGHT_LOOP_BEGIN reads these two in Forward+
                    inputData.positionWS = input.positionWS;
                    inputData.normalizedScreenSpaceUV = screenUV;
                    uint pixelLightCount = GetAdditionalLightsCount();
                    #if USE_CLUSTER_LIGHT_LOOP
                        [loop] for (uint lightIndex = 0; lightIndex < min(URP_FP_DIRECTIONAL_LIGHTS_COUNT, MAX_VISIBLE_LIGHTS); lightIndex++)
                        {
                            CLUSTER_LIGHT_LOOP_SUBTRACTIVE_LIGHT_CHECK
                            color += AdditionalToon(GetAdditionalLight(lightIndex, input.positionWS, shadowMask), albedo, normal, meshRenderingLayers);
                        }
                    #endif
                    LIGHT_LOOP_BEGIN(pixelLightCount)
                        color += AdditionalToon(GetAdditionalLight(lightIndex, input.positionWS, shadowMask), albedo, normal, meshRenderingLayers);
                    LIGHT_LOOP_END
                #endif

                // things darken a little toward the ground they stand on. Ceiling: one world-space height per material
                // (_GroundY), so it suits a level whose floor is a plane; with several floor heights set _ContactShade
                // to 0, or _GroundY per material. An object-relative height would break skinned meshes (their matrix
                // is the root bone's) and statically batched ones (identity matrix).
                half contact = saturate((input.positionWS.y - _GroundY) / _ContactHeight);
                color *= lerp(1.0 - _ContactShade, 1.0, contact * contact * (3.0 - 2.0 * contact));

                // a hard-edged glossy spot, and a thin rim of light round the sunny side of the outline, both only as
                // strong as the surface is smooth
                half3 halfway = normalize(light.direction + view);
                half exponent = exp2(_Smoothness * 9.0 + 1.0);
                half spot = smoothstep(0.45, 0.55, pow(saturate(dot(normal, halfway)), exponent));
                half fresnel = (1.0 - saturate(dot(normal, view))) * (0.4 + 0.6 * saturate(facing + 0.3));
                half rim = smoothstep(_RimEdge - 0.04, _RimEdge + 0.04, fresnel);
                color += light.color * mainOn * _Smoothness * (spot * _SpecularStrength * lit + rim * _RimStrength * (0.3 + 0.7 * shadow));

                return half4(MixFog(color, input.fogFactor), 1.0);
            }
            ENDHLSL
        }

        // the ink line: the back faces, pushed out a little and filled with a dark tint of the surface's color
        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "SRPDefaultUnlit" }
            Cull Front

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            #if defined(LOD_FADE_CROSSFADE)
                #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/LODCrossFade.hlsl"
            #endif

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                half fogFactor : TEXCOORD1;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                // a baked mesh carries its smoothed normal in the tangent with w = 0, which skinning moves with the
                // bones; a real tangent has w = +-1, so any other mesh (or one made in code) uses its own normal
                bool smoothed = abs(input.tangentOS.w) < 0.5 && dot(input.tangentOS.xyz, input.tangentOS.xyz) > 0.25;
                float3 normalOS = smoothed ? input.tangentOS.xyz : input.normalOS;

                // pushed out in screen space, a fixed number of 1080p pixels whatever the distance or resolution
                float4 positionCS = TransformObjectToHClip(input.positionOS.xyz);
                float3 normalCS = mul((float3x3)UNITY_MATRIX_VP, TransformObjectToWorldNormal(normalOS));
                float2 direction = normalize(normalCS.xy + 1e-5);
                float2 pixel = float2(_ScreenParams.y / _ScreenParams.x, 1.0) * (2.0 / 1080.0);
                positionCS.xy += direction * pixel * _OutlineWidth * positionCS.w;
                output.positionCS = positionCS;
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.fogFactor = ComputeFogFactor(positionCS.z);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                #if defined(LOD_FADE_CROSSFADE)
                    LODFadeCrossFade(input.positionCS);
                #endif
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb * _BaseColor.rgb;
                return half4(MixFog(albedo * _OutlineColor.rgb, input.fogFactor), 1.0);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0

            HLSLPROGRAM
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/ShadowCasterPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma vertex DepthOnlyVertex
            #pragma fragment DepthOnlyFragment
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            ENDHLSL
        }

        // the normals buffer that SSAO (its default source), decals and other screen effects read
        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On

            HLSLPROGRAM
            #pragma vertex DepthNormalsVertex
            #pragma fragment DepthNormalsFragment
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            ENDHLSL
        }

        // per-object motion for TAA, STP and motion blur (URP's own pass file, as URP/Lit uses it); the outline hull
        // has none of its own, so the few pixels it adds past the silhouette take the camera's motion. The pass file
        // declares its own vertex/fragment, multi_compile_instancing and DOTS.hlsl pragmas, so none are repeated here
        Pass
        {
            Name "MotionVectors"
            Tags { "LightMode" = "MotionVectors" }
            ColorMask RG

            HLSLPROGRAM
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/ObjectMotionVectors.hlsl"
            ENDHLSL
        }

        // only the lightmapper draws this: the surface color that baked bounce light picks up
        Pass
        {
            Name "Meta"
            Tags { "LightMode" = "Meta" }
            Cull Off

            HLSLPROGRAM
            #pragma vertex UniversalVertexMeta
            #pragma fragment UniversalFragmentMetaUnlit
            #pragma shader_feature EDITOR_VISUALIZATION
            #include "Packages/com.unity.render-pipelines.universal/Shaders/UnlitMetaPass.hlsl"
            ENDHLSL
        }
    }

    CustomEditor "__GAME__.Editor.Art.ToonShaderGUI"
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
