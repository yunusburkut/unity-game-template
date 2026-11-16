// Asset import audit for `unity command script run --file <this file's absolute path> --timeout 120`.
// Read-only: it changes no importer. Writes the table to <project>/Temp/asset-audit.txt (outside Assets/,
// so no import) and returns the same text. Judge each row against unity-performance SKILL.md "Asset audit".
// Ceiling: it lists every texture and clip under Folder in one pass; on a very large project set Folder to
// one art folder (Assets/<Game>/Art) per run to stay inside the timeout. Vendored trees are skipped: their import
// settings are the vendor's and an unreferenced file there never ships; add a folder to Vendored when a pack adds one.
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

public static class AssetAudit
{
    const string Folder = "Assets";
    static readonly string[] Platforms = { "Standalone", "Android", "iPhone", "WebGL" };
    static readonly string[] Vendored = { "Assets/Feel/", "Assets/Plugins/", "Assets/TextMesh Pro/" };

    static bool IsVendored(string path) =>
        System.Array.Exists(Vendored, v => path.StartsWith(v, System.StringComparison.Ordinal));

    public static string Run()
    {
        var sb = new StringBuilder();

        sb.AppendLine("## Textures");
        sb.AppendLine("path\ttype\tsource_wxh\tread_write\tmipmaps\tnpot_scale\t" +
                      "default(max/format)\tStandalone\tAndroid\tiPhone\tWebGL");
        foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { Folder }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            if (IsVendored(path)) continue;
            if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
            ti.GetSourceTextureWidthAndHeight(out var w, out var h);
            var def = ti.GetDefaultPlatformTextureSettings();
            sb.Append(path).Append('\t').Append(ti.textureType).Append('\t').Append(w).Append('x').Append(h)
              .Append('\t').Append(ti.isReadable ? "ON" : "off")
              .Append('\t').Append(ti.mipmapEnabled ? "on" : "off")
              .Append('\t').Append(ti.npotScale)
              .Append('\t').Append(def.maxTextureSize).Append('/').Append(def.format);
            foreach (var p in Platforms)
            {
                var s = ti.GetPlatformTextureSettings(p);
                sb.Append('\t').Append(s.overridden ? s.maxTextureSize + "/" + s.format : "-");
            }
            sb.AppendLine();
        }

        sb.AppendLine().AppendLine("## Audio");
        sb.AppendLine("path\tlength_s\tforce_mono\tdefault(load/format/quality)\tAndroid\tiPhone\tWebGL");
        foreach (var guid in AssetDatabase.FindAssets("t:AudioClip", new[] { Folder }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            if (IsVendored(path)) continue;
            if (!(AssetImporter.GetAtPath(path) is AudioImporter ai)) continue;
            var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
            var d = ai.defaultSampleSettings;
            sb.Append(path).Append('\t').Append(clip != null ? clip.length.ToString("F1") : "?")
              .Append('\t').Append(ai.forceToMono ? "on" : "off")
              .Append('\t').Append(d.loadType).Append('/').Append(d.compressionFormat).Append('/')
              .Append(d.quality.ToString("F2"));
            foreach (var p in new[] { "Android", "iPhone", "WebGL" })
            {
                if (!ai.ContainsSampleSettingsOverride(p)) { sb.Append("\t-"); continue; }
                var s = ai.GetOverrideSampleSettings(p);
                sb.Append('\t').Append(s.loadType).Append('/').Append(s.compressionFormat);
            }
            sb.AppendLine();
        }

        var text = sb.ToString();
        var outPath = Path.Combine(Directory.GetCurrentDirectory(), "Temp", "asset-audit.txt");
        File.WriteAllText(outPath, text);
        Debug.Log("AssetAudit: " + outPath);
        return text;
    }
}
