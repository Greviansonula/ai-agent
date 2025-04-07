#!/usr/bin/env python3
from src.tools.database import DatabaseTools
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Data Support Agent", "0.1.0")
db_tools = DatabaseTools()

@mcp.tool()
async def query_pg(sql: str) -> str:
    """Execute SQL queries safely"""
    return db_tools.query_pg(sql)

@mcp.tool()
def query_couch(db_name: str, doc_id: str = None, query: dict = None, operation: str = "read", data: dict = None) -> str:
    # db_name: str, doc_id: str = None, query: dict = None
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
    return db_tools.query_couch(db_name, doc_id, query, operation, data)

if __name__ == "__main__":
    print("Starting server...")
    # Initialize and run the server
    mcp.run(transport="stdio")
    