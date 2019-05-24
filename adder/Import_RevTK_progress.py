import csv, sys, datetime, time, traceback, math

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from os.path import expanduser

### FIELD NAME OF HEISIG INDEX ###
fieldIndex = 'frameNoV6'


## MAIN ##
def run():
    # Stats
    updated = 0
    numcards = mw.col.cardCount()

    # Get the RevTK file
    fname = QFileDialog.getOpenFileName(None, 'Open file', '', 'CSV (*.csv)')

    # Open
    try:
        f = open(fname, 'r')
    except:
        print
        'Could not open file %s' % fname
        return

    # Process
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for line in reader:

        if processCard(*line):
            updated += 1

    # Close
    f.close()

    # Finished
    showInfo('Updated %d/%d cards.' % (updated, numcards))
    mw.reset()


## RUN FOR EACH CARD IN FILE ##
def processCard(nr, kanji, keyword, public, last_edited, story):

   '''' 
     get all collection
     get data from csv
     index = 0
     
     fillStories
        while index <= collection.length
            if collection[index] and csv[index]
                overwrite keyword
                overwrite heisigStory
            else if not (collection[index]) and csv[index]
                createCard
            else skip card
        
   ''''

    try:

        # Get the IDs of cards with given Heisig index
        cids = mw.col.findCards("%s:%s" % (fieldIndex, nr))
        if not cids:
            print "cool"
            # TODO METHOD TO SKIP CARD
            # print 'Could not find card with index %s' % nr
            # return False

        # Update cards
        for cid in cids:
            # Get card
            card = mw.col.getCard(cid)
            note = card.note()


            for (name, value) in note.items():
                note[name] = value + " new"

        # Flush
        card.flush()

            # Success
        return True

    except:

        # Error
        print
        'Unexpected error occurred while updating card nr.%s:\n%s' % (nr, traceback.format_exc())
        return False


## COMPUTES WHEN THE CARD IS DUE IN DAYS ##
def isDueIn(duedate):
    d = duedate.encode('utf-8')

    if d == '0000-00-00':

        return 0

    else:

        n = datetime.date.today()
        d = datetime.date.fromtimestamp(time.mktime(time.strptime(d, '%Y-%m-%d')))

        return max(0, (d - n).days)


## COMPUTES WHEN THE CARD WAS SEEN LAST
def seenLast(seen):
    s = seen.encode('utf-8')

    if s == '0000-00-00 00:00:00':

        return 0

    else:
        n = datetime.date.today()
        s = datetime.date.fromtimestamp(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))

        return max(0, (n - s).days)


## MENU ENTRY ##
action = QAction('Import RevTK progress...', mw)
mw.connect(action, SIGNAL('triggered()'), run)
mw.form.menuTools.addAction(action)
