"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TransactionRequest(BaseModel):
    """Transaction analysis request."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    sender_upi: str = Field(..., description="Sender UPI ID")
    receiver_upi: str = Field(..., description="Receiver UPI ID")
    timestamp: str = Field(..., description="Transaction timestamp (ISO format)")
    device_id: Optional[str] = Field(None, description="Device identifier")
    location: Optional[str] = Field(None, description="Transaction location")


class FraudDetectionResponse(BaseModel):
    """Fraud detection response."""
    transaction_id: str
    fraud_score: float = Field(..., ge=0, le=1, description="Fraud probability score")
    is_fraud: bool
    reasons: List[str]
    ml_score: float
    gnn_score: float
    rule_score: float
    recommendation: str


class ExplanationResponse(BaseModel):
    """Explainability response."""
    transaction_id: str
    overall_fraud_score: float
    is_fraud: bool
    explanations: Dict[str, Any]
    recommendation: str


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    total_transactions: int
    fraud_transactions: int
    fraud_rate: float
    total_amount: float
    fraud_amount: float
    recent_frauds: List[Dict[str, Any]]


class NetworkNode(BaseModel):
    """Network graph node."""
    id: str
    label: str
    group: str
    value: int


class NetworkEdge(BaseModel):
    """Network graph edge."""
    source: str
    target: str
    value: float


class NetworkGraphResponse(BaseModel):
    """Network graph response."""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]



