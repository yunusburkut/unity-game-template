# __GAME__

TODO: one line on the game.

Design, rules and architecture: [DESIGN.md](DESIGN.md). Current work: [PLAN.md](PLAN.md). Working with Claude:
[REHBER.md](REHBER.md).

## Open

Unity 6000.6.0f1, URP. Feel by More Mountains is a paid Asset Store package committed under `Assets/Feel` (if the
folder is missing, import Feel from the Asset Store there first), so this repository must stay private (`.gitignore` says what to do before making it public). Open
`Assets/__GAME__/Scenes/Main.unity` and press Play.

**GameKit > Set Up Project** reapplies the player and platform settings (Input System only, Main scene in the
build); the URP assets, quality levels, company, product and bundle id are created once and then left to the game.
A pack's setup step, if the game has one, keeps the same promise: it runs once and then leaves its output to the game
(the pack's own README in unity-game-template says what it touches). From the command line:

```
Unity -batchmode -quit -projectPath . -executeMethod GameKit.Editor.ProjectSetup.Run -gameCompany __COMPANY__
```

## Build

**GameKit > Build > Windows / Android (APK) / Android (AAB, Google Play) / iOS / WebGL**, or with the Editor closed:

```
Unity -batchmode -quit -projectPath . -buildTarget Android -executeMethod GameKit.Editor.BuildMenu.Android
```

The result lands in `Logs/agent/build.log`, the build in `Builds/`. **Development Build** in File > Build Profiles
makes every entry a development build with the profiler attached. The APK is for test phones (a batch build, or an
Editor session where the keystore passwords were not typed in, signs it with the debug key; build.log says so). Google Play takes the AAB,
signed with the upload keystore set in Player Settings > Publishing Settings (never committed); Unity does not save the keystore passwords, so build the AAB from the menu (or `build aab`)
in an Editor session where they have been typed in. Android needs the
Android Build Support module in Unity Hub; iOS produces an Xcode project that is built on a Mac with Xcode 26.
WebGL is Brotli-compressed for itch.io.

## Git

Scenes and prefabs merge through Unity's Smart Merge (`.gitattributes`), and a pre-commit hook in `.githooks/`
refuses an asset without its `.meta`. A fresh clone turns both on with the same settings the new game was made with
(use the Editor folder of the version in `ProjectSettings/ProjectVersion.txt`):

```
git config core.hooksPath .githooks
git config merge.unityyamlmerge.name "Unity SmartMerge"
git config merge.unityyamlmerge.driver "'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/Tools/UnityYAMLMerge.exe' merge -h -p --force --fallback none %O %B %A %A"
git config merge.unityyamlmerge.recursive binary
```
