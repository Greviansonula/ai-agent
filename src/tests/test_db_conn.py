import os
import psycopg2
import couchdb
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# PostgreSQL credentials
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")
DB_HOST = os.getenv("DB_HOST")

# CouchDB credentials
COUCH_USER = os.getenv("COUCH_USER")
COUCH_PASSWORD = os.getenv("COUCH_PASSWORD")
COUCH_HOST = os.getenv("COUCH_HOST", "localhost")
COUCH_PORT = os.getenv("COUCH_PORT", "5984")

postgres_url = f"postgresql://{PG_USER}:{PG_PASSWORD}@{DB_HOST}/{PG_DB}"
couch_url = f"http://{COUCH_USER}:{COUCH_PASSWORD}@{COUCH_HOST}:{COUCH_PORT}"

print(f"Postgres URL: {postgres_url}")
print(f"CouchDB URL: {couch_url}")

# --- PostgreSQL connection ---
pg_conn = None
try:
    pg_conn = psycopg2.connect(postgres_url)
    logger.info("✅ PostgreSQL connection established.")
    
    cursor = pg_conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print("PostgreSQL Tables:", [table[0] for table in tables])
    cursor.close()
except Exception as e:
    logger.error(f"❌ PostgreSQL connection failed: {e}")
finally:
    if pg_conn:
        pg_conn.close()

# --- CouchDB connection ---
try:
    couch = couchdb.Server(couch_url)
    couch.resource.credentials = (COUCH_USER, COUCH_PASSWORD)
    logger.info("✅ CouchDB connection established.")

    # List existing databases
    print("CouchDB Databases:", couch.all_dbs())

    # Create or access _users database
    if "_users" not in couch:
        couch.create("_users")
        logger.info("✅ Created '_users' database.")
    users_db = couch["_users"]

    # Insert 3 sample user accounts
    users = [
        {"_id": "org.couchdb.user:user1", "name": "user1", "type": "user", "roles": [], "password": "password1", "email": "user1@example.com"},
        {"_id": "org.couchdb.user:user2", "name": "user2", "type": "user", "roles": ["reader"], "password": "password2", "email": "user2@example.com"},
        {"_id": "org.couchdb.user:user3", "name": "user3", "type": "user", "roles": ["admin"], "password": "password3", "email": "user3@example.com"},
    ]

    for user in users:
        user_id = user["_id"]
        if user_id not in users_db:
            users_db.save(user)
            logger.info(f"✅ Inserted: {user['name']}")
        else:
            logger.info(f"⚠️ User already exists: {user['name']}")

except Exception as e:
    logger.error(f"❌ CouchDB error: {e}")
