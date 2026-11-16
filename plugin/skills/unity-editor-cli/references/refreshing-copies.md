# Refreshing the copied Unity skills (template maintainers only)

This is maintenance work in the template repo itself. In a game the copies live only in the plugin: never
refresh, merge or edit them from a game session.

`unity-cli`, `ui-ugui`, `urp-postprocessing` and `unity-package-management` are copies of the official Unity plugin's
skills (`unity@claude-plugins-official`); the plugin itself stays off because its other skills cost every session
context. The copies do not update by themselves, and they carry house edits (template rules, gamekit hand-offs) mixed
into Unity's text, so a refresh is a merge, never a copy over: take the newer upstream (`unity skill show --list` /
`--path <file>` prints the CLI's own `unity-cli` skill and writes nothing; the other three come from the plugin's newer
version, installed and kept disabled), diff it against the folder here, take the upstream changes and keep every house
edit, and keep every file the copy added (never a mirror that deletes extra reference files). The house edits are
marked near the top of each copy; re-apply any that the merge touched: `unity-cli`'s top blockquote (the gamekit
overrides: `gk-bridge` for tests and builds, no `unity mcp configure`, no `unity skill install` / `setup` without a yes,
new games via `gamekit:new-game`, Play Mode verification through `play-capture`, `allowed-tools` narrowed to
the read-only `unity` forms, the bootstrap and CI build workflows moved to `references/workflows.md`, and the gamekit
notes atop `build-run-test.md`, `playmode-verification-loop.md` and `workflows.md`), `urp-postprocessing`'s top
"House edits (gamekit)" blockquote, `unity-package-management`'s "Local
gamekit adaptations" block and `ui-ugui`'s "House rules win" list. `unity-cli` is copied from
`unity@claude-plugins-official` 0.1.9-beta (docs for CLI `1.0.0-beta.16`), as its blockquote says. Note the CLI version
the merge was aligned to in that skill's `CHANGELOG.md` (`unity-cli`) or `LICENSE.md` (the others): `urp-postprocessing`'s records 0.1.6-beta merged up to 0.1.9-beta;
`ui-ugui`'s and `unity-package-management`'s do not record theirs yet, so add it at their next merge.

After a merge, recheck the CLI-specific claims in `unity-editor-cli/SKILL.md` (command names, `script run` and its 60 s
default, the 5 s `script eval` budget, `capture game_view` paths) against the installed `unity --version`, and update
the version that file says they were checked on.
