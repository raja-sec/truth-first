import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Import your Base so SQLAlchemy knows what tables to build
from database.models import Base

# Force load the .env file to grab the Neon URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def build_tables():
    print("🔌 Connecting to Neon Database...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        print("🏗️ Building tables from models...")
        # This forcefully creates all tables that don't exist yet
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ All tables created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(build_tables())