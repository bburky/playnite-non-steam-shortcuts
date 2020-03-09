# Non-Steam Shortcuts


# Please edit the following line to the location of your profile's Steam
# userdata directory, including your steam user ID:
# (Do not include a trailing backslash.)
STEAM_USERDATA = r"C:\Program Files (x86)\Steam\userdata\12345678"



# Do not edit anything below this line
###############################################################################

### crc_algorithms.py (Playnite won't import python files)

#  pycrc -- parameterisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2013  Thomas Pircher  <tehpeh@gmx.net>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.


"""
CRC algorithms implemented in Python.
If you want to study the Python implementation of the CRC routines, then this
is a good place to start from.

The algorithms Bit by Bit, Bit by Bit Fast and Table-Driven are implemented.

This module can also be used as a library from within Python.

Examples
========

This is an example use of the different algorithms:

>>> from crc_algorithms import Crc
>>>
>>> crc = Crc(width = 16, poly = 0x8005,
...           reflect_in = True, xor_in = 0x0000,
...           reflect_out = True, xor_out = 0x0000)
>>> print("0x%x" % crc.bit_by_bit("123456789"))
>>> print("0x%x" % crc.bit_by_bit_fast("123456789"))
>>> print("0x%x" % crc.table_driven("123456789"))
"""

# Class Crc
###############################################################################
class Crc(object):
    """
    A base class for CRC routines.
    """

    # Class constructor
    ###############################################################################
    def __init__(self, width, poly, reflect_in, xor_in, reflect_out, xor_out, table_idx_width = None):
        """The Crc constructor.

        The parameters are as follows:
            width
            poly
            reflect_in
            xor_in
            reflect_out
            xor_out
        """
        self.Width          = width
        self.Poly           = poly
        self.ReflectIn      = reflect_in
        self.XorIn          = xor_in
        self.ReflectOut     = reflect_out
        self.XorOut         = xor_out
        self.TableIdxWidth  = table_idx_width

        self.MSB_Mask = 0x1 << (self.Width - 1)
        self.Mask = ((self.MSB_Mask - 1) << 1) | 1
        if self.TableIdxWidth != None:
            self.TableWidth = 1 << self.TableIdxWidth
        else:
            self.TableIdxWidth = 8
            self.TableWidth = 1 << self.TableIdxWidth

        self.DirectInit = self.XorIn
        self.NonDirectInit = self.__get_nondirect_init(self.XorIn)
        if self.Width < 8:
            self.CrcShift = 8 - self.Width
        else:
            self.CrcShift = 0


    # function __get_nondirect_init
    ###############################################################################
    def __get_nondirect_init(self, init):
        """
        return the non-direct init if the direct algorithm has been selected.
        """
        crc = init
        for i in range(self.Width):
            bit = crc & 0x01
            if bit:
                crc^= self.Poly
            crc >>= 1
            if bit:
                crc |= self.MSB_Mask
        return crc & self.Mask


    # function reflect
    ###############################################################################
    def reflect(self, data, width):
        """
        reflect a data word, i.e. reverts the bit order.
        """
        x = data & 0x01
        for i in range(width - 1):
            data >>= 1
            x = (x << 1) | (data & 0x01)
        return x


    # function bit_by_bit
    ###############################################################################
    def bit_by_bit(self, in_str):
        """
        Classic simple and slow CRC implementation.  This function iterates bit
        by bit over the augmented input message and returns the calculated CRC
        value at the end.
        """
        register = self.NonDirectInit
        for c in in_str:
            octet = ord(c)
            if self.ReflectIn:
                octet = self.reflect(octet, 8)
            for i in range(8):
                topbit = register & self.MSB_Mask
                register = ((register << 1) & self.Mask) | ((octet >> (7 - i)) & 0x01)
                if topbit:
                    register ^= self.Poly

        for i in range(self.Width):
            topbit = register & self.MSB_Mask
            register = ((register << 1) & self.Mask)
            if topbit:
                register ^= self.Poly

        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        return register ^ self.XorOut


    # function bit_by_bit_fast
    ###############################################################################
    def bit_by_bit_fast(self, in_str):
        """
        This is a slightly modified version of the bit-by-bit algorithm: it
        does not need to loop over the augmented bits, i.e. the Width 0-bits
        wich are appended to the input message in the bit-by-bit algorithm.
        """
        register = self.DirectInit
        for c in in_str:
            octet = ord(c)
            if self.ReflectIn:
                octet = self.reflect(octet, 8)
            for i in range(8):
                topbit = register & self.MSB_Mask
                if octet & (0x80 >> i):
                    topbit ^= self.MSB_Mask
                register <<= 1
                if topbit:
                    register ^= self.Poly
            register &= self.Mask
        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        return register ^ self.XorOut


    # function gen_table
    ###############################################################################
    def gen_table(self):
        """
        This function generates the CRC table used for the table_driven CRC
        algorithm.  The Python version cannot handle tables of an index width
        other than 8.  See the generated C code for tables with different sizes
        instead.
        """
        table_length = 1 << self.TableIdxWidth
        tbl = [0] * table_length
        for i in range(table_length):
            register = i
            if self.ReflectIn:
                register = self.reflect(register, self.TableIdxWidth)
            register = register << (self.Width - self.TableIdxWidth + self.CrcShift)
            for j in range(self.TableIdxWidth):
                if register & (self.MSB_Mask << self.CrcShift) != 0:
                    register = (register << 1) ^ (self.Poly << self.CrcShift)
                else:
                    register = (register << 1)
            if self.ReflectIn:
                register = self.reflect(register >> self.CrcShift, self.Width) << self.CrcShift
            tbl[i] = register & (self.Mask << self.CrcShift)
        return tbl


    # function table_driven
    ###############################################################################
    def table_driven(self, in_str):
        """
        The Standard table_driven CRC algorithm.
        """
        tbl = self.gen_table()

        register = self.DirectInit << self.CrcShift
        if not self.ReflectIn:
            for c in in_str:
                tblidx = ((register >> (self.Width - self.TableIdxWidth + self.CrcShift)) ^ ord(c)) & 0xff
                register = ((register << (self.TableIdxWidth - self.CrcShift)) ^ tbl[tblidx]) & (self.Mask << self.CrcShift)
            register = register >> self.CrcShift
        else:
            register = self.reflect(register, self.Width + self.CrcShift) << self.CrcShift
            for c in in_str:
                tblidx = ((register >> self.CrcShift) ^ ord(c)) & 0xff
                register = ((register >> self.TableIdxWidth) ^ tbl[tblidx]) & (self.Mask << self.CrcShift)
            register = self.reflect(register, self.Width + self.CrcShift) & self.Mask

        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        return register ^ self.XorOut

#### End crc_algorithms

import struct
import shutil
from collections import Counter
import traceback
from os.path import isdir, isfile, join

import System.Guid as Guid
from System.Collections.ObjectModel import ObservableCollection
from System.IO import FileInfo, Path
from System import Array, Object

import clr
clr.AddReference("System.Core")
import System
clr.ImportExtensions(System.Linq)


STEAM_PLUGIN_GUID = Guid.Parse("CB91DFC9-B977-43BF-8E70-55F46E410FAB")

SHORTCUT_DEFAULTS = {
    "allowoverlay": 1,
    "allowdesktopconfig": 1,
    "shortcutpath": "",
    "ishidden": 0,
    "openvr": 0,
    "tags": {},
    "lastplaytime": 0,
    "devkit": 0,
    "devkitgameid": "",
}

SHORTCUTS_VDF = join(STEAM_USERDATA, "config", "shortcuts.vdf")

# Parse shortcuts.vdf
# Steam matches keys case insensitively, so lowercase all keys to be case insensitive

def parse_object(stream):
    k = parse_string(stream).lower()
    # Read key value pairs until a \x08 byte is reached
    v = dict(iter(lambda: parse(stream), None))
    return k, v

def parse_int_value(stream):
    k = parse_string(stream).lower()
    v, = struct.unpack("i", stream.read(4))
    return k, v

def parse_string_value(stream):
    k = parse_string(stream).lower()
    v = parse_string(stream)
    return k, v

def parse_string(stream):
    # Strings are null terminated
    return "".join(iter(lambda: stream.read(1),"\x00"))

parse_types = {
    "\x00": parse_object,
    "\x01": parse_string_value,
    "\x02": parse_int_value,
    "\x08": lambda stream: None,
}

def parse(stream):
    # Read a per type one byte header, then parse using the correct type
    data_type = stream.read(1)
    return parse_types[data_type](stream)

def parse_shortcuts(stream):
    shortcuts = parse(stream)[1].values()
    if Counter(s["appname"] for s in shortcuts).most_common()[0][1] > 1:
        raise "Duplicate appnames in Steam shortcuts"
    return {s["appname"]: s for s in shortcuts}

# Dump shortcuts.vdf

def dump_object_value(stream, k, values):
    stream.write("\x00")
    stream.write(k)
    stream.write("\x00")
    for k, v in values.iteritems():
        if isinstance(v, dict):
            dump_object_value(stream, k, v)
        elif isinstance(v, str):
            dump_string_value(stream, k, v)
        elif isinstance(v, int):
            dump_int_value(stream, k, v)
        elif isinstance(v, bool):
            dump_int_value(stream, k, int(v))
        else:
            raise TypeError("Unrecognized type:", type(v))
    stream.write("\x08")

def dump_string_value(stream, k, v):
    stream.write("\x01")
    stream.write(k)
    stream.write("\x00")
    stream.write(v)
    stream.write("\x00")

def dump_int_value(stream, k, v):
    stream.write("\x02")
    stream.write(k)
    stream.write("\x00")
    stream.write(struct.pack("i", v))

def dump_shortcuts(stream, shortcuts):
    # Any string can be used as the key in shortcuts.vdf
    # Originally it is a string of the index, but we use the AppName instead
    dump_object_value(stream, "shortcuts", shortcuts)
    stream.write("\x08")

def steam_URL(shortcut):
    # Comments by Scott Rice:
    """
    Calculates the filename for a given shortcut. This filename is a 64bit
    integer, where the first 32bits are a CRC32 based off of the name and
    target (with the added condition that the first bit is always high), and
    the last 32bits are 0x02000000.
    """
    # This will seem really strange (where I got all of these values), but I
    # got the xor_in and xor_out from disassembling the steamui library for
    # OSX. The reflect_in, reflect_out, and poly I figured out via trial and
    # error.
    algorithm = Crc(width = 32, poly = 0x04C11DB7, reflect_in = True, xor_in = 0xffffffff, reflect_out = True, xor_out = 0xffffffff)
    input_string = shortcut["exe"] + shortcut["appname"]
    top_32 = algorithm.bit_by_bit(input_string) | 0x80000000
    full_64 = (top_32 << 32) | 0x02000000
    return "steam://rungameid/" + str(full_64)

def find_play_action(game):
    """
    Check if there is an existing OtherAction titled "Launch without Steam".

    This will occur if the script is rerun on a game. We want to find the
    original PlayAction to update the non-Steam shortcut.
    """

    if game.OtherActions:
        for play_action in game.OtherActions:
            if play_action.Name == "Launch without Steam":
                return play_action
    return game.PlayAction

def emulator_expand_variables(profile, game):
    # HACK! Import EmulatorProfileExtensions with reflection
    EmulatorProfileExtensions = PlayniteApi.GetType().Assembly.GetType("Playnite.EmulatorProfileExtensions")
    method = EmulatorProfileExtensions.GetMethod("ExpandVariables")
    return method.Invoke(None, Array[Object]((profile, game,)))

def non_steam_shortcuts():
    games_updated = 0
    games_new = 0
    games_skipped_no_action = []
    games_skipped_steam_native = []
    games_skipped_bad_emulator = []
    games_url = []

    if not isdir(join(STEAM_USERDATA, "config")):
        PlayniteApi.Dialogs.ShowErrorMessage(
            "Please configure this extension by setting the path to your Steam profile's userdata folder. "
            "Edit the nonsteam.py file of this extension and update STEAM_USERDATA.",
            "Error: Extension not configured")
        return

    if isfile(SHORTCUTS_VDF):
        try:
            shutil.copyfile(SHORTCUTS_VDF, SHORTCUTS_VDF+".bak")
        except Exception as e:
            PlayniteApi.Dialogs.ShowErrorMessage(
                traceback.format_exc(),
                "Error backing up shortcuts.vdf")
            return

        try:
            with open(SHORTCUTS_VDF, "rb") as f:
                steam_shortcuts = parse_shortcuts(f)
        except Exception as e:
            PlayniteApi.Dialogs.ShowErrorMessage(
                traceback.format_exc(),
                "Error loading shortcuts.vdf")
            return
    else:
        steam_shortcuts = {}

    for game in PlayniteApi.MainView.SelectedGames:
        play_action = find_play_action(game)

        # If a game somehow has no PlayAction, skip it
        if not play_action:
            games_skipped_no_action.append(game.Name)
            continue

        # Skip the game if it is handled by the Steam plugin
        if game.PluginId == STEAM_PLUGIN_GUID:
            games_skipped_steam_native.append(game.Name)
            continue

        # If a game has a URL PlayAction, use it anyway but log it
        if play_action.Type == GameActionType.URL:
            games_url.append(game.Name)

        # Create/Update Non-Steam shortcut
        play_action_expanded = PlayniteApi.ExpandGameVariables(game, play_action)
        if play_action_expanded.Type == GameActionType.Emulator:
            emulator = PlayniteApi.Database.Emulators.Get(play_action.EmulatorId)
            if emulator.Profiles:
                profile = emulator.Profiles.FirstOrDefault(lambda a: a.Id == play_action.EmulatorProfileId)
            else:
                profile = None
            if not profile:
                games_skipped_bad_emulator.append(game.Name)
                continue
            profile_expanded = emulator_expand_variables(profile, game)
            start_dir = profile_expanded.WorkingDirectory
            exe = profile_expanded.Executable
            arguments = profile_expanded.Arguments or ""
            if play_action_expanded.AdditionalArguments:
                arguments += " " + play_action_expanded.AdditionalArguments
            if play_action_expanded.OverrideDefaultArgs:
                arguments = play_action_expanded.Arguments or ""
        elif play_action_expanded.Type == GameActionType.File:
            start_dir = play_action_expanded.WorkingDir
            exe = play_action_expanded.Path
            arguments = play_action_expanded.Arguments or ""
        elif play_action_expanded.Type == GameActionType.URL:
            exe = play_action_expanded.Path
            start_dir = ""
            arguments = ""
        if not play_action_expanded.Type == GameActionType.URL:
            if not start_dir:
                start_dir = FileInfo(exe).Directory.FullName
            exe = Path.Combine(start_dir, exe)
        if game.Icon:
            icon = PlayniteApi.Database.GetFullFilePath(game.Icon)
        else:
            icon = ""
        shortcut = {
            "icon": icon,
            "exe": '"{}"'.format(exe),
            "startdir": '"{}"'.format(start_dir),
            "appname": game.Name,
            "launchoptions": arguments,
        }
        if game.Name in steam_shortcuts:
            games_updated += 1
            steam_shortcuts[game.Name].update(shortcut)
            shortcut = steam_shortcuts[game.Name]
        else:
            games_new += 1
            shortcut.update(SHORTCUT_DEFAULTS)
            steam_shortcuts[game.Name] = shortcut

        # Update Playnite actions
        # Only run once, don't create duplicate OtherActions
        if play_action == game.PlayAction:
            old_action = game.PlayAction
            steam_action = GameAction(
                Name="Non-Steam Steam Shortcut",
                Type=GameActionType.URL,
                Path=steam_URL(shortcut),
                IsHandledByPlugin=False,
            )
            game.PlayAction = steam_action
            if not game.OtherActions:
                game.OtherActions = ObservableCollection[GameAction]()
            old_action.Name = "Launch without Steam"
            game.OtherActions.Insert(0, old_action)
        else:
            # play_action is already an OtherAction
            # Just make sure the URL is up to date on the main PlayAction
            game.PlayAction.Path = steam_URL(shortcut)

    # Save updated shortcuts.vdf
    try:
        with open(SHORTCUTS_VDF, "wb") as f:
            dump_shortcuts(f, steam_shortcuts)
    except Exception as e:
        PlayniteApi.Dialogs.ShowErrorMessage(
            traceback.format_exc(),
            "Error saving shortcuts.vdf")
        return

    message = "Please relaunch Steam to update non-Steam shortcuts!\n\n"
    message += "Updated {} existing non-Steam shortcuts\n".format(games_updated)
    message += "Created {} new non-Steam shortcuts".format(games_new)
    if games_skipped_steam_native:
        message += "\n\nSkipped {} native Steam game(s):\n".format(len(games_skipped_steam_native))
        message += "\n".join(games_skipped_steam_native)
    if games_skipped_no_action:
        message += "\n\nSkipped {} game(s) without any PlayAction set (not installed?):\n".format(len(games_skipped_no_action))
        message += "\n".join(games_skipped_no_action)
    if games_skipped_bad_emulator:
        message += "\n\nSkipped {} emulated game(s) with bad emulator profiles:\n".format(len(games_skipped_bad_emulator))
        message += "\n".join(games_skipped_bad_emulator)
    if games_url:
        message += "\n\nWarning: Some games had URL launch actions. (Typically managed by a library plugin.) "
        message += "You may wish to update their actions and recreate non-Steam shortcuts. "
        message += "Steam will still launch these games, but the Steam overlay will not function."
        message += "\n\nThe following {} game(s) had URL launch actions:\n".format(len(games_url))
        message += "\n".join(games_url)
    PlayniteApi.Dialogs.ShowMessage(
        message,
        "Updated Non-Steam Shortcuts"
    )
