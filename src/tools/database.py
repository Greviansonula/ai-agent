import psycopg2
import couchdb
# from ..utils.config import load_config
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()
# TODO: Add a config file for the database connection details

# PostgreSQL connection details
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")
DB_HOST = os.getenv("DB_HOST")

# CouchDB connection details
COUCH_USER = os.getenv("COUCH_USER")
COUCH_PASSWORD = os.getenv("COUCH_PASSWORD")
COUCH_HOST = os.getenv("COUCH_HOST", "localhost")
COUCH_PORT = os.getenv("COUCH_PORT", "5984")

postgres_url = f"postgresql://{PG_USER}:{PG_PASSWORD}@{DB_HOST}/{PG_DB}"
couch_url = f"http://{COUCH_USER}:{COUCH_PASSWORD}@{COUCH_HOST}:{COUCH_PORT}"

print(f"Postgres URL: {postgres_url}")
print(f"CouchDB URL: {couch_url}")


class DatabaseTools:
    """Database connection and query execution tools."""
    def __init__(self):
        # config = load_config()
        self.conn = psycopg2.connect(postgres_url)
        self.couch = couchdb.Server(couch_url)

    def query_pg(self, sql: str) -> str:
        """Execute SQL queries safely"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            if cursor.description:
                result = cursor.fetchall()
                return "\n".join(str(row) for row in result)
            else:
                self.conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
        except Exception as e:
            return f"Query error: {str(e)}"
        # finally:
        #     self.conn.close()

        
    def query_couch(self, db_name: str, doc_id: str = None, query: dict = None, operation: str = "read", data: dict = None) -> str:
        """
        Perform CRUD operations on CouchDB documents in a specific database.

        """
        logger.info(f"Performing operation '{operation}' on CouchDB database '{db_name}' - doc_id: {doc_id}, query: {query}, data: {data}")

        try:
            # Check if the database exists
            if db_name not in self.couch:
                return f"Error: Database '{db_name}' does not exist."

            db = self.couch[db_name]

            if operation == "read":
                if doc_id:
                    # Fetch a specific document by ID
                    try:
                        doc = db[doc_id]
                        return str(doc)
                    except couchdb.ResourceNotFound:
                        return f"Error: Document with ID '{doc_id}' not found in database '{db_name}'."
                else:
                    # Use mango query to list documents
                    try:
                        results = db.find(query)
                        return "\n".join(str(doc) for doc in results)
                    except Exception as e:
                        logger.error(f"Error querying CouchDB: {str(e)}")
                        return f"Error: {str(e)}"

            elif operation == "create":
                if not data:
                    return "Error: 'data' is required for create operation."
                # Create a new document
                doc_id, doc_rev = db.save(data)
                return f"Document created with ID: {doc_id} and revision: {doc_rev}"

            elif operation == "update":
                if not doc_id or not data:
                    return "Error: 'doc_id' and 'data' are required for update operation."
                # Fetch the existing document
                try:
                    doc = db[doc_id]
                    doc.update(data)
                    db.save(doc)
                    return f"Document with ID '{doc_id}' updated successfully."
                except couchdb.ResourceNotFound:
                    return f"Error: Document with ID '{doc_id}' not found in database '{db_name}'."

            elif operation == "delete":
                if not doc_id:
                    return "Error: 'doc_id' is required for delete operation."
                # Fetch the existing document
                try:
                    doc = db[doc_id]
                    db.delete(doc)
                    return f"Document with ID '{doc_id}' deleted successfully."
                except couchdb.ResourceNotFound:
                    return f"Error: Document with ID '{doc_id}' not found in database '{db_name}'."

            else:
                return f"Error: Invalid operation '{operation}'. Supported operations: 'create', 'read', 'update', 'delete'."

        except Exception as e:
            logger.error(f"Failed to connect to CouchDB: {str(e)}")
            return f"Error: Failed to connect to CouchDB. {str(e)}"
    