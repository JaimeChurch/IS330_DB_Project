import sqlite3
from pathlib import Path
from collections import Counter

# Use the same database path as other scripts
DB = Path(r"d:\Classes\Fall 2025\IS 330\python machine learning\app.db")
if not DB.exists():
    print("DB not found:", DB)
    raise SystemExit(1)

def find_common_species():
    con = sqlite3.connect(str(DB))
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    
    # Query to get all species and count them
    cur.execute("""
        SELECT species, COUNT(*) as count 
        FROM characters 
        WHERE species IS NOT NULL 
        GROUP BY species 
        ORDER BY count DESC;
    """)
    
    species_counts = cur.fetchall()
    
    # Print results in a formatted way
    print("\nSpecies Distribution:")
    print("-" * 40)
    
    if not species_counts:
        print("No species data found in the database.")
    else:
        # Calculate total for percentage
        total_characters = sum(count for _, count in species_counts)
        
        # Print each species with count and percentage
        for species, count in species_counts:
            percentage = (count / total_characters) * 100
            print(f"{species:<20} {count:>3} characters ({percentage:>5.1f}%)")
    
    con.close()

if __name__ == "__main__":
    find_common_species()
