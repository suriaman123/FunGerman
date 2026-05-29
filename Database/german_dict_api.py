"""
german_dict_api.py
==================
Query interface for the Fun German dictionary SQLite database.

Usage example
-------------
    from german_dict_api import GermanDictionary

    db = GermanDictionary()

    # Get a computer word starting with 'S' at A2 level
    word = db.get_computer_word('S', 'A2')

    # Validate a user word
    result = db.validate_user_word('Schule', 'S')

    # Look up a word
    info = db.lookup('Schule')

    # Browse words
    food = db.browse(category='food', level='A1')
"""

import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'german_dictionary.db')


class GermanDictionary:
    """Thin wrapper around the German dictionary SQLite database."""

    # Map each CEFR level to the levels the computer is *allowed* to use
    # e.g. A2 computer may use A1 and A2 words
    LEVEL_POOL = {
        'A1': ['A1'],
        'A2': ['A1', 'A2'],
        'B1': ['A1', 'A2', 'B1'],
        'B2': ['A1', 'A2', 'B1', 'B2'],
        'C1': ['A1', 'A2', 'B1', 'B2', 'C1'],
        'C2': ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
    }

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    # ── connection management ─────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ── core game queries ─────────────────────────────────────────────────

    def get_computer_word(
        self,
        start_letter: str,
        level: str,
        used_words: list[str] | None = None,
    ) -> dict | None:
        """
        Return a random word starting with *start_letter* at the given CEFR
        *level* (including all easier levels).  Words in *used_words* are
        excluded.  Returns None if no suitable word is found (computer concedes).

        Return dict keys:
            word, display, article, definition, example_de, example_en,
            category, level, last_letter
        """
        used_words = [w.lower() for w in (used_words or [])]
        levels = self.LEVEL_POOL.get(level.upper(), ['A1'])
        placeholders_lvl  = ','.join('?' * len(levels))
        letter = start_letter.upper()

        exclude_clause = ''
        params: list = [letter] + levels
        if used_words:
            ph = ','.join('?' * len(used_words))
            exclude_clause = f'AND word_lower NOT IN ({ph})'
            params += used_words

        sql = f"""
            SELECT word, display, article, definition,
                   example_de, example_en, category, level, last_letter
            FROM words
            WHERE first_letter = ?
              AND level IN ({placeholders_lvl})
              {exclude_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        cur = self._get_conn().cursor()
        row = cur.execute(sql, params).fetchone()
        if row is None:
            return None
        return dict(row)

    def validate_user_word(
        self,
        word: str,
        must_start_with: str,
    ) -> dict:
        """
        Check whether *word* exists in the dictionary and starts with the
        correct letter.

        Returns:
            {
                'exists':  bool,   # found in DB
                'valid':   bool,   # exists AND starts with the right letter
                'reason':  str,    # human-readable reason if invalid
                'info':    dict | None   # full word info if found
            }
        """
        letter = must_start_with.upper()
        cur = self._get_conn().cursor()
        row = cur.execute(
            """SELECT word, display, article, definition,
                      example_de, example_en, category, level, first_letter
               FROM words WHERE word_lower = ?""",
            (word.lower(),),
        ).fetchone()

        if row is None:
            return {
                'exists': False,
                'valid': False,
                'reason': f'"{word}" was not found in the dictionary.',
                'info': None,
            }

        info = dict(row)
        if info['first_letter'] != letter:
            return {
                'exists': True,
                'valid': False,
                'reason': (
                    f'"{word}" starts with {info["first_letter"]}, '
                    f'but must start with {letter}.'
                ),
                'info': info,
            }

        return {'exists': True, 'valid': True, 'reason': '', 'info': info}

    # ── lookup / flashcard ────────────────────────────────────────────────

    def lookup(self, word: str) -> dict | None:
        """Return full info for a single word (case-insensitive).  None if not found."""
        cur = self._get_conn().cursor()
        row = cur.execute(
            """SELECT word, display, article, definition,
                      example_de, example_en, category, level,
                      first_letter, last_letter
               FROM words WHERE word_lower = ?""",
            (word.lower(),),
        ).fetchone()
        return dict(row) if row else None

    def lookup_id(self, word_id: int) -> dict | None:
        """Return full info by primary key id."""
        cur = self._get_conn().cursor()
        row = cur.execute(
            "SELECT * FROM words WHERE id = ?", (word_id,)
        ).fetchone()
        return dict(row) if row else None

    # ── browse / search ───────────────────────────────────────────────────

    def browse(
        self,
        level: str | None = None,
        category: str | None = None,
        first_letter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        Browse words with optional filters.  Returns a list of dicts.
        """
        clauses, params = [], []
        if level:
            clauses.append('level = ?')
            params.append(level.upper())
        if category:
            clauses.append('category = ?')
            params.append(category.lower())
        if first_letter:
            clauses.append('first_letter = ?')
            params.append(first_letter.upper())

        where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
        sql = f"""
            SELECT word, display, article, definition,
                   example_de, example_en, category, level,
                   first_letter, last_letter
            FROM words {where}
            ORDER BY level, word_lower
            LIMIT ? OFFSET ?
        """
        cur = self._get_conn().cursor()
        rows = cur.execute(sql, params + [limit, offset]).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        Full-text search on word, display, and English definition.
        """
        q = f'%{query.lower()}%'
        sql = """
            SELECT word, display, article, definition,
                   example_de, example_en, category, level,
                   first_letter, last_letter
            FROM words
            WHERE word_lower LIKE ?
               OR LOWER(definition) LIKE ?
               OR LOWER(display) LIKE ?
            ORDER BY
                CASE WHEN word_lower = ? THEN 0
                     WHEN word_lower LIKE ? THEN 1
                     ELSE 2 END,
                level
            LIMIT ?
        """
        cur = self._get_conn().cursor()
        rows = cur.execute(
            sql, (q, q, q, query.lower(), f'{query.lower()}%', limit)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── random quiz helpers ───────────────────────────────────────────────

    def random_words(
        self,
        level: str | None = None,
        n: int = 10,
        category: str | None = None,
    ) -> list[dict]:
        """Return *n* random words, optionally filtered by level / category."""
        clauses, params = [], []
        if level:
            levels = self.LEVEL_POOL.get(level.upper(), [level.upper()])
            clauses.append(f"level IN ({','.join('?'*len(levels))})")
            params.extend(levels)
        if category:
            clauses.append('category = ?')
            params.append(category.lower())
        where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
        sql = f"""
            SELECT word, display, article, definition,
                   example_de, example_en, category, level,
                   first_letter, last_letter
            FROM words {where}
            ORDER BY RANDOM()
            LIMIT ?
        """
        cur = self._get_conn().cursor()
        rows = cur.execute(sql, params + [n]).fetchall()
        return [dict(r) for r in rows]

    def get_starting_letters(self, level: str, n: int = 5) -> list[str]:
        """
        Return *n* letters that have at least one word at *level*,
        chosen randomly — used for the coin-toss letter-pick screen.
        """
        levels = self.LEVEL_POOL.get(level.upper(), [level.upper()])
        ph = ','.join('?' * len(levels))
        sql = f"""
            SELECT DISTINCT first_letter
            FROM words
            WHERE level IN ({ph})
            ORDER BY RANDOM()
            LIMIT ?
        """
        cur = self._get_conn().cursor()
        rows = cur.execute(sql, levels + [n]).fetchall()
        return [r[0] for r in rows]

    # ── stats ─────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return a summary of what's in the database."""
        cur = self._get_conn().cursor()
        total = cur.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        by_level = {
            r[0]: r[1]
            for r in cur.execute(
                "SELECT level, COUNT(*) FROM words GROUP BY level ORDER BY level"
            )
        }
        by_category = {
            r[0]: r[1]
            for r in cur.execute(
                "SELECT category, COUNT(*) FROM words GROUP BY category ORDER BY 2 DESC"
            )
        }
        letters = [
            r[0]
            for r in cur.execute(
                "SELECT DISTINCT first_letter FROM words ORDER BY first_letter"
            )
        ]
        return {
            'total': total,
            'by_level': by_level,
            'by_category': by_category,
            'letters_covered': letters,
        }


# ── quick smoke test ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    with GermanDictionary() as db:
        s = db.stats()
        print(f"Total words: {s['total']}")
        print(f"Levels: {s['by_level']}")
        print(f"Letters: {' '.join(s['letters_covered'])}\n")

        print("Computer word starting with 'S' at B1:")
        w = db.get_computer_word('S', 'B1')
        print(f"  → {w['display']}  [{w['level']}]  ({w['definition']})\n")

        print("Validate 'Schule' starting with 'S':")
        r = db.validate_user_word('Schule', 'S')
        print(f"  valid={r['valid']}  info={r['info']['display'] if r['info'] else None}\n")

        print("Validate 'Schule' starting with 'K' (wrong letter):")
        r = db.validate_user_word('Schule', 'K')
        print(f"  valid={r['valid']}  reason={r['reason']}\n")

        print("Validate 'xyz' (nonexistent):")
        r = db.validate_user_word('xyz', 'X')
        print(f"  valid={r['valid']}  reason={r['reason']}\n")

        print("Lookup 'Wasser':")
        info = db.lookup('Wasser')
        print(f"  {info['display']}: {info['definition']}")
        print(f"  Example: {info['example_de']}\n")

        print("Starting letters for B1:")
        print(" ", db.get_starting_letters('B1', n=5))

        print("\n5 random A1 food words:")
        for w in db.random_words(level='A1', category='food', n=5):
            print(f"  {w['display']:20s} {w['definition']}")
