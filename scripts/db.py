import couchdb
from dotenv import load_dotenv
import os

load_dotenv()

# CouchDB connection details
COUCH_USER = os.getenv("COUCH_USER")
COUCH_PASSWORD = os.getenv("COUCH_PASSWORD")
COUCH_HOST = os.getenv("COUCH_HOST", "localhost")
COUCH_PORT = os.getenv("COUCH_PORT", "5984")

COUCHDB_URL = f"http://{COUCH_USER}:{COUCH_PASSWORD}@{COUCH_HOST}:{COUCH_PORT}"

# Update these with your CouchDB connection details
DATABASE_NAME = "_users"

def create_database(couchdb_url, db_name):
    # Connect to the CouchDB server
    couch = couchdb.Server(couchdb_url)
    print(f"Connected to CouchDB at {couchdb_url}")
    
    # Check if the database exists; if not, create it
    if db_name in couch:
        print(f"Database '{db_name}' already exists!")
        db = couch[db_name]
    else:
        db = couch.create(db_name)
        print(f"Database '{db_name}' created successfully!")
    
    return db

if __name__ == "__main__":
    db = create_database(COUCHDB_URL, DATABASE_NAME)
