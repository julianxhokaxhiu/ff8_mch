# FF8 MCH: Blender plugin for Field models

FF8 MCH is a Blender plugin that allows to import/export .MCH field model files for Final Fantasy VIII

## Installation

0. Install [Blender 4.3](https://www.blender.org/download/releases/4-3/)
1. Download this repository [as a ZIP](https://github.com/julianxhokaxhiu/ff8_mch/archive/refs/heads/master.zip)
2. Edit -> Preferences -> Add-ons -> Install from Disk...
3. Pick the ZIP you downloaded
4. Enable `FF8 MCH Field Models`
5. Import/Export using the relative `File -> Import/Export -> FF8 Field Model` menu

## Development setup

### Visual Studio Code

0. Install [Python](https://www.python.org/)
1. Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
2. Install https://github.com/hextantstudios/hextant_python_debugger
3. Install https://github.com/nutti/fake-bpy-module ( `pip install fake-bpy-module` )
4. Start the debugger: Blender icon -> System -> Start Debug Server
5. Clone this project in the Blender addon path
    - Windows: `%appdata%\Blender Foundation\Blender\4.3\scripts\addons\`
    - Mac: `/Users/$USER/Library/Application Support/Blender/4.3/scripts/addons/`
    - Linux: `$HOME/.config/blender/4.3/scripts/addons/`
6. Open the `ff8_mch` folder in Visual Studio Code
7. Press `F5` on Visual Studio Code
6. Run the extension in Blender

## Credits

Original Blender plugin was authored by [Shunsq](https://forums.qhimm.com/index.php?action=profile;u=23158).

### License

FF8 MCH is released under GPLv3 license. You can get a copy of the license here: [COPYING.txt](COPYING.txt)

If you paid for FF8 MCH, remember to ask for a refund from the person who sold you a copy. Also make sure you get a copy of the source code (if it was provided as binary only).

If the person who gave you this copy refuses to give you the source code, report it here: https://www.gnu.org/licenses/gpl-violation.html

All rights belong to their respective owners.
