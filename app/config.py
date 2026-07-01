"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "UPI Fraud Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Model Configuration
    FRAUD_THRESHOLD: float = 0.7
    MIN_TRANSACTION_AMOUNT: float = 10000.0
    MODEL_PATH: str = "./data/models/"
    
    # GNN Configuration
    GNN_ENABLED: bool = True
    GNN_MODEL_PATH: str = "./data/models/gnn_model.pth"
    MAX_GRAPH_NODES: int = 10000
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/fraud_detection.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()



