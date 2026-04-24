"""
Database initialization and reset script.
Use this to set up or reset the gamblingapp database.
"""

import sys
from pathlib import Path
import mysql.connector
from mysql.connector import Error as MySQLError

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gambling_app_core import APP_CONFIG
from gambling_app_db import DatabaseSetup, DatabaseConnection
from gambling_app_utils import LoggerSetup


def create_database():
    """Create the gamblingapp database if it doesn't exist."""
    try:
        print(f"Creating database: {APP_CONFIG.database.database}")
        
        # Connect to MySQL server (without database)
        config = {
            "host": APP_CONFIG.database.host,
            "user": APP_CONFIG.database.user,
            "password": APP_CONFIG.database.password,
            "port": APP_CONFIG.database.port
        }
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {APP_CONFIG.database.database}")
        print(f"Database '{APP_CONFIG.database.database}' created successfully")
        
        cursor.close()
        conn.close()
    
    except MySQLError as e:
        print(f"Error creating database: {e}")
        return False
    
    return True


def setup_database():
    """Set up the database with all tables."""
    try:
        print("\nSetting up database tables...")
        DatabaseSetup.create_tables()
        print("Database tables created successfully")
        return True
    
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False


def reset_database():
    """Reset the database by dropping all tables."""
    try:
        confirm = input("\nWARNING: This will delete all data. Are you sure? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("Reset cancelled")
            return False
        
        print("Dropping all tables...")
        DatabaseSetup.drop_all_tables()
        
        print("Recreating tables...")
        DatabaseSetup.create_tables()
        
        print("Database reset successfully")
        return True
    
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False


def main():
    """Main initialization script."""
    try:
        # Setup logging
        LoggerSetup.setup()
        
        print("=" * 70)
        print("Gambling Simulation System - Database Initialization")
        print("=" * 70)
        print()
        
        print("Available options:")
        print("1. Create/Initialize database")
        print("2. Reset database (WARNING: deletes all data)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            if create_database():
                if setup_database():
                    print("\n✓ Database initialization complete!")
            else:
                print("\n✗ Database initialization failed")
                sys.exit(1)
        
        elif choice == "2":
            if reset_database():
                print("\n✓ Database reset complete!")
            else:
                print("\n✗ Database reset failed")
                sys.exit(1)
        
        elif choice == "3":
            print("Exiting...")
            sys.exit(0)
        
        else:
            print("Invalid choice")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        # Close database connection
        db = DatabaseConnection.get_instance()
        db.close()


if __name__ == "__main__":
    main()
