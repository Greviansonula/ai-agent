import os
import psycopg2
import couchdb

from loguru import logger
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

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

# Create an MCP server
mcp = FastMCP("Data Support Agent")


@mcp.tool()
def query_pg(sql: str) -> str:
    """Execute SQL queries safely"""
    logger.info(f"Executing SQL query: {sql}")
    conn = psycopg2.connect(
        user=PG_USER,
        password=PG_PASSWORD,
        host=DB_HOST,
        database=PG_DB
    )
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Check if the query returns results
        if cursor.description:
            result = cursor.fetchall()
            return "\n".join(str(row) for row in result)
        else:
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

@mcp.tool()
def query_couch(db_name: str, doc_id: str = None, query: dict = None, operation: str = "read", data: dict = None) -> str:
    """
    Perform CRUD operations on CouchDB documents in a specific database.

    Args:
        db_name (str): Name of the CouchDB database.
        doc_id (str): Document ID to fetch, update, or delete a specific document.
        query (dict): Mango query to list documents (if doc_id is not provided).
        operation (str): The type of operation to perform. Options: "create", "read", "update", "delete".
        data (dict): The data to use for create or update operations.

    Returns:
        str: The result of the operation.
    """
    logger.info(f"Performing operation '{operation}' on CouchDB database '{db_name}' - doc_id: {doc_id}, query: {query}, data: {data}")

    try:
        # Connect to CouchDB
        couch = couchdb.Server(couch_url)

        # Check if the database exists
        if db_name not in couch:
            return f"Error: Database '{db_name}' does not exist."

        db = couch[db_name]

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



@mcp.prompt()
def mobilization_prompt(previous_membership: str, current_membership: str) -> str:
    return f"Please review this location mobilized from {previous_membership} to {current_membership}"


if __name__ == "__main__":
    print("Starting server...")
    # Initialize and run the server
    mcp.run(transport="stdio")