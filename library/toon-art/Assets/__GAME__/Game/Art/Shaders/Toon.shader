// The look of the casual top charts, drawn like a cartoon: two crisp bands of light and shade with a cool,
// saturated tint on the shade side, sun shadows cut to the same hard edge, a sharp glossy spot and a thin light rim
// on smooth surfaces, a little contact shading where things meet the ground, and an ink outline in a darker shade of
// the surface's own color. Smoothness drives the spot and the rim together, so 0 gives a matte ground and 0.6 a
// plastic bag. The outline is an inverted hull pushed out by a fixed number of pixels (at 1080p, so it reads the same
// on a phone and a monitor) along the smoothed normal OutlineNormalsPostprocessor bakes into the tangent, so
// hard-edged and skinned models get an unbroken line too. A material without an outline has that pass switched off
// (ToonShader.Apply / the Outline toggle), so it pays no second draw. Real main light and shadows; SRP batcher and
// GPU instancing friendly. Merged from Pixel Volley (lighting) and Mixtrol (outline).
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
        _GroundY("Ground Height", Float) = -0.06
        _ContactHeight("Contact Height", Float) = 0.25

        [Header(Outline)]
        [ToggleUI] _Outline("Outline", Float) = 1
        _OutlineColor("Outline Tint", Color) = (0.36, 0.3, 0.46, 1)
        _OutlineWidth("Outline Width, 1080p pixels", Range(0, 8)) = 1.5
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

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
            #pragma multi_compile_instancing
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

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
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb * _BaseColor.rgb;
                half3 normal = normalize(input.normalWS);
                half3 view = GetWorldSpaceNormalizeViewDir(input.positionWS);

                Light light = GetMainLight(TransformWorldToShadowCoord(input.positionWS));
                half facing = dot(normal, light.direction);
                // two flat bands with a narrow edge between them, and shadows cut to the same edge
                half band = smoothstep(_RampOffset - _RampSoftness, _RampOffset + _RampSoftness, facing);
                half shadow = smoothstep(0.3, 0.7, light.shadowAttenuation);
                half lit = band * shadow;

                // the shade keeps its color: richer and cooler instead of grayer
                half3 shadeAlbedo = lerp(Luminance(albedo).xxx, albedo, _ShadeSaturation) * _ShadeColor.rgb;
                half3 color = lerp(shadeAlbedo, albedo * light.color, lit);
                color += albedo * SampleSH(normal) * _AmbientStrength;

                // things darken a little toward the ground they stand on
                half contact = saturate((input.positionWS.y - _GroundY) / _ContactHeight);
                color *= lerp(1.0 - _ContactShade, 1.0, contact * contact * (3.0 - 2.0 * contact));

                // a hard-edged glossy spot, and a thin rim of light round the sunny side of the outline, both only as
                // strong as the surface is smooth
                half3 halfway = normalize(light.direction + view);
                half exponent = exp2(_Smoothness * 9.0 + 1.0);
                half spot = smoothstep(0.45, 0.55, pow(saturate(dot(normal, halfway)), exponent));
                half fresnel = (1.0 - saturate(dot(normal, view))) * (0.4 + 0.6 * saturate(facing + 0.3));
                half rim = smoothstep(_RimEdge - 0.04, _RimEdge + 0.04, fresnel);
                color += light.color * _Smoothness * (spot * _SpecularStrength * lit + rim * _RimStrength * (0.3 + 0.7 * shadow));

                return half4(color, 1.0);
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
            #pragma multi_compile_instancing

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
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb * _BaseColor.rgb;
                return half4(albedo * _OutlineColor.rgb, 1.0);
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
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 Vert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                float3 normalWS = TransformObjectToWorldNormal(input.normalOS);
                #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                    float3 lightDirection = normalize(_LightPosition - positionWS);
                #else
                    float3 lightDirection = _LightDirection;
                #endif
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirection));
                #if UNITY_REVERSED_Z
                    positionCS.z = min(positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #else
                    positionCS.z = max(positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return positionCS;
            }

            half4 Frag() : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 Vert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return TransformObjectToHClip(input.positionOS.xyz);
            }

            half Frag() : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }
    }

    CustomEditor "__GAME__.Editor.Art.ToonShaderGUI"
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
