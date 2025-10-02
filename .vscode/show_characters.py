import sqlite3
from pathlib import Path

DB = Path(r"d:\Classes\Fall 2025\IS 330\python machine learning\app.db")
if not DB.exists():
    print("DB not found:", DB); raise SystemExit(1)

con = sqlite3.connect(str(DB))
con.execute("PRAGMA foreign_keys = ON;")
cur = con.cursor()
cur.execute("SELECT id, character_name, actor_name, species FROM characters ORDER BY id;")
rows = cur.fetchall()
if not rows:
    print("No characters found")
else:
    print("ID  Character Name        Actor Name             Species")
    print("-" * 70)
    for id_, character, actor, species in rows:
        print(f"{id_:>2}. {character:<20} {actor:<20} {species}")
con.close()