// A flat cel sky to go with Toon: light at the horizon, darker toward the top, no clouds, and a pale sun disc with one
// halo band (two flat steps, no glow gradient). The disc is here, not a mesh: a mesh far enough away to sit still
// would lie past the fog's end and fog out. One unlit skybox pass on the view direction. Use it from a material set as
// RenderSettings.skybox (Lighting > Environment); _SunDirection is where the disc shows and need not follow the light.
Shader "__GAME__/Sky"
{
    Properties
    {
        _TopColor("Top", Color) = (0.47, 0.64, 0.88, 1)
        _HorizonColor("Horizon", Color) = (0.8, 0.86, 0.92, 1)
        _Exponent("Falloff", Range(0.1, 4)) = 0.6
        _SunDirection("Sun direction", Vector) = (0.6, 0.45, 0.66, 0)
        _SunColor("Sun", Color) = (1, 0.96, 0.84, 1)
        _SunSize("Sun radius (deg)", Range(0.5, 10)) = 3.2
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _TopColor;
                half4 _HorizonColor;
                half _Exponent;
                float4 _SunDirection;
                half4 _SunColor;
                half _SunSize;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings { float4 positionCS : SV_POSITION; float3 direction : TEXCOORD0; UNITY_VERTEX_OUTPUT_STEREO };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.direction = input.positionOS.xyz;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                // below the horizon keeps the horizon colour: the ground and the fog cover it
                float3 view = normalize(input.direction);
                half up = saturate(view.y);
                half3 sky = lerp(_HorizonColor.rgb, _TopColor.rgb, pow(up, _Exponent));
                // the disc, then a halo band twice its radius at a third of its strength: hard edges, cel steps
                float toward = dot(view, normalize(_SunDirection.xyz));
                float radius = radians(_SunSize);
                half step = toward > cos(radius) ? 1.0 : (toward > cos(radius * 2.0) ? 0.3 : 0.0);
                return half4(lerp(sky, _SunColor.rgb, step), 1.0);
            }
            ENDHLSL
        }
    }
}
