import sqlite3, sys
sys.path.insert(0, '/home/claude/german_dict')
from words_data   import WORDS
from words_data_2 import WORDS2
from words_data_3 import WORDS3

DB_PATH = '/home/claude/german_dict/german_dictionary.db'

ALL_WORDS = WORDS + WORDS2 + WORDS3

def build():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS words;
        DROP TABLE IF EXISTS metadata;

        CREATE TABLE words (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            word         TEXT NOT NULL,
            word_lower   TEXT NOT NULL,
            article      TEXT DEFAULT '',
            display      TEXT NOT NULL,
            definition   TEXT NOT NULL,
            example_de   TEXT NOT NULL,
            example_en   TEXT NOT NULL,
            category     TEXT NOT NULL,
            level        TEXT NOT NULL,
            first_letter TEXT NOT NULL,
            last_letter  TEXT NOT NULL
        );

        CREATE INDEX idx_word_lower   ON words(word_lower);
        CREATE INDEX idx_first_letter ON words(first_letter);
        CREATE INDEX idx_last_letter  ON words(last_letter);
        CREATE INDEX idx_level        ON words(level);
        CREATE INDEX idx_category     ON words(category);
        CREATE INDEX idx_level_first  ON words(level, first_letter);
        CREATE INDEX idx_level_last   ON words(level, last_letter);

        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT);
    """)

    seen, dupes, rows = set(), 0, []
    for entry in ALL_WORDS:
        word, article, definition, example_de, example_en, category, level = entry
        wl = word.lower()
        if wl in seen:
            dupes += 1
            continue
        seen.add(wl)
        clean = ''.join(ch for ch in word if ch.isalpha())
        if not clean:
            continue
        display = f"{article} {word}".strip() if article else word
        rows.append((word, wl, article, display, definition,
                     example_de, example_en, category, level,
                     clean[0].upper(), clean[-1].upper()))

    c.executemany("""
        INSERT INTO words (word,word_lower,article,display,definition,
            example_de,example_en,category,level,first_letter,last_letter)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, rows)

    c.execute("INSERT INTO metadata VALUES ('version','1.0')")
    c.execute("INSERT INTO metadata VALUES ('language','German')")
    c.execute(f"INSERT INTO metadata VALUES ('total_words','{len(rows)}')")
    conn.commit()

    print(f"\n✅  {len(rows)} unique words  ({dupes} duplicates removed)\n")

    print("CEFR breakdown:")
    for row in c.execute("SELECT level, COUNT(*) n FROM words GROUP BY level ORDER BY level"):
        bar = '█' * (row[1]//10)
        print(f"  {row[0]}  {row[1]:4d}  {bar}")

    print("\nTop categories:")
    for row in c.execute("SELECT category, COUNT(*) n FROM words GROUP BY category ORDER BY n DESC LIMIT 12"):
        print(f"  {row[0]:22s} {row[1]:4d}")

    print("\nLetters with most words (top 10):")
    for row in c.execute("SELECT first_letter, COUNT(*) n FROM words GROUP BY first_letter ORDER BY n DESC LIMIT 10"):
        print(f"  {row[0]}  {row[1]}")

    print("\nLetters present:")
    letters = [r[0] for r in c.execute("SELECT DISTINCT first_letter FROM words ORDER BY first_letter")]
    print(" ", " ".join(letters))

    print(f"\n📦  {DB_PATH}")
    conn.close()

if __name__ == '__main__':
    build()
