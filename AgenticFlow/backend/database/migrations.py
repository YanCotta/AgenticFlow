"""
Database migration utilities for AgenticFlow.

This module provides functions for managing database schema migrations.
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import settings
from . import Base, engine

def get_alembic_config() -> Config:
    """Get the Alembic configuration."""
    # Get the directory where this file is located
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the alembic.ini file
    ini_path = os.path.join(Path(__file__).parent.parent, 'alembic.ini')
    
    # Create and configure the Alembic config
    alembic_cfg = Config(ini_path)
    
    # Set the script location to the migrations directory
    alembic_cfg.set_main_option('script_location', os.path.join(migrations_dir, 'alembic'))
    
    # Set the database URL
    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
    
    return alembic_cfg

def ensure_migrations_table(connection):
    """Ensure the alembic_version table exists."""
    context = MigrationContext.configure(connection)
    if not context._has_version_table():
        context._ensure_version_table()


def init_migrations():
    """Initialize the migrations directory."""
    # Create the migrations directory if it doesn't exist
    migrations_dir = os.path.join(os.path.dirname(__file__), 'alembic')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
    
    # Initialize the Alembic environment
    alembic_cfg = get_alembic_config()
    command.init(alembic_cfg, directory=migrations_dir, template='generic')
    
    # Update the env.py file to use our models
    env_py = os.path.join(migrations_dir, 'env.py')
    with open(env_py, 'r') as f:
        content = f.read()
    
    # Add imports and model metadata
    content = content.replace(
        'from logging.config import fileConfig',
        'from logging.config import fileConfig\n'
        'from database.models_new import Base\n'
        'from database import Base\n'
    )
    
    content = content.replace(
        'target_metadata = None',
        'target_metadata = Base.metadata'
    )
    
    with open(env_py, 'w') as f:
        f.write(content)
    
    print(f"Initialized migrations in {migrations_dir}")


def create_migration(message: str = None):
    """Create a new migration."""
    if not message:
        message = input("Enter migration name: ")
    
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=True)


def upgrade(revision: str = 'head'):
    """Upgrade the database to a later version."""
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)


def downgrade(revision: str):
    """Revert the database to a previous version."""
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)


def current():
    """Show the current revision."""
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)


def history():
    """Show migration history."""
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)


def ensure_latest():
    """Ensure the database is at the latest migration."""
    alembic_cfg = get_alembic_config()
    
    # Get the current database revision
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
    
    # Get the latest revision from the filesystem
    script = ScriptDirectory.from_config(alembic_cfg)
    head_rev = script.get_current_head()
    
    if current_rev != head_rev:
        print(f"Database is at revision {current_rev}, upgrading to {head_rev}...")
        upgrade()
    else:
        print("Database is up to date.")


def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    from . import recreate_db
    print("Database reset complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m database.migrations <command> [args...]")
        print("\nCommands:")
        print("  init           Initialize migrations")
        print("  migrate        Create a new migration")
        print("  upgrade [rev]  Upgrade to a later version (default: head)")
        print("  downgrade rev  Revert to a previous version")
        print("  current        Show current revision")
        print("  history        Show migration history")
        print("  ensure-latest  Ensure database is at latest migration")
        print("  reset          Reset the database (DANGEROUS!)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_migrations()
    elif command == "migrate":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_migration(message)
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
        upgrade(revision)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("Error: revision is required")
            sys.exit(1)
        downgrade(sys.argv[2])
    elif command == "current":
        current()
    elif command == "history":
        history()
    elif command == "ensure-latest":
        ensure_latest()
    elif command == "reset":
        confirm = input("WARNING: This will delete all data. Are you sure? (y/n) ")
        if confirm.lower() == 'y':
            reset_db()
        else:
            print("Reset cancelled.")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
