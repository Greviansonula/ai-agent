import pytest
from unittest.mock import patch, MagicMock
from src.tools.database import DatabaseTools
import psycopg2
import couchdb
from loguru import logger

# Test for PostgreSQL query
@pytest.fixture
def mock_postgres_connection():
    # Mocking psycopg2.connect
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn

# Test for CouchDB query
@pytest.fixture
def mock_couchdb_server():
    # Mocking couchdb.Server
    with patch('couchdb.Server') as mock_server:
        mock_db = MagicMock()
        mock_server.return_value = mock_db
        yield mock_db

def test_query_pg_success(mock_postgres_connection):
    db_tools = DatabaseTools()

    # Setup mock cursor
    mock_cursor = MagicMock()
    mock_cursor.description = ['column1', 'column2']
    mock_cursor.fetchall.return_value = [{'column1': 'value1', 'column2': 'value2'}]

    mock_postgres_connection.cursor.return_value = mock_cursor

    sql = "SELECT * FROM users"
    result = db_tools.query_pg(sql)

    assert "value1" in result
    assert "value2" in result
    mock_postgres_connection.cursor.return_value.close.assert_called_once()

def test_query_pg_failure(mock_postgres_connection):
    db_tools = DatabaseTools()

    # Setup mock cursor to raise an error
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_cursor.fetchall.side_effect = psycopg2.Error("Some database error")

    mock_postgres_connection.cursor.return_value = mock_cursor

    sql = "SELECT * FROM non_existent_table"
    result = db_tools.query_pg(sql)

    assert "Query error" in result
    mock_postgres_connection.cursor.return_value.close.assert_called_once()

def test_query_couch_read(mock_couchdb_server):
    db_tools = DatabaseTools()

    # Mock a successful read operation
    db_name = "test_db"
    doc_id = "12345"
    mock_db = mock_couchdb_server[db_name]
    mock_doc = {"_id": doc_id, "data": "test data"}
    mock_db.__getitem__.return_value = mock_doc

    result = db_tools.query_couch(db_name=db_name, doc_id=doc_id, operation="read")

    assert doc_id in result
    assert "data" in result

def test_query_couch_read_document_not_found(mock_couchdb_server):
    db_tools = DatabaseTools()

    # Simulate document not found error
    db_name = "test_db"
    doc_id = "non_existing_doc"
    mock_db = mock_couchdb_server[db_name]
    mock_db.__getitem__.side_effect = couchdb.ResourceNotFound

    result = db_tools.query_couch(db_name=db_name, doc_id=doc_id, operation="read")

    assert "Error" in result
    assert "not found" in result

def test_query_couch_create(mock_couchdb_server):
    db_tools = DatabaseTools()

    # Simulate successful document creation
    db_name = "test_db"
    data = {"name": "test document"}
    mock_db = mock_couchdb_server[db_name]
    mock_db.save.return_value = ("12345", "1-abc")

    result = db_tools.query_couch(db_name=db_name, operation="create", data=data)

    assert "Document created" in result
    assert "12345" in result

def test_query_couch_update(mock_couchdb_server):
    db_tools = DatabaseTools()

    # Simulate successful document update
    db_name = "test_db"
    doc_id = "12345"
    data = {"name": "updated document"}
    mock_db = mock_couchdb_server[db_name]
    mock_db.__getitem__.return_value = {"_id": doc_id, "_rev": "1-abc", "name": "old document"}
    mock_db.save.return_value = ("12345", "2-xyz")

    result = db_tools.query_couch(db_name=db_name, operation="update", doc_id=doc_id, data=data)

    assert "updated" in result
    assert "Document" in result

def test_query_couch_delete(mock_couchdb_server):
    db_tools = DatabaseTools()

    # Simulate successful document deletion
    db_name = "test_db"
    doc_id = "12345"
    mock_db = mock_couchdb_server[db_name]
    mock_db.__getitem__.return_value = {"_id": doc_id, "_rev": "1-abc", "name": "old document"}
    mock_db.delete.return_value = None

    result = db_tools.query_couch(db_name=db_name, operation="delete", doc_id=doc_id)

    assert "deleted" in result
    assert "Document" in result
