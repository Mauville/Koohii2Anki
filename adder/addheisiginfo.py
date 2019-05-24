# -*- coding: utf-8 -*-
# Copyright: Ian Worthington <Worthy.vii@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#
# Adding of Heisig Keywords - to the "Keywords" field
# Adding of Heisig Numbers - to the "Heisig Number" field
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
import os
import re
from anki.utils import stripHTML, isWin, isMac

# import the main window object (mw) from ankiqt
from aqt import mw
from aqt.utils import showInfo
import sys
import codecs

#version they want to use, 2010 or old

# RTK file path
this_dir, this_filename = os.path.split(__file__)
allRTK = os.path.join(this_dir, "RTK.tsv") 

#RTK data goes here
kanjiIndex = dict()
                    

joinseparator = ','

#Fields used
#in					
expField = 'Expression'
#out
kanjiDstField = 'Reading'
heisigNumDstField = 'Caution'
#Default Heisig version to use
heisigVersion = '2010'

def readRTK():
    with open(allRTK, 'r') as f:
        content = f.read().splitlines()
        #sys.stderr.write(content[0] + "\n")
    f.close() 
    for line in content:
        fieldhash = dict(zip(('kanji', 'heisigold', 'heisig2010', 'keyword'),
                            line.split('\t')))
        kanjiIndex[fieldhash['kanji'].decode('utf8')] = fieldhash
    
    
def getHeisigVersion():

    #sys.stderr.write("setversion")
    mw.hDialog = hDialog = QMessageBox()
    hDialog.setText("Would you like to use the numbering from RTK-1 6th edition, or an older edition?")
    hDialog.setInformativeText("The 6th edition will use numbers from 1-2200. Older versions are missing some kanji and so the supplemented extra kanji numbers (e.g. 265A) will be used instead or the RTK3 book. Choose according to which edition of the RTK-1 book you will be referencing.")

    yButton = hDialog.addButton("6th Edition", QMessageBox.AcceptRole)
    nButton = hDialog.addButton("Older Edition",QMessageBox.RejectRole)
    hDialog.setStandardButtons(QMessageBox.Cancel);
    
    
    ret = hDialog.exec_()
    if ret == QMessageBox.AcceptRole:
        version = "2010"
        #sys.stderr.write("accept" + str(ret))
    elif ret == QMessageBox.RejectRole:
        version = "old"
        #sys.stderr.write("reject" + str(ret))
    elif ret == QMessageBox.Cancel:
        return False
        
    return version

    
#get user to select from a list
def getKeyFromList(titleText, labelText, strings):
        
    d = QInputDialog()
    d.setComboBoxItems(strings)
    d.setWindowTitle(titleText)
    d.setLabelText(labelText)
    d.setOption(QInputDialog.UseListViewForComboBoxItems)
       
    
    if d.exec_()==1:
        return d.textValue()

      
def addHeisigNumbers(nids):
    #get version to use
    
    version = getHeisigVersion()
    if version == False:
        return
    
    
    fields = []
    
    anote=mw.col.getNote(nids[0])
    #get the fields of the first note
    for (i, f) in anote.items():
        fields.append(i)
    
    #get input/output fields from user
    expField = getKeyFromList("Select field to read from", "Read relevant kanji/expression from:", fields)
    if (expField is None):
        return
    heisigNumDstField = getKeyFromList("Select field to write to", "Write Heisig numbers to:", fields)
    if (heisigNumDstField is None):
        return
    
    
    
    mw.checkpoint("Add Heisig Numbers")
    mw.progress.start()
    readRTK()
    
    #For each seleccted card
    for nid in nids:
        note = mw.col.getNote(nid)
        src = None
        if expField in note:
            src = expField
        if not src:
            # no src field then next card
            continue
        dst = None
        if heisigNumDstField in note:
            dst = heisigNumDstField
        if not dst:
            # no dst field then skip card
            continue
        srcTxt = mw.col.media.strip(note[src])
        if not srcTxt.strip():
            continue
        #Add the data to the dst field
        num = joinseparator.join(lookupKanjiInfo(srcTxt, 'heisig'+version))
        if num!=0:
            note[dst] = str(num)
        #sys.stderr.write("Results:" + note[dst])
        note.flush()
    mw.progress.finish()
    mw.reset()	
    
def addMostDifficultHeisigNumber(nids):
      
    fields = []
    
    anote=mw.col.getNote(nids[0])
    #get the fields of the first note
    for (i, f) in anote.items():
        fields.append(i)
    
    #get input/output fields from user
    expField = getKeyFromList("Select field to read from", "Read relevant kanji/expression from:", fields)
    if (expField is None):
        return
    heisigNumDstField = getKeyFromList("Select field to write to", "Write Heisig numbers to:", fields)
    if (heisigNumDstField is None):
        return
    
    
    
    mw.checkpoint("Add Heisig Numbers")
    mw.progress.start()
    readRTK()
    #For each seleccted card
    for nid in nids:
        note = mw.col.getNote(nid)
        src = None
        if expField in note:
            src = expField
        if not src:
            # no src field then next card
            continue
        dst = None
        if heisigNumDstField in note:
            dst = heisigNumDstField
        if not dst:
            # no dst field then skip card
            continue
        srcTxt = mw.col.media.strip(note[src])
        if not srcTxt.strip():
            continue
        #Add the data to the dst field
        num = max((map(int, lookupKanjiInfo(srcTxt, 'heisig2010'))))
        note[dst] = str(num)
        #sys.stderr.write("Results:" + note[dst])
        note.flush()
    mw.progress.finish()
    mw.reset()	

def lookupKanjiInfo(wordsTxt, key):
    #first get only the kanji
    words = re.findall(ur'[\u4e00-\u9fbf]',wordsTxt)
    results = []
    for word in words:
        if (word in kanjiIndex):
            results.append(kanjiIndex[word][key]) 
        else:
            if (key=='heisigold' or key=='heisig2010'):
                results.append('0')
            else:
                results.append('??')
    return results    

def addKanjiKeywords_bulk(nids):
    
    fields = []
    
    anote=mw.col.getNote(nids[0])

    #get the fields of the first note
    for (i, f) in anote.items():
        fields.append(i)
    
    #get input/output fields from user
    expField = getKeyFromList("Select field to read from", "Read relevant kanji/expression from:", fields)
    if (expField is None):
        return
    kanjiDstField = getKeyFromList("Select field to write to", "Write keywords to:", fields)
    if (heisigNumDstField is None):
        return

    
    mw.checkpoint("Add Heisig Keywords")
    readRTK()	
    
    #set version
    version = '2010'
    
    #get output field
    #which numbering system do you want to use?
    mw.progress.start()
    #For each seleccted card
    for nid in nids:
        note = mw.col.getNote(nid)
        
        
        src = None
        if expField in note:
            src = expField
        if not src:
            # no src field then next card
            continue
        dst = None
        if kanjiDstField in note:
            dst = kanjiDstField
        if not dst:
            # no dst field then skip card
            continue
                    
        
        #Add the data to the dst field
        if True == doNote(note, expField, kanjiDstField):
            note.flush()
    mw.progress.finish()
    mw.reset()


    
def addKanjiKeywords_onFocusLost(flag, note, fidx):
            
    
    #check if the fields exist
    dst = src = None
    global expField
    global kanjiDstField
    
    for c, name in enumerate(mw.col.models.fieldNames(note.model())):
        if name == expField:
            src = expField
            srcIdx = c
        if name == kanjiDstField:
            dst = kanjiDstField
            
    if not src or not dst:
        return flag
    
    # dst field already filled?
    #if note[dst]:
        #return flag
        
    # event coming from src field?
    if fidx != srcIdx:
        return flag

    readRTK()
    
    #do the note and handle the results
    if False == doNote(note, None, None):
        return flag
    return True
    
    
    
def doNote(note, expF=None , kanjiDField=None):
    
    #If no fields were given then use the defaults
    if expF==None:
        global expressionField
    else:
        expressionField = expF
        
    if kanjiDField==None:
        global kanjiDstField
    else:
        kanjiDstField = kanjiDField
        
    #Strip out any annoying HTML
    srcTxt = stripHTML(note[expField])
    
    
    changed = 0
    
    #Add the data to the dst field
    result = joinseparator.join(lookupKanjiInfo(srcTxt, 'keyword'))
    if result and note[kanjiDstField] != result:
        changed = 1
        note[kanjiDstField] = result 
    
    
   
    
    if changed == 1:
        return True
    else:
        return False
    
    
    
    
def setupMenu(browser):

    browser.form.menuEdit.addSeparator()
    
    heisigMenu = browser.form.menuEdit.addMenu('Heisig Info')
    
    a = QAction("Add Keywords", browser)
    b = QAction("Add Indices", browser)
    c = QAction("Add highest Index", browser)
    
    heisigMenu.addAction(a)
    heisigMenu.addAction(b)
    heisigMenu.addAction(c)

    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onKanjiKeywords(e))
    browser.connect(b, SIGNAL("triggered()"), lambda e=browser: onHeisigNumbers(e))
    browser.connect(c, SIGNAL("triggered()"), lambda e=browser: onHardestHeisigNumber(e))
                    
def onKanjiKeywords(browser):
    addKanjiKeywords_bulk(browser.selectedNotes())
    
def onHeisigNumbers(browser):
    addHeisigNumbers(browser.selectedNotes())

def onHardestHeisigNumber(browser):
    addMostDifficultHeisigNumber(browser.selectedNotes())


addHook("browser.setupMenus", setupMenu)

addHook('editFocusLost', addKanjiKeywords_onFocusLost)