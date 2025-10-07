import os
from typing import Optional

class Settings:
    """Application settings loaded from Railway Shared Variables"""
    
    def __init__(self):
        # Database Configuration
        self.database_url: str = self._get_required_variable("DATABASE_URL")
        
        # Application Settings
        self.environment: str = self._get_variable("RAILWAY_ENVIRONMENT", "production")
        self.app_name: str = self._get_variable("APP_NAME", "Cooking School Survey")
        self.secret_key: str = self._get_variable("SECRET_KEY", "fallback-secret-key-change-in-production")
        self.debug: bool = self._get_variable("DEBUG", "False").lower() == "true"
        
        # Security Settings
        self.allowed_hosts: list = self._get_variable("ALLOWED_HOSTS", "your-app-name.up.railway.app").split(",")
        self.cors_origins: list = self._get_variable("CORS_ORIGINS", "").split(",")
        
    def _get_required_variable(self, var_name: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Required environment variable {var_name} is not set")
        return value
    
    def _get_variable(self, var_name: str, default: Optional[str] = None) -> str:
        """Get environment variable with fallback"""
        return os.getenv(var_name, default)
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

# Global settings instance
settings = Settings()