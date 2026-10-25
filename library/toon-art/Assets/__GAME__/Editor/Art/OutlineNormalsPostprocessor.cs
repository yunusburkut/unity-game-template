using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace __GAME__.Editor.Art
{
    /// <summary>
    /// Writes a smoothed normal into the tangent (xyz, w = 0) of every mesh imported under <see cref="ModelsFolder"/>,
    /// so the toon outline's inverted hull is pushed out along one direction per corner and stays closed where the mesh
    /// has a hard edge. The tangent, not a UV channel, because skinning moves it with the bones; nothing else reads it
    /// (the toon shader has no normal maps). A model elsewhere keeps its own tangents, and the shader falls back to its
    /// normal. This changes the import, never the file.
    /// </summary>
    internal sealed class OutlineNormalsPostprocessor : AssetPostprocessor
    {
        const string ModelsFolder = "Assets/__GAME__/Game/Art/Models/";

        // Raise when the folder or the bake changes, so the models reimport.
        public override uint GetVersion() => 1;

        void OnPostprocessModel(GameObject root)
        {
            if (!assetPath.StartsWith(ModelsFolder)) return;
            foreach (MeshFilter f in root.GetComponentsInChildren<MeshFilter>(true)) Bake(f.sharedMesh);
            foreach (SkinnedMeshRenderer s in root.GetComponentsInChildren<SkinnedMeshRenderer>(true)) Bake(s.sharedMesh);
        }

        static void Bake(Mesh mesh)
        {
            if (mesh == null) return;
            Vector3[] positions = mesh.vertices;
            Vector3[] normals = mesh.normals;
            if (normals.Length != positions.Length) return;

            // Vertices split at a hard edge or a UV seam share a position. Each distinct face direction counts once, so a
            // seam's duplicate does not pull the corner toward one face: a cube corner gets the diagonal.
            var groups = new Dictionary<Vector3Int, List<Vector3>>();
            var keys = new Vector3Int[positions.Length];
            for (int i = 0; i < positions.Length; i++)
            {
                Vector3Int key = Vector3Int.RoundToInt(positions[i] * 10000f);
                keys[i] = key;
                if (!groups.TryGetValue(key, out List<Vector3> seen)) groups[key] = seen = new List<Vector3>(4);
                if (!seen.Exists(n => Vector3.Dot(n, normals[i]) > 0.999f)) seen.Add(normals[i]);
            }

            var tangents = new Vector4[positions.Length];
            for (int i = 0; i < positions.Length; i++)
            {
                Vector3 sum = Vector3.zero;
                foreach (Vector3 n in groups[keys[i]]) sum += n;
                Vector3 smooth = sum.sqrMagnitude > 1e-6f ? sum.normalized : normals[i];
                tangents[i] = new Vector4(smooth.x, smooth.y, smooth.z, 0f);
            }
            mesh.tangents = tangents;
        }
    }
}
