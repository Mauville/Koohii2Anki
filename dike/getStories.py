# suppose its v6
# add an input select for v4

import pandas

import sys

# read kanji and story column
stories = pandas.read_csv('my_stories.csv', sep=",", encoding="utf-8", usecols=[5, 1, 0, 2])
# read the deck transformed to tsv
names = ["v4", "v6", "keyword", "kanji", "hint", "primitive", "strokeCount", "lesson", "heisigS", "heisigC", "MyStory",
         "KS1", "KS2", "Jou", "JLPT", "On", "Kun", "words", "reading", "Diagram", "?"]

deck = pandas.read_csv('formattedRTK.tsv', sep="\t", names=names, encoding="utf-8", header=None, index_col=0)
# convert the MyStory and keyword columns to string in case of blanks
deck = deck.astype({"MyStory": object, "keyword": object})

# sort by version number
deck = deck.sort_values(by="v6")

for _, row in stories.iterrows():
    # access element in position 0.
    currentKanji = row["kanji"]
    currentIndex = row["framenr"]
    currentKeyword = row["keyword"]
    currentStory = row["story"]
    # find row in deck that corresponds to the stories index 
    deckRow = deck.loc[deck['v6'] == currentIndex]
    # assert kanji == kanji
    if deckRow.iloc[0]["kanji"] == currentKanji:
        # write values to rows
        deck.at[deckRow["v6"].index.item(), "keyword"] = currentKeyword
        deck.at[deckRow["v6"].index.item(), "MyStory"] = currentStory
    print(deckRow.iloc[0]["kanji"])
    print(deckRow["v6"].index.item())

