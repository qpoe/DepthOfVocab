import sqlite3
con = sqlite3.connect("db/vocabulary.db")
cur = con.cursor()
words = []
synonyms = []
cur.execute("SELECT word_name, definition, synonyms from vocabs")
for word_name, definition, synonym in cur.fetchall():
    words.append({"word": word_name, "definition": definition})
    synonyms.append({"word": word_name, "synonyms": str(synonym).split(',')})
cur.close()