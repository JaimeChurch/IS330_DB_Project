from pathlib import Path
import sqlite3
import argparse

DEFAULT_DB = Path(__file__).resolve().parent.parent / "app.db"

SQL_CREATE = [
	"""
	CREATE TABLE IF NOT EXISTS characters (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		character_name TEXT NOT NULL UNIQUE,
		actor_name TEXT NOT NULL,
		species TEXT
	);
	"""
]

SEED_CHARACTERS = [
    ("James T. Kirk", "William Shatner", "Human"),
    ("Spock", "Leonard Nimoy", "Vulcan/Human"),
    ("Leonard McCoy", "DeForest Kelley", "Human"),
    ("Montgomery Scott", "James Doohan", "Human"),
    ("Uhura", "Nichelle Nichols", "Human"),
    ("Hikaru Sulu", "George Takei", "Human"),
    ("Pavel Chekov", "Walter Koenig", "Human")
]

def create_database(path: Path) -> sqlite3.Connection:
	path.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(str(path))
	conn.execute("PRAGMA foreign_keys = ON;")
	cur = conn.cursor()
	for s in SQL_CREATE:
		cur.executescript(s)
	conn.commit()
	return conn

def seed(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO characters 
        (character_name, actor_name, species) 
        VALUES (?, ?, ?);
        """, SEED_CHARACTERS)
    conn.commit()

def list_tables(conn: sqlite3.Connection):
	cur = conn.cursor()
	cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
	return [r[0] for r in cur.fetchall()]


def counts(conn: sqlite3.Connection, tables):
	cur = conn.cursor()
	out = {}
	for t in tables:
		cur.execute(f"SELECT COUNT(*) FROM {t}")
		out[t] = cur.fetchone()[0]
	return out

def main(argv=None):
	ap = argparse.ArgumentParser()
	ap.add_argument("--db", default=str(DEFAULT_DB), help="Path to sqlite db file")
	ap.add_argument("--seed", action="store_true", help="Insert example rows")
	args = ap.parse_args(argv)

	db_path = Path(args.db)
	conn = create_database(db_path)
	print(f"Database created/opened: {db_path}")
	if args.seed:
		seed(conn)
		print("Inserted seed data")

	tables = list_tables(conn)
	cnts = counts(conn, tables)
	print("Tables and counts:")
	for t in tables:
		print(f" - {t}: {cnts.get(t, 0)}")

	conn.close()

if __name__ == '__main__':
	main()
