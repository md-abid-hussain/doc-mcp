#!/usr/bin/env python3
"""Database setup and maintenance script."""

import asyncio
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.config import settings
from src.database.mongodb import mongodb_client
from src.database.vector_store import create_search_indexes


async def setup_database():
    """Set up database collections and indexes."""
    try:
        print("🔧 Setting up database...")

        # Test connection
        if not mongodb_client.test_connection():
            print("❌ Failed to connect to MongoDB")
            return False

        print("✅ Connected to MongoDB")

        # Get collections
        docs_collection = mongodb_client.get_collection(settings.collection_name)
        repos_collection = mongodb_client.get_collection(settings.repos_collection_name)

        print(f"📊 Documents collection: {settings.collection_name}")
        print(f"📋 Repositories collection: {settings.repos_collection_name}")

        # Create search indexes
        vs_model, fts_model = create_search_indexes()

        try:
            docs_collection.create_search_indexes(models=[vs_model, fts_model])
            print("✅ Search indexes created")
        except Exception as e:
            print(f"⚠️ Search indexes might already exist: {e}")

        print("🎉 Database setup complete!")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    finally:
        mongodb_client.close()


async def check_database_status():
    """Check database status and collections."""
    try:
        print("🔍 Checking database status...")

        if not mongodb_client.test_connection():
            print("❌ Cannot connect to MongoDB")
            return

        print("✅ MongoDB connection OK")

        # Check collections
        db = mongodb_client.database
        collections = await db.list_collection_names()

        print(f"📊 Available collections: {collections}")

        docs_collection = mongodb_client.get_collection(settings.collection_name)
        repos_collection = mongodb_client.get_collection(settings.repos_collection_name)

        doc_count = docs_collection.count_documents({})
        repo_count = repos_collection.count_documents({})

        print(f"📄 Documents: {doc_count}")
        print(f"📋 Repositories: {repo_count}")

    except Exception as e:
        print(f"❌ Status check failed: {e}")
    finally:
        mongodb_client.close()


async def clear_database():
    """Clear all data from database."""
    try:
        response = input("⚠️ This will delete ALL data. Type 'YES' to confirm: ")
        if response != "YES":
            print("❌ Operation cancelled")
            return

        print("🗑️ Clearing database...")

        docs_collection = mongodb_client.get_collection(settings.collection_name)
        repos_collection = mongodb_client.get_collection(settings.repos_collection_name)

        docs_result = docs_collection.delete_many({})
        repos_result = repos_collection.delete_many({})

        print(f"✅ Deleted {docs_result.deleted_count} documents")
        print(f"✅ Deleted {repos_result.deleted_count} repositories")

    except Exception as e:
        print(f"❌ Clear operation failed: {e}")
    finally:
        mongodb_client.close()


async def main():
    """Main script entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_setup.py [setup|status|clear]")
        return

    command = sys.argv[1]

    if command == "setup":
        await setup_database()
    elif command == "status":
        await check_database_status()
    elif command == "clear":
        await clear_database()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, status, clear")


if __name__ == "__main__":
    asyncio.run(main())
