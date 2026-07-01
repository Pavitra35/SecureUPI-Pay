"""Database utilities for storing transactions."""
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings
import os

Base = declarative_base()


class Transaction(Base):
    """Transaction model."""
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True)
    amount = Column(Float)
    sender_upi = Column(String)
    receiver_upi = Column(String)
    timestamp = Column(DateTime)
    device_id = Column(String, nullable=True)
    location = Column(String, nullable=True)
    fraud_score = Column(Float)
    is_fraud = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Database manager."""
    
    def __init__(self):
        os.makedirs(os.path.dirname(settings.DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)
        self.engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def save_transaction(self, transaction_data: dict):
        """Save transaction to database."""
        session = self.get_session()
        try:
            txn = Transaction(**transaction_data)
            session.add(txn)
            session.commit()
            return txn
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_transaction(self, transaction_id: str):
        """Get transaction by ID."""
        session = self.get_session()
        try:
            return session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        finally:
            session.close()
    
    def get_recent_transactions(self, limit: int = 1000):
        """Get recent transactions."""
        session = self.get_session()
        try:
            return session.query(Transaction).order_by(Transaction.timestamp.desc()).limit(limit).all()
        finally:
            session.close()


db = Database()



