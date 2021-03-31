import csv, sys, datetime, time, traceback, math
from PyQt5.QtWidgets import *
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from os.path import expanduser

### FIELD NAME OF HEISIG INDEX ###
config = mw.addonManager.getConfig(__name__)
fieldIndex = config['version']


## MAIN ##
def run():
    # Stats
    updated = 0
    numcards = mw.col.cardCount()

    # Get the RevTK file
    fname = QFileDialog.getOpenFileName(None, 'Open file', '', 'CSV (*.csv)')[0]

    # Open
    try:
        f = open(fname, 'r', encoding="utf-8")
    except:
        print('Could not open file %s' % fname)
        return

    # Process
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for line in reader:
        ##FIRST ERROR
        if processCard(*line):
            updated += 1
    ##FIRST ERROR

    # Close
    f.close()

    # Finished
    showInfo('Updated %d/%d cards.' % (updated, numcards))
    mw.reset()


## RUN FOR EACH CARD IN FILE ##
def processCard(nr, kanji, keyword, lastseen, due, box, fails, passes):
    try:
        # Get the IDs of cards with given Heisig index
        query = fieldIndex + ":" + nr
        cids = mw.col.findCards(query)
        if not cids:
            print('Could not find card with index %s' % nr)
            return False

        b = min(30, int(box))
        if b < 1:
            print('Invalid box [%s] for card nr.%s' % (box, nr))
            return False

        # Update cards
        for cid in cids:

            # Get card
            card = mw.col.getCard(cid)

            # Update
            card.due = mw.col.sched.today + isDueIn(str(due))  # Day on which card will be due
            card.reps = int(passes) + int(fails)  # Reviews
            card.lapses = int(fails)  # Times relearnt
            card.ivl = max(1, isDueIn(due) + seenLast(lastseen))  # Interval
            card.factor = 2000 + min(600, max(0, 300 * math.log(b) - 10 * b))  # 300 * ln(x) - 10*x
            if card.ivl >= 15:
                i = min(150, card.ivl)
                ivlPenalty = (i ** 2) / 10 - 1.065 * max(0, (i ** 2.26) / 40 - 25 * math.sqrt(i))
                card.factor = max(2000, card.factor - ivlPenalty)  # If the interval is especially long, make it harder
            card.factor = int(round(card.factor))

            # Card type 
            card.type = 2  # Due

            if card.reps == 0:

                card.type = 0  # New
                card.ivl = 0
                card.factor = 2500

            elif b == 1:

                card.type = 3  # Relearnt (We can't distinguish between 'restudy' and 'relearnt'
                card.ivl = 1  # => assume 'relearnt'
                card.due = mw.col.sched.today

            card.queue = card.type

            # Flush
            card.flush()

        # Success
        return True

    except:

        # Error
        showInfo(traceback.format_exc())
        print('Unexpected error occurred while updating card nr.%s:\n%s' % (nr, traceback.format_exc()))
        return False


## COMPUTES WHEN THE CARD IS DUE IN DAYS ##
def isDueIn(duedate):
    d = duedate
    # d = duedate.encode('utf-8')
    # d = d.decode('utf-8')

    if d == '0000-00-00':

        return 0

    else:

        n = datetime.date.today()
        d = datetime.date.fromtimestamp(time.mktime(time.strptime(d, '%Y-%m-%d')))

        return max(0, (d - n).days)


## COMPUTES WHEN THE CARD WAS SEEN LAST
def seenLast(seen):
    s = seen
    # s = seen.encode('utf-8')
    # s = seen.decode('utf-8')

    if s == '0000-00-00 00:00:00':

        return 0

    else:
        n = datetime.date.today()
        s = datetime.date.fromtimestamp(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))

        return max(0, (n - s).days)


## MENU ENTRY ##
action = QAction('Import Kanji Koohii progress...', mw)
action.triggered.connect(run)
mw.form.menuTools.addAction(action)
