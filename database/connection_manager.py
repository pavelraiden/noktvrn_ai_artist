"""
Database Connection Manager for PostgreSQL.

This module provides a centralized way to manage PostgreSQL database connections
using a connection pool.
"""

import os
import logging
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database connection parameters (Ideally from environment variables)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ai_artist_db")
DB_USER = os.environ.get("DB_USER", "ai_artist_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secure_password")

# Connection pool settings
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10

connection_pool = None


def init_connection_pool():
    """Initializes the PostgreSQL connection pool."""
    global connection_pool
    if connection_pool is None:
        try:
            # Fixed the unterminated string literal by ensuring the f-string is properly closed
            logger.info(
                f"Initializing PostgreSQL connection pool for database "
                f"{DB_NAME} on {DB_HOST}:{DB_PORT}"
            )
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                MIN_CONNECTIONS,
                MAX_CONNECTIONS,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
            )
            logger.info("PostgreSQL connection pool initialized successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(
                f"Error while initializing PostgreSQL connection pool: {error}",
                exc_info=True,
            )
            connection_pool = None  # Ensure pool is None if init fails
            raise
    else:
        logger.warning("Connection pool already initialized.")


@contextmanager
def get_db_connection():
    """Provides a database connection from the pool using a context manager."""
    global connection_pool
    if connection_pool is None:
        logger.error(
            "Connection pool is not initialized. Call init_connection_pool() first."
        )
        raise ConnectionError("Connection pool not initialized.")

    conn = None
    try:
        conn = connection_pool.getconn()
        if conn:
            logger.debug("Acquired connection from pool.")
            yield conn
        else:
            logger.error("Failed to get connection from pool.")
            raise ConnectionError("Failed to get connection from pool.")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error getting connection from pool: {error}", exc_info=True)
        # If error occurs during yield, conn might be None or invalid
        # The finally block will attempt to put it back, which might fail
        # but is generally the correct pattern for pool management.
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)
            logger.debug("Released connection back to pool.")


@contextmanager
def get_db_cursor(commit=False):
    """Provides a database cursor from a connection using a context manager."""
    with get_db_connection() as conn:
        cursor = None
        try:
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
                logger.debug("Transaction committed.")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Database cursor error: {error}", exc_info=True)
            if conn:  # Check if connection exists before rollback
                conn.rollback()
                logger.warning("Transaction rolled back due to error.")
            raise
        finally:
            if cursor:
                cursor.close()
                logger.debug("Cursor closed.")


def close_connection_pool():
    """Closes all connections in the pool."""
    global connection_pool
    if connection_pool:
        logger.info("Closing PostgreSQL connection pool.")
        connection_pool.closeall()
        connection_pool = None
        logger.info("PostgreSQL connection pool closed.")
    else:
        logger.warning("Connection pool was not initialized or already closed.")


# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        init_connection_pool()

        # Test getting a connection and cursor
        with get_db_cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            logger.info(f"Database version: {db_version}")

        # Test another connection
        with get_db_cursor(commit=True) as cursor:
            # Example: Create a dummy table (if it doesn\t exist)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50)
                );
            """
            )
            # Example: Insert data
            cursor.execute("INSERT INTO test_table (name) VALUES (%s);", ("Test Name",))
            logger.info("Dummy data inserted.")

    except Exception as e:
        logger.error(f"An error occurred during example usage: {e}")
    finally:
        close_connection_pool()
