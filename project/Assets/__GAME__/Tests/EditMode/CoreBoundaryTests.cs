using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using __GAME__.Core;
using NUnit.Framework;
using UnityEngine;

namespace __GAME__.Tests.EditMode
{
    /// <summary>
    /// Core is the deterministic simulation (CLAUDE.md, Assembly boundary). The compiler cannot tell a
    /// <c>Time.deltaTime</c> in Core from one in Game, so these checks make a breach fail the EditMode run
    /// instead of waiting for a reviewer to notice it.
    /// Ceiling: the source scan is a token list, not a parser. It ignores // comments but not strings or
    /// block comments; a new banned API goes into <see cref="Banned"/>.
    /// </summary>
    public sealed class CoreBoundaryTests
    {
        static readonly System.Reflection.Assembly Core = typeof(Ease).Assembly;

        // Engine assemblies Core must never link against: physics, the old input manager, the Input System,
        // the Editor. Mathf, vectors and data-only ScriptableObject configs live in CoreModule and stay allowed.
        static readonly string[] BannedAssemblies =
        {
            "UnityEngine.PhysicsModule", "UnityEngine.Physics2DModule", "UnityEngine.InputLegacyModule",
            "UnityEngine.InputModule", "Unity.InputSystem", "UnityEditor",
        };

        // The APIs CLAUDE.md bans from Core. Time, GameObject, SceneManager, Random, Screen and the rest live in
        // CoreModule, so only the source can show them. UnityEngine.Random is global state (seed a System.Random
        // or a Core RNG struct instead); Screen, Camera, Application, PlayerPrefs and Resources are scene or
        // platform state; Instantiate, Destroy and the Find*Object* searches make or reach scene objects, called
        // bare (inside a ScriptableObject) or as Object.X / UnityEngine.Object.X (from a static Core function).
        // The lookbehind lets a Core field or method of the same name (state.Time, state.Random, pool.Destroy(x))
        // and System.Random through.
        static readonly Regex Banned = new Regex(
            @"\b(MonoBehaviour|GameObject|SceneManager|SceneManagement)\b" +
            @"|(?<![\w.])(Time|Input|Physics|Physics2D|Random|Screen|Camera|Application|PlayerPrefs|Resources)\.\w" +
            @"|\bUnityEngine\.(Time|Input|Physics|Physics2D|Random|Screen|Camera|Application|PlayerPrefs|Resources)\b" +
            @"|(?<![\w.])(?:(?:UnityEngine\.)?Object\.)?" +
            @"(Instantiate|Destroy|DestroyImmediate|Find(?:Any|First)?Objects?(?:OfType|ByType))\s*[<(]",
            RegexOptions.Compiled);

        [Test]
        public void Core_DeclaresNoComponent()
        {
            var components = Core.GetTypes().Where(t => typeof(Component).IsAssignableFrom(t)).ToArray();
            Assert.IsEmpty(components, "Core bileşen (MonoBehaviour) tanımlamamalı: " +
                                       string.Join(", ", components.Select(t => t.FullName)));
        }

        [Test]
        public void Core_HoldsNoSceneOrAssetReference()
        {
            // A Core config is data only (CLAUDE.md): a Transform, Camera, GameObject, Material or Sprite field is
            // a managed reference the simulation must not hold. Another ScriptableObject config may nest.
            const System.Reflection.BindingFlags all = System.Reflection.BindingFlags.Instance |
                System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public |
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly;

            var fields = Core.GetTypes()
                .SelectMany(t => t.GetFields(all).Select(f => new { t, f }))
                .Where(x => ReferencedTypes(x.f.FieldType).Any(r =>
                    typeof(Object).IsAssignableFrom(r) && !typeof(ScriptableObject).IsAssignableFrom(r)))
                .Select(x => x.t.FullName + "." + x.f.Name + " : " + x.f.FieldType.Name)
                .ToArray();

            Assert.IsEmpty(fields, "Core sahne/asset referansı tutmamalı (yalnız ScriptableObject config); " +
                                   "bunlar Game'e ait:\n" + string.Join("\n", fields));
        }

        [Test]
        public void Core_TakesOrReturnsNoSceneOrAssetReference()
        {
            // A Core solver must not take a Transform (or any scene/asset object) and write to it, nor hand one
            // back: the Game glue reads the scene and passes values. Properties are covered by their accessors.
            const System.Reflection.BindingFlags all = System.Reflection.BindingFlags.Instance |
                System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public |
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly;
            System.Type generated = typeof(System.Runtime.CompilerServices.CompilerGeneratedAttribute);

            var members = Core.GetTypes()
                .Where(t => !t.IsDefined(generated, true))
                .SelectMany(t => t.GetMethods(all).Where(m => !m.IsDefined(generated, false)).Select(m => new { t, m }))
                .SelectMany(x => x.m.GetParameters().Select(p => p.ParameterType).Append(x.m.ReturnType)
                    .Where(type => ReferencedTypes(type).Any(r =>
                        typeof(Object).IsAssignableFrom(r) && !typeof(ScriptableObject).IsAssignableFrom(r)))
                    .Select(type => x.t.FullName + "." + x.m.Name + " : " + type.Name))
                .Distinct()
                .ToArray();

            Assert.IsEmpty(members, "Core metodu sahne/asset nesnesi almamalı ya da döndürmemeli (değer olarak " +
                                    "Game'den gelir):\n" + string.Join("\n", members));
        }

        // The field's type plus what an array or generic (List<T>, T[]) holds.
        static System.Collections.Generic.IEnumerable<System.Type> ReferencedTypes(System.Type type)
        {
            yield return type;
            if (type.HasElementType)
                foreach (var t in ReferencedTypes(type.GetElementType())) yield return t;
            if (type.IsGenericType)
                foreach (var t in type.GetGenericArguments().SelectMany(ReferencedTypes)) yield return t;
        }

        [Test]
        public void Core_LinksNoSceneOrInputAssembly()
        {
            var linked = Core.GetReferencedAssemblies().Select(a => a.Name)
                             .Where(n => BannedAssemblies.Any(b => n == b || n.StartsWith(b + ".")))
                             .ToArray();
            Assert.IsEmpty(linked, "Core bu assembly'lere bağlanmamalı: " + string.Join(", ", linked));
        }

        [Test]
        public void CoreSource_UsesNoSceneOrFrameApi()
        {
            string folder = Path.Combine(Application.dataPath, "__GAME__", "Core");
            Assert.IsTrue(Directory.Exists(folder), "Core klasörü bulunamadı: " + folder);

            var hits = Directory.GetFiles(folder, "*.cs", SearchOption.AllDirectories)
                .SelectMany(file => File.ReadAllLines(file).Select((line, i) => new { file, line, i }))
                .Select(x => new { x.file, x.i, code = StripLineComment(x.line) })
                .Where(x => Banned.IsMatch(x.code))
                .Select(x => Path.GetFileName(x.file) + ":" + (x.i + 1) + "  " + x.code.Trim())
                .ToArray();

            Assert.IsEmpty(hits, "Core sahne/kare API'si kullanmamalı (Time, Input, Physics, Random, Screen, " +
                                 "Camera, Application, PlayerPrefs, Resources, Instantiate/Destroy ve sahne tipleri " +
                                 "Game'e ait; dt parametre olarak gelir):\n" + string.Join("\n", hits));
        }

        [Test]
        public void Prototypes_StayOutsideCoreAndGame()
        {
            // A Prototypes/<Name> asmdef is throwaway (gamekit:prototype): it may use Core, never Game, and
            // nothing shipped or tested may use it (Core, Game, the test assemblies), or deleting the folder with
            // its verdict breaks the build.
            // Ceiling: it sees only loaded assemblies; an Editor-only prototype is loaded in the Editor, which
            // is where this runs.
            string core = Core.GetName().Name;
            string game = core.Substring(0, core.Length - ".Core".Length) + ".Game";
            var loaded = System.AppDomain.CurrentDomain.GetAssemblies();

            var breaches = loaded
                .Select(a => new { name = a.GetName().Name, refs = a.GetReferencedAssemblies().Select(r => r.Name).ToArray() })
                .SelectMany(a =>
                    a.name.Contains(".Prototypes.")
                        ? a.refs.Where(r => r == game).Select(r => a.name + " -> " + r)
                        : a.name == core || a.name == game || a.name.Contains(".Tests")
                            ? a.refs.Where(r => r.Contains(".Prototypes.")).Select(r => a.name + " -> " + r)
                            : Enumerable.Empty<string>())
                .ToArray();

            Assert.IsEmpty(breaches, "Prototip Game'e bağlanmamalı; Core/Game/testler de prototipe bağlanmamalı:\n" +
                                     string.Join("\n", breaches));
        }

        [Test]
        public void Prototypes_StayOutOfPlayerBuilds()
        {
            // gamekit:prototype section 3: a prototype asmdef is never auto-referenced and compiles only in the
            // Editor. The one exception is a device test, which drops UNITY_EDITOR while PLAN.md's
            // `prototype <Name>: ..., first scene was <path>` line records how to restore it.
            string folder = Path.Combine(Application.dataPath, "__GAME__", "Prototypes");
            if (!Directory.Exists(folder)) return;
            string planPath = Path.Combine(Path.GetDirectoryName(Application.dataPath), "PLAN.md");
            string[] plan = File.Exists(planPath) ? File.ReadAllLines(planPath) : new string[0];

            var breaches = Directory.GetFiles(folder, "*.asmdef", SearchOption.AllDirectories)
                .SelectMany(file =>
                {
                    string json = File.ReadAllText(file);
                    string name = Path.GetFileName(Path.GetDirectoryName(file));
                    bool deviceTest = plan.Any(l => l.Contains("prototype " + name + ":") && l.Contains("first scene was"));
                    var problems = new System.Collections.Generic.List<string>();
                    if (!Regex.IsMatch(json, @"""autoReferenced""\s*:\s*false"))
                        problems.Add(Path.GetFileName(file) + ": \"autoReferenced\": false yok");
                    if (!deviceTest && !Regex.IsMatch(json, @"""defineConstraints""\s*:\s*\[[^\]]*""UNITY_EDITOR"""))
                        problems.Add(Path.GetFileName(file) + ": \"defineConstraints\": [\"UNITY_EDITOR\"] yok " +
                                     "(cihaz testi değilse; PLAN.md'de 'first scene was' notu yok)");
                    return problems;
                })
                .ToArray();

            Assert.IsEmpty(breaches, "Prototip player build'e girmemeli:\n" + string.Join("\n", breaches));
        }

        static string StripLineComment(string line)
        {
            int at = line.IndexOf("//", System.StringComparison.Ordinal);
            return at < 0 ? line : line.Substring(0, at);
        }
    }
}
