# Non-Steam Shortcut Extension for Playnite

This extension will automatically creates non-Steam shortcuts for the currently selected games in Playnite. Multiple games can be highlighted to create multiple shortcuts at once. The game in Playnite will be modified to launch the game using Steam.

Rerunning this extension is safe, it will update the shortcut with the information from the OtherAction titled "Launch without Steam".

Warning: Any existing non-Steam shortcut with the same name (`AppName`) as a game in your Playnite library will be replaced with an updated shortcut. This allows updating shortcuts, but may potentially clobber some of your existing non-Steam shortcuts.

This effectively allows using the Steam overlay for any game in Playnite.

## Installation

1. [Download](https://github.com/bburky/playnite-non-steam-shortcuts/archive/master.zip) this extension
2. Extract the extension into a new folder in your "Extensions" folder in your Playnite library.
3. Update `STEAM_USERDATA` at the top of `nonsteam.py` manually to be the location of your Steam profile's userdata directory, including your Steam ID.
4. Relaunch Playnite or select "Tools" → "Reload Scripts".

You should have a new folder in your `Extensions` folder called `playnite-non-steam-shortcuts` containing `extension.yaml` and `nonsteam.py`.

Select some games and chose "Extensions" → "Create non-Steam shortcuts for selected games" in the menu. Then relaunch Steam to update it's non-Steam shortcuts.

## Sources used for shortcut.vdf reverse engineering

*  https://github.com/tirish/steam-shortcut-editor/blob/master/lib/parser.js

    Has a fairly easy to follow VDF parser. The `parseObjectValue()` function recursively calls everything else.

*   https://github.com/CorporalQuesadilla/Steam-Shortcut-Manager/wiki/Steam-Shortcuts-Documentation

    No code used other than the CRC algorithm, which is originally from https://github.com/scottrice/Ice (and is MIT licensed).
