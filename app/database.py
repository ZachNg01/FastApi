import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

class DatabaseManager:
    """Secure database connection manager using Railway Shared Variables"""
    
    def __init__(self):
        self.database_url = self._prepare_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _prepare_database_url(self) -> str:
        """Prepare and validate database URL"""
        db_url = settings.database_url
        
        # Fix common connection string format issues
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        # Validate URL contains required components
        if "postgresql://" not in db_url:
            raise ValueError("Invalid DATABASE_URL format")
            
        return db_url
    
    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling"""
        pool_settings = {
            "pool_pre_ping": True,      # Verify connection before use
            "pool_recycle": 300,        # Recycle connections after 5 minutes
            "pool_size": 10,            # Maximum permanent connections
            "max_overflow": 20,         # Maximum temporary connections
            "echo": settings.debug      # Log SQL in development
        }
        
        return create_engine(self.database_url, **pool_settings)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_db(self):
        """Dependency for FastAPI routes"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Global database manager instance
db_manager = DatabaseManager()
get_db = db_manager.get_db

# Base for models
Base = declarative_base()