#TODO add an input select for v4

import pandas

version = "v6"
# read kanji and story column
stories = pandas.read_csv('my_stories.csv', sep=",", encoding="utf-8", usecols=[5, 1, 0, 2])
# read the deck transformed to tsv
names = ["v4", "v6", "keyword", "kanji", "hint", "primitive", "strokeCount", "lesson", "heisigS", "heisigC", "MyStory",
         "KS1", "KS2", "Jou", "JLPT", "On", "Kun", "words", "reading", "Diagram", "?"]
deck = pandas.read_csv('formattedRTK.tsv', sep="\t", names=names, encoding="utf-8", header=None, index_col=0)
# convert the MyStory and keyword columns to string in case of blanks
deck = deck.astype({"MyStory": object, "keyword": object})

# sort by version number
deck = deck.sort_values(by=version)
missingKanji = []
for _, row in stories.iterrows():
    # access element in position 0.
    currentKanji = row["kanji"]
    currentIndex = row["framenr"]
    currentKeyword = row["keyword"]
    currentStory = row["story"]
    # find row in deck that corresponds to the stories index 
    deckRow = deck.loc[deck[version] == currentIndex]
    # try to find a note in the deck. If not found, create one.
    try:
        # assert kanji == kanji
        if deckRow.iloc[0]["kanji"] == currentKanji:
            # write values to rows
            deck.at[deckRow[version].index.item(), "keyword"] = currentKeyword
            deck.at[deckRow[version].index.item(), "MyStory"] = currentStory
            print(str(deckRow.iloc[0]["kanji"]) + ": " + str(deckRow[version].index.item()))

    except IndexError:
        print("An existing note could not be found for the character " + currentKanji + "")
        deck.loc[currentIndex] = [currentIndex, currentIndex, currentKeyword, currentKanji, "", "", "", "", "",
                                  "", currentStory, "", "", "Hyougai", "0", "", "", "", "", "", "Hyougai"]
        print("Created a note for " + currentKanji + " ")

# Write to deck
print("Writing to file")
deck.to_csv("Formatted.txt", sep="\t", header=False, index=True)
