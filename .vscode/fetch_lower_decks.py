import sqlite3
from pathlib import Path
import requests
from bs4 import BeautifulSoup

def get_cast_from_section(soup, section_id):
    section = soup.find('span', {'id': section_id})
    if not section:
        print(f"Could not find '{section_id}' section on the page")
        return []
        
    section = section.parent
    cast_list = section.find_next('ul').find_all('li')
    
    cast_members = []
    for item in cast_list:
        text = item.get_text()
        if ' as ' in text:
            actor, character = text.split(' as ')
            # Clean up any trailing notes or parentheses
            character = character.split('(')[0].strip()
            # Remove any text after commas (additional character names)
            character = character.split(',')[0].strip()
            actor = actor.strip()
            cast_members.append((actor, character))
    
    return cast_members

def fetch_cast_data():
    url = "https://memory-alpha.fandom.com/wiki/Star_Trek:_Lower_Decks#Starring"
    print("Fetching data from Memory Alpha wiki...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        cast_members = []
        
        # Get main cast
        main_cast = get_cast_from_section(soup, 'Starring')
        if main_cast:
            print(f"Found {len(main_cast)} main cast members")
            cast_members.extend(main_cast)
            
        # Get special guest stars
        special_guests = get_cast_from_section(soup, 'Special_guest_stars')
        if special_guests:
            print(f"Found {len(special_guests)} special guest stars")
            cast_members.extend(special_guests)
            
        # Get recurring characters
        recurring = get_cast_from_section(soup, 'Additional_recurring_characters')
        if recurring:
            print(f"Found {len(recurring)} recurring characters")
            cast_members.extend(recurring)
        
        return cast_members
        
    except requests.RequestException as e:
        raise Exception(f"Error fetching data from website: {e}")
    except Exception as e:
        raise Exception(f"Error parsing cast data: {e}")

def main():
    # Connect to the database
    db_path = Path(__file__).resolve().parent.parent / "app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Clear existing data and reset the ID counter
        cursor.execute("DELETE FROM characters")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='characters'")
        print("Cleared existing data and reset ID counter")
        
        # Fetch cast data from the website
        cast_members = fetch_cast_data()
        
        if not cast_members:
            raise ValueError("No cast members found on the page")
            
        print(f"Found {len(cast_members)} cast members")
        
        # Track unique characters while preserving order
        seen_characters = {}  # character -> actor mapping
        
        # Process in order, keeping only first occurrence of each character
        for actor, character in cast_members:
            if character not in seen_characters:
                seen_characters[character] = actor
        
        # Insert the unique characters
        for character, actor in seen_characters.items():
            cursor.execute(
                "INSERT INTO characters (character_name, actor_name) VALUES (?, ?)",
                (character, actor)
            )
        
        # Commit the transaction
        conn.commit()
        print(f"Successfully added {len(seen_characters)} unique characters to database!")
        
    except Exception as e:
        conn.rollback()  # Roll back on any error
        print(f"Error: {e}")
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()