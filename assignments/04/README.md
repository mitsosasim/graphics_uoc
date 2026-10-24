# Unity runner game

A packaged Windows Unity player from the graphics course. The build contains compiled game scripts, four serialized level files, assets, the Unity player, and the Mono runtime. The editable Unity project is not included.

**Unity 2022.3.22f1 player · Windows x64 · managed C# assembly**

Clone or download this repository, then run `python tools/restore_game.py` from its root. It verifies and reconstructs the exact original ZIP at `build/runner-windows.zip` from the [packaged parts](windows-build).

1. Extract the complete ZIP into a writable folder.
2. Keep the executable, `UnityPlayer.dll`, `Runner Game_Data`, and `MonoBleedingEdge` together.
3. Start `Runner Game.exe` on Windows. Unity Editor is not required.
4. Follow the in-game menu/instructions. Controls and gameplay were not verified in this environment.

The supplied archive is preserved byte for byte through verified split parts. A Wine attempt did not reach game startup, so no runtime screenshot or gameplay claim is supplied. Editing/rebuilding requires the original Unity project.

[Full PC guide](../../docs/SETUP.md#assignment-4-play-the-windows-runner-game) · [Collection overview](../../README.md)
