"""
Database connection module for MySQL connections.
Handles connection pooling and management using mysql-connector-python.
"""

import mysql.connector
from mysql.connector import Error as MySQLError
from contextlib import contextmanager
from typing import Optional
import logging

from gambling_app_core.config import APP_CONFIG
from gambling_app_core.exceptions import ConnectionException, DatabaseException


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages MySQL database connections."""
    
    _instance: Optional["DatabaseConnection"] = None
    
    def __init__(self):
        """Initialize database connection (singleton pattern)."""
        self.connection = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to MySQL database."""
        try:
            config = APP_CONFIG.database.to_dict()
            logger.info(f"Connecting to database: {config['database']}")
            
            self.connection = mysql.connector.connect(**config)
            
            if self.connection.is_connected():
                logger.info("Database connection established successfully")
        except MySQLError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionException(f"Database connection failed: {str(e)}")
    
    @staticmethod
    def get_instance() -> "DatabaseConnection":
        """Get singleton instance of database connection."""
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = DatabaseConnection()
        return DatabaseConnection._instance
    
    def get_connection(self):
        """Get the database connection object."""
        if self.connection is None or not self.connection.is_connected():
            self._connect()
        return self.connection
    
    @contextmanager
    def get_cursor(self, buffered: bool = False):
        """
        Context manager for database cursor.
        Automatically handles cursor closure.
        """
        cursor = None
        try:
            cursor = self.get_connection().cursor(dictionary=True, buffered=buffered)
            yield cursor
            self.get_connection().commit()
        except MySQLError as e:
            self.get_connection().rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseException(f"Database operation failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            List of result rows
        """
        try:
            with self.get_cursor(buffered=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except MySQLError as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseException(f"Query execution failed: {str(e)}")
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """
        Execute an INSERT query and return inserted ID.
        
        Args:
            query: SQL INSERT query string
            params: Query parameters (optional)
        
        Returns:
            ID of inserted row
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except MySQLError as e:
            logger.error(f"Insert failed: {e}")
            raise DatabaseException(f"Insert failed: {str(e)}")
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE query and return affected rows.
        
        Args:
            query: SQL UPDATE query string
            params: Query parameters (optional)
        
        Returns:
            Number of affected rows
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except MySQLError as e:
            logger.error(f"Update failed: {e}")
            raise DatabaseException(f"Update failed: {str(e)}")
    
    def execute_delete(self, query: str, params: tuple = None) -> int:
        """
        Execute a DELETE query and return affected rows.
        
        Args:
            query: SQL DELETE query string
            params: Query parameters (optional)
        
        Returns:
            Number of affected rows
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except MySQLError as e:
            logger.error(f"Delete failed: {e}")
            raise DatabaseException(f"Delete failed: {str(e)}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")


class DatabaseSetup:
    """Handles database initialization and schema creation."""
    
    @staticmethod
    def create_tables() -> None:
        """Create all required database tables."""
        db = DatabaseConnection.get_instance()
        
        # SQL to create all tables
        create_tables_sql = [
            # Gamblers table
            """
            CREATE TABLE IF NOT EXISTS gamblers (
                gambler_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                starting_stake DECIMAL(15, 2) NOT NULL,
                current_stake DECIMAL(15, 2) NOT NULL,
                win_threshold DECIMAL(15, 2) NOT NULL,
                loss_threshold DECIMAL(15, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_name (name)
            )
            """,
            
            # Sessions table
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                gambler_id INT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP NULL,
                starting_stake DECIMAL(15, 2) NOT NULL,
                ending_stake DECIMAL(15, 2) NULL,
                total_bets INT DEFAULT 0,
                total_wins INT DEFAULT 0,
                total_losses INT DEFAULT 0,
                session_status VARCHAR(50) NOT NULL DEFAULT 'active',
                pause_count INT DEFAULT 0,
                FOREIGN KEY (gambler_id) REFERENCES gamblers(gambler_id) ON DELETE CASCADE,
                INDEX idx_gambler_status (gambler_id, session_status),
                INDEX idx_start_time (start_time)
            )
            """,
            
            # Bets table
            """
            CREATE TABLE IF NOT EXISTS bets (
                bet_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                gambler_id INT NOT NULL,
                bet_amount DECIMAL(15, 2) NOT NULL,
                betting_strategy VARCHAR(100) NOT NULL,
                odds DECIMAL(10, 4) NOT NULL,
                odd_type VARCHAR(50) NOT NULL,
                placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                outcome VARCHAR(50) DEFAULT 'pending',
                result_amount DECIMAL(15, 2) NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                FOREIGN KEY (gambler_id) REFERENCES gamblers(gambler_id) ON DELETE CASCADE,
                INDEX idx_session_outcome (session_id, outcome),
                INDEX idx_gambler_id (gambler_id)
            )
            """,
            
            # Transactions table (audit trail)
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                gambler_id INT NOT NULL,
                session_id INT NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                previous_balance DECIMAL(15, 2) NOT NULL,
                new_balance DECIMAL(15, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description VARCHAR(255),
                FOREIGN KEY (gambler_id) REFERENCES gamblers(gambler_id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                INDEX idx_gambler_created (gambler_id, created_at),
                INDEX idx_session_created (session_id, created_at)
            )
            """,
            
            # Statistics table
            """
            CREATE TABLE IF NOT EXISTS statistics (
                statistic_id INT AUTO_INCREMENT PRIMARY KEY,
                gambler_id INT NOT NULL UNIQUE,
                total_sessions INT DEFAULT 0,
                total_bets INT DEFAULT 0,
                total_wins INT DEFAULT 0,
                total_losses INT DEFAULT 0,
                total_profit_loss DECIMAL(15, 2) DEFAULT 0,
                win_rate DECIMAL(5, 2) DEFAULT 0,
                peak_stake DECIMAL(15, 2) DEFAULT 0,
                lowest_stake DECIMAL(15, 2) DEFAULT 0,
                average_bet DECIMAL(15, 2) DEFAULT 0,
                longest_win_streak INT DEFAULT 0,
                longest_loss_streak INT DEFAULT 0,
                volatility DECIMAL(10, 4) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (gambler_id) REFERENCES gamblers(gambler_id) ON DELETE CASCADE
            )
            """
        ]
        
        try:
            with db.get_cursor() as cursor:
                for sql in create_tables_sql:
                    cursor.execute(sql)
                logger.info("All database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise DatabaseException(f"Failed to create tables: {str(e)}")
    
    @staticmethod
    def drop_all_tables() -> None:
        """Drop all database tables (use with caution)."""
        db = DatabaseConnection.get_instance()
        tables = [
            "bets",
            "transactions",
            "statistics",
            "sessions",
            "gamblers"
        ]
        
        try:
            with db.get_cursor() as cursor:
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info("All tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise DatabaseException(f"Failed to drop tables: {str(e)}")
