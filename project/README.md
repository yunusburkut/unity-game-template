# __GAME__

TODO: one line on the game.

The plan, the rules and the architecture are in [DESIGN.md](DESIGN.md).

## Open

Unity 6000.6.0f1, URP. Feel by More Mountains is a paid Asset Store package and is not in the repository: import it
from the Asset Store into `Assets/Feel` first. Then open `Assets/__GAME__/Scenes/Main.unity` and press Play.

**__GAME__ > Set Up Project** reapplies the platform setup (URP Mobile and PC tiers, Input System only, Main scene in
the build). From the command line:

```
Unity -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.ProjectSetup.Run
```

## Build

**__GAME__ > Build > Windows / Android / iOS / WebGL**, or with the Editor closed:

```
Unity -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.BuildMenu.Android
```

The result lands in `Logs/agent/build.log`, the build in `Builds/`. Android needs the Android Build Support module in
Unity Hub; iOS produces an Xcode project that is built on a Mac.
