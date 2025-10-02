import sqlite3
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

DB = Path(r"d:\Classes\Fall 2025\IS 330\python machine learning\app.db")
if not DB.exists():
    print("DB not found:", DB)
    raise SystemExit(1)

def clean_character_name(name):
    # List of titles and ranks to remove
    titles = [
        'Dr.', 'Doctor', 'Captain', 'Capt.', 'Lt.', 'Lieutenant',
        'Commander', 'Cmdr.', 'Colonel', 'Col.',
        'Admiral', 'Adm.', 'Professor', 'Prof.',
        'Vice Admiral', 'Ensign', 'General', 'Nurse',
        'Lieutenant jg', 'Lt. Cmdr.'
    ]
    
    # Remove titles and rank designations
    cleaned_name = name
    
    # Remove "Lieutenant jg" specifically first (order matters)
    if 'Lieutenant jg' in cleaned_name:
        cleaned_name = cleaned_name.replace('Lieutenant jg', '').strip()
    
    # Then remove other titles
    for title in titles:
        if cleaned_name.lower().startswith(title.lower() + ' '):
            cleaned_name = cleaned_name[len(title):].strip()
    
    # Remove any parenthetical content
    cleaned_name = cleaned_name.split('(')[0].strip()
    
    # Handle specific character mappings
    name_mapping = {
        'William T. Riker': 'William_Riker',
        'Julian Bashir': 'Julian_Bashir',
        'Data': 'Data_(android)',
        'Lt. Cmdr. Data': 'Data_(android)',
        'Kira Nerys': 'Kira_Nerys',
        'Zefram Cochrane': 'Zefram_Cochrane',
        'Leah Brahms': 'Leah_Brahms',
        'K\'orin': 'Korin',  # Handle special characters
    }
    
    # Clean up the name
    cleaned_name = cleaned_name.strip()
    
    # Check for the full name in mapping first
    if name in name_mapping:
        return name_mapping[name]
    
    # Then check for the cleaned name
    if cleaned_name in name_mapping:
        return name_mapping[cleaned_name]
    
    # Handle special cases for Data
    if 'Data' in cleaned_name:
        return 'Data_(android)'
        
    # Replace spaces with underscores for URL
    return cleaned_name.replace(' ', '_')

def get_species_from_memory_alpha(character_name):
    base_url = "https://memory-alpha.fandom.com/wiki/"
    cleaned_name = clean_character_name(character_name)
    url = base_url + cleaned_name
    
    try:
        # Add a small delay to be nice to the server
        time.sleep(1)
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for species information in the infobox
        aside = soup.find('aside', class_='portable-infobox')
        if aside:
            # Find all data items
            data_items = aside.find_all('div', class_='pi-item')
            for item in data_items:
                # Look for the species label
                label = item.find('h3', class_='pi-data-label')
                if label and 'Species' in label.text:
                    # Get the species value
                    value = item.find('div', class_='pi-data-value')
                    if value:
                        return value.text.strip()
        
        # If we couldn't find it in the infobox, try searching the page text
        species_section = soup.find('b', string='Species:')
        if species_section:
            species = species_section.find_next().text.strip()
            return species
            
        return "Unknown"
        
    except requests.RequestException as e:
        print(f"Error fetching species for {character_name}: {e}")
        return "Unknown"

def update_species_in_db():
    con = sqlite3.connect(str(DB))
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    
    # Get all characters
    cur.execute("SELECT id, character_name FROM characters WHERE species IS NULL OR species = 'Unknown';")
    characters = cur.fetchall()
    
    for char_id, character_name in characters:
        print(f"Fetching species for {character_name}...")
        species = get_species_from_memory_alpha(character_name)
        
        # Update the database
        cur.execute("UPDATE characters SET species = ? WHERE id = ?;", (species, char_id))
        print(f"Updated {character_name}: {species}")
        
        # Commit after each update to save progress
        con.commit()
    
    con.close()
    print("Species update complete!")

if __name__ == "__main__":
    print("Starting species update process...")
    update_species_in_db()
