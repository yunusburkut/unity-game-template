# __GAME__

TODO: one line on the game.

The plan, the rules and the architecture are in [DESIGN.md](DESIGN.md).

## Open

Unity 6000.6.0f1, URP. Feel by More Mountains is a paid Asset Store package and is not in the repository: import it
from the Asset Store into `Assets/Feel` first. Then open `Assets/__GAME__/Scenes/Main.unity` and press Play.

**__GAME__ > Set Up Project** reapplies the player and platform settings (Input System only, Main scene in the
build); the URP assets, quality levels, company, product and bundle id are created once and then left to the game.
A pack's setup step may reapply its own settings (mobile-2d resets the URP renderer lists, Main's lights and camera). From the command line:

```
Unity -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.ProjectSetup.Run
```

## Build

**__GAME__ > Build > Windows / Android (APK) / Android (AAB, Google Play) / iOS / WebGL**, or with the Editor closed:

```
Unity -batchmode -quit -projectPath . -buildTarget Android -executeMethod __GAME__.Editor.BuildMenu.Android
```

The result lands in `Logs/agent/build.log`, the build in `Builds/`. **Development Build** in File > Build Profiles
makes every entry a development build with the profiler attached. The APK is for test phones (a batch build signs it
with the debug key). Google Play takes the AAB, signed with the upload keystore set in Player Settings > Publishing
Settings (never committed); Unity does not save the keystore passwords, so build the AAB from the menu (or `build aab`)
in an Editor session where they have been typed in. Android needs the
Android Build Support module in Unity Hub; iOS produces an Xcode project that is built on a Mac with Xcode 26.
WebGL is Brotli-compressed for itch.io.

## Git

Scenes and prefabs merge through Unity's Smart Merge (`.gitattributes`), and a pre-commit hook in `.githooks/`
refuses an asset without its `.meta`. A fresh clone turns both on with:

```
git config core.hooksPath .githooks
git config merge.unityyamlmerge.driver "'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/Tools/UnityYAMLMerge.exe' merge -h -p --force --fallback none %O %B %A %A"
```
