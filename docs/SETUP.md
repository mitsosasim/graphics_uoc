# Run every assignment on your PC

## Windows: prepare the Python graphics environment

1. Install **Python 3.10 (64-bit)** and **Git for Windows**. Enable Python's launcher when installing. Use a desktop session with an OpenGL 4.1-capable graphics driver. Update your Intel/NVIDIA/AMD driver if context creation fails. The runner game itself does not require Python. The archive reconstruction command uses Python.
2. Open PowerShell in the folder where you keep projects. Clone this collection:

   ```powershell
   git clone https://github.com/mitsosasim/graphics_uoc.git
   cd graphics_uoc
   py -3.10 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Download the **graphics teaching framework**, not the unrelated `elements` package on PyPI:

   ```powershell
   git clone https://github.com/papagiannakis/Elements.git vendor/Elements
   git -C vendor/Elements checkout 7617f647dee71d9978adca0db0e3a99324f245b3
   ```

   Keep the checkout in this exact location. The launcher adds it to Python's import path, so you do not need to install the framework's unrelated optional notebook/ML packages. The pinned revision supplies the APIs, Earth texture, and cloudy cubemap used here.

4. From the **repository root**, launch each example separately:

   ```powershell
   .\.venv\Scripts\python.exe tools/run.py 1.1
   .\.venv\Scripts\python.exe tools/run.py 1.2
   .\.venv\Scripts\python.exe tools/run.py 1.3
   .\.venv\Scripts\python.exe tools/run.py 2.1
   .\.venv\Scripts\python.exe tools/run.py 2.2
   .\.venv\Scripts\python.exe tools/run.py 3.1
   ```

   Close a window before running the next command. `--elements "C:\path\to\Elements"` selects a different framework location. Windows commands are provided for your PC, while the render runs here were verified on Linux.

## What to try in each window

| Exercise | What you see | What to do |
| --- | --- | --- |
| 1.1 | Indexed wireframe sphere | Explore the camera panel. Extra sphere variants are commented examples in the code, not active runtime modes. |
| 1.2 | Two cubes, a pyramid, axes and grid | Use **TRS Controls** for object/group translation, rotation, scale, and visibility. Drag overlapping GUI panels by their title bars. |
| 1.3 | Triangle, line and point primitives | Explore the camera and inspect their separate mesh/primitive setups. |
| 2.1 | Two colored cubes and a pyramid | Open **Color & Lighting Controls**, change material colors, lighting and shininess. |
| 2.2 | Sphere, orbiting light and cloudy skybox | Change **Lighting Settings** for the two lights and ambient contribution. The sphere does not display a recognizable Earth texture in the verified run. |
| 3.1 | Joint-weighted wireframe object | Enlarge the **ANIMATION** panel if labels are clipped. Toggle **Play Animation** for the two-keyframe loop. Turn it off to drag each joint angle manually. |

The native ImGui panels may overlap on first launch. Move/collapse them to inspect the scene. Framework camera controls are in the main ImGui panel. Use the window close button to exit. No web server is involved.

## Assignment 3: open the Maya animation

1. Install/open Autodesk Maya. The binary scene metadata identifies **Maya 2025**. Maya is proprietary and is not bundled with this collection.
2. Choose **File → Open Scene**, then open `assignments/03/ex32_4845.mb`.
3. Select the geometry in the Outliner and press **F** to frame it. Set the playback range to include the animation keys visible in the timeline.
4. Press Play and inspect the joint hierarchy and keyframes. The original submission describes nine differently shaped cubes arranged in an L with five keyframes. This description is historical, since Maya execution was unavailable here.
5. The original submission separately links a Unity solar-system exercise: <https://drive.google.com/drive/folders/136uNvAFv26qZPFnFzKZJTvgbsd0EoYwd>. Those files are not in the supplied archives and are not claimed as verified. If you have access, download the entire project and open its `Assets`, `Packages`, and `ProjectSettings` directory through Unity Hub.

## Assignment 4: play the Windows runner game

1. From the repository root, run `python tools/restore_game.py`. Then open `build/runner-windows.zip` in File Explorer and choose **Extract All**. Use a normal writable folder outside the ZIP.
2. Keep **all extracted files together**. `Runner Game.exe`, `UnityPlayer.dll`, `Runner Game_Data`, and `MonoBleedingEdge` are required siblings. Moving just the EXE breaks the game.
3. Double-click **Runner Game.exe**. Unity Editor is not required to play this build. The build metadata identifies Unity **2022.3.22f1**.
4. Use the game's own menu and on-screen instructions. Exact movement keys and gameplay flow have not been verified here, so this guide does not invent a control scheme.
5. To edit or rebuild it, obtain the original Unity project. This ZIP is a compiled Windows player and cannot be opened in Unity Hub as an editable project.

The Windows game could not be run in this environment. A Wine launch attempt failed before game startup. No game or Maya screenshot is presented as a verified run.

## Linux and screenshot reproduction

Use Python 3.10 in a virtual environment, then the same `pip install -r requirements.txt`, framework checkout, and `python tools/run.py EXERCISE` commands. A local desktop requires SDL2/OpenGL support. Headless rendering was verified using the SDL offscreen driver and Mesa:

```sh
SDL_VIDEODRIVER=offscreen PYOPENGL_PLATFORM=egl LIBGL_ALWAYS_SOFTWARE=1 \
python tools/run.py 2.1 --capture build/lighting.png --frames 60
```

Replace `2.1` with any of the six exercise IDs. Captures read actual OpenGL framebuffer pixels before GUI overlays. Exercise 1.2's capture uses a wider camera view to frame the group. No geometry or output is synthesized. The default interactive invocation preserves the exercise's camera behavior.

## Troubleshooting and implementation scope

- `No module named Elements`: check `vendor/Elements/Elements` exists, the pinned checkout succeeded, and you are using the launcher.
- OpenGL context/GLX errors: use a hardware desktop driver with OpenGL 4.1+, or the tested Linux offscreen command. Remote desktop/VM software can expose insufficient OpenGL support.
- Do not install the unrelated PyPI package named `elements`. Use the Git checkout above.
- Import paths for the ImGui decorators were adapted to the pinned framework. An unused Unix-only `curses` import was removed for Windows compatibility.
- Assignment 2 loads its supplied `Shader.py` through the launcher. Exercise 2.2 creates the texture after context initialization. Its missing `Stars2.0` assets were replaced by the framework's bundled **Cloudy** JPEG cubemap. This is a documented asset substitution, not the original star background.
- The texture/UV/shading result in 2.2 remains a known limitation. The original submission reported a black Earth texture. The present scene renders, but does not validate correct Earth mapping.
