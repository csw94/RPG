# Chronicles of Pixel

A Korean language, top down RPG built with Pygame CE. Explore the field with
WASD or the arrow keys, open treasure with Space, and fight turn based battles.
Press F5 or click **저장** to save. Escape saves and returns to the title.

## Download and run on Windows

1. Open the [latest release](https://github.com/csw94/RPG/releases/latest).
2. Download **ChroniclesOfPixel.exe** from the release assets.
3. Double click the downloaded EXE to play. No Python installation is needed.

The game stores saves in your Windows application data folder. The EXE includes
the Korean font and does not need a separate assets folder.

## Run from source

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Build a single Windows executable

```powershell
pyinstaller --onefile --windowed --add-data "assets;assets" --name "ChroniclesOfPixel" main.py
```

The map, player, chests, and monsters use shape based rendering, so external
image assets are not required. The bundled font license is in `assets/fonts/OFL.txt`.
