"""
Main entry point for the Gambling Simulation System.
Initializes the application and starts the UI.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gambling_app_utils import LoggerSetup
from gambling_app_db import DatabaseSetup, DatabaseConnection
from gambling_app_core import APP_CONFIG
from gambling_app_ui import GamblingUI
from gambling_app_core import GamblingAppException


def initialize_app():
    """Initialize the application."""
    try:
        # Setup logging
        logger = LoggerSetup.setup()
        logger.info("=" * 70)
        logger.info("Starting Gambling Simulation System")
        logger.info("=" * 70)
        
        # Initialize database
        print("Initializing database...")
        DatabaseSetup.create_tables()
        logger.info("Database initialized successfully")
        
        print("Database initialized successfully!\n")
        
        return True
    
    except GamblingAppException as e:
        print(f"Initialization error: {e}")
        logger.error(f"Initialization error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during initialization: {e}")
        logger.error(f"Unexpected error during initialization: {e}")
        return False


def main():
    """Main application entry point."""
    try:
        # Initialize application
        if not initialize_app():
            sys.exit(1)
        
        # Start UI
        ui = GamblingUI()
        ui.run()
    
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Close database connection
        db = DatabaseConnection.get_instance()
        db.close()


if __name__ == "__main__":
    main()
