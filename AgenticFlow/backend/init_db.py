#!/usr/bin/env python3
"""
Initialize the database and run migrations.

This script initializes the database and runs any pending migrations.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from database.migrations import init_migrations, ensure_latest, reset_db

def main():
    """Main entry point for the database initialization script."""
    parser = argparse.ArgumentParser(description='Initialize and manage the database.')
    parser.add_argument('--reset', action='store_true', help='Reset the database (DANGEROUS!)')
    args = parser.parse_args()
    
    try:
        if args.reset:
            confirm = input("WARNING: This will delete all data. Are you sure? (y/n) ")
            if confirm.lower() == 'y':
                reset_db()
                print("Database reset complete.")
            else:
                print("Reset cancelled.")
                return
        
        # Initialize migrations if needed
        migrations_dir = os.path.join(os.path.dirname(__file__), 'database', 'alembic')
        if not os.path.exists(migrations_dir):
            print("Initializing migrations...")
            init_migrations()
        
        # Ensure the database is at the latest migration
        print("Ensuring database is up to date...")
        ensure_latest()
        
        print("Database initialization complete.")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
