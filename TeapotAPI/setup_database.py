"""
Database setup script for TeapotAPI
"""
import asyncio
import os
from app.database import init_db, engine
from app.config import settings


async def setup_database():
    """Setup database tables"""
    print("Setting up database...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        await init_db()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise


async def main():
    """Main setup function"""
    print("🚀 TeapotAPI Database Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please copy env.example to .env and configure it.")
        return
    
    await setup_database()
    
    print("\n📋 Next steps:")
    print("1. Run: alembic revision --autogenerate -m 'Initial migration'")
    print("2. Run: alembic upgrade head")
    print("3. Start the server: python run.py")


if __name__ == "__main__":
    asyncio.run(main())
