#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# kanji_colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams; this is the anki2 addon file.
#
# Copyright 2012 Cayenne Boyer
#
# The code to do this automatically when the Kanji field is exited was
# originally based on the Japanese support reading generation addon by
# Damien Elmes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

# Installation: copy this file and the kanjicolorizer directory to your
# Anki addons folder.

# Usage: Add a "Diagram" field to a model with "Japanese"
# in the name and a field named "Kanji".  When you finish editing the
# kanji field, if it contains precisely one character, a colored stroke
# order diagram will be added to the Diagram field in the same way that
# the Japanese support plugin adds readings.
#
# To add diagrams to all such fields, or regenerate them with new
# settings, use the "Kanji Colorizer: (re)generate all" option in the
# tools menu.


from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *
from .kanjicolorizer.colorizer import (KanjiVG, KanjiColorizer,
                                      InvalidCharacterError)

# Configuration

addon_config = mw.addonManager.getConfig(__name__)

config = "--mode "
config += addon_config["mode"]
if addon_config["group-mode"]:
  config += " --group-mode "
config += " --saturation "
config += str(addon_config["saturation"])
config += " --value "
config += str(addon_config["value"])
config += " --image-size "
config += str(addon_config["image-size"])

# mod
srcField = 'Kanji'
dstField = 'strokeOrder'

kc = KanjiColorizer(config)


def modelIsCorrectType(model):
    '''
    Returns True if model has rtk in the name and has both srcField
    and dstField; otherwise returns False
    '''
    # Does the model name have Japanese in it?
    model_name = model['name'].lower()
    fields = mw.col.models.fieldNames(model)
    # mod
    return ('japanese' in model_name and
                         srcField in fields and
                         dstField in fields)


def characters_to_colorize(s):
    '''
    Given a string, returns a lost of characters to colorize

    If the string consists of only a single character, returns a list
    containing that character.  If it is longer, returns a list of  only the
    kanji.

    '''
    if len(s) <= 1:
        return list(s)
    return [c for c in s if ord(c) >= 19968 and ord(c) <= 40879]


def addKanji(note, flag=False, currentFieldIndex=None):
    '''
    Checks to see if a kanji should be added, and adds it if so.
    '''
    if not modelIsCorrectType(note.model()):
        return flag

    if currentFieldIndex != None: # We've left a field
        # But it isn't the relevant one
        if note.model()['flds'][currentFieldIndex]['name'] != srcField:
            return flag

    srcTxt = mw.col.media.strip(note[srcField])

    oldDst = note[dstField]
    dst=''

    for character in characters_to_colorize(str(srcTxt)):
        # write to file; anki works in the media directory by default
        try:
            filename = KanjiVG(character).ascii_filename
        except InvalidCharacterError:
            # silently ignore non-Japanese characters
            continue
        char_svg = kc.get_colored_svg(character).encode('utf_8')
        anki_fname = mw.col.media.writeData(filename, char_svg)
        dst += '<img src="{!s}">'.format(anki_fname)

    if dst != oldDst and dst != '':
        note[dstField] = dst
        note.flush()
        return True

    return flag


# Add a colorized kanji to a Diagram whenever leaving a Kanji field

def onFocusLost(flag, note, currentFieldIndex):
    return addKanji(note, flag, currentFieldIndex)

addHook('editFocusLost', onFocusLost)


# menu item to regenerate all

def regenerate_all():
    # Find the models that have the right name and fields; faster than
    # checking every note
    if not askUser("Do you want to regenerate all kanji diagrams? "
                   'This may take some time and will overwrite the '
                   'destination strokeOrder fields.'):
        return
    models = [m for m in mw.col.models.all() if modelIsCorrectType(m)]
    # Find the notes in those models and give them kanji
    for model in models:
        for nid in mw.col.models.nids(model):
            addKanji(mw.col.getNote(nid))
    showInfo("Done regenerating colorized kanji diagrams!")

# add menu item
do_regenerate_all = QAction("Kanji Colorizer for RTK: (re)generate all", mw)
do_regenerate_all.triggered.connect(regenerate_all)
mw.form.menuTools.addAction(do_regenerate_all)
