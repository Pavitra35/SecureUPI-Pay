"""API routes for fraud detection."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.api.schemas import (
    TransactionRequest, FraudDetectionResponse, ExplanationResponse,
    DashboardStatsResponse, NetworkGraphResponse
)
from app.models.feature_engineering import FeatureEngineer
from app.models.ensemble_model import EnsembleFraudDetector
from app.gnn.fraud_graph import GNNFraudDetector
from app.rules.rule_engine import RuleEngine
from app.explainability.explainer import FraudExplainer
from app.utils.database import db
import pandas as pd
from datetime import datetime

router = APIRouter()

# Initialize components
feature_engineer = FeatureEngineer()
ensemble_model = EnsembleFraudDetector()
gnn_detector = GNNFraudDetector()
rule_engine = RuleEngine()
explainer = FraudExplainer()

# Initialize models (will use default if not trained)
ensemble_model._initialize_default_models()


@router.post("/transaction/analyze", response_model=FraudDetectionResponse)
async def analyze_transaction(transaction: TransactionRequest):
    """
    Analyze a transaction for fraud detection.
    
    This endpoint uses ensemble ML models, GNN analysis, and rule engine
    to detect fraudulent transactions.
    """
    try:
        # Convert to dict
        txn_dict = transaction.dict()
        
        # Get historical transactions
        historical_txns = db.get_recent_transactions(limit=1000)
        historical_data = pd.DataFrame([
            {
                'sender_upi': t.sender_upi,
                'receiver_upi': t.receiver_upi,
                'amount': t.amount,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            for t in historical_txns
        ])
        
        # Extract features
        features = feature_engineer.extract_features(txn_dict, historical_data if len(historical_data) > 0 else None)
        
        # ML Model Prediction
        ml_result = ensemble_model.predict_with_explanations(features)
        
        # GNN Analysis
        historical_list = [
            {
                'sender_upi': t.sender_upi,
                'receiver_upi': t.receiver_upi,
                'amount': t.amount,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            for t in historical_txns
        ]
        gnn_result = gnn_detector.detect_fraud(txn_dict, historical_list)
        
        # Rule Engine
        rule_result = rule_engine.evaluate(txn_dict, historical_list)
        
        # Combine results
        overall_fraud_score = (
            0.5 * ml_result['fraud_score'] +
            0.3 * gnn_result['fraud_score'] +
            0.2 * rule_result['risk_score']
        )
        is_fraud = overall_fraud_score >= 0.7
        
        # Collect reasons
        reasons = []
        if ml_result['fraud_score'] >= 0.7:
            reasons.append(f"ML models detected high fraud probability ({ml_result['fraud_score']:.2%})")
        if gnn_result['is_fraud']:
            reasons.extend(gnn_result.get('reasons', []))
        if rule_result['is_fraud']:
            reasons.extend([v.get('message', '') for v in rule_result.get('violations', [])])
        
        if not reasons:
            reasons = ["No significant fraud indicators detected"]
        
        # Save transaction
        try:
            db.save_transaction({
                'transaction_id': txn_dict['transaction_id'],
                'amount': txn_dict['amount'],
                'sender_upi': txn_dict['sender_upi'],
                'receiver_upi': txn_dict['receiver_upi'],
                'timestamp': datetime.fromisoformat(txn_dict['timestamp'].replace('Z', '+00:00')),
                'device_id': txn_dict.get('device_id'),
                'location': txn_dict.get('location'),
                'fraud_score': overall_fraud_score,
                'is_fraud': is_fraud
            })
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error saving transaction: {e}")
        
        # Generate recommendation
        recommendation = "BLOCK" if overall_fraud_score >= 0.8 else \
                        "FLAG" if overall_fraud_score >= 0.7 else \
                        "MONITOR" if overall_fraud_score >= 0.5 else "APPROVE"
        
        return FraudDetectionResponse(
            transaction_id=txn_dict['transaction_id'],
            fraud_score=overall_fraud_score,
            is_fraud=is_fraud,
            reasons=reasons[:5],  # Limit to top 5 reasons
            ml_score=ml_result['fraud_score'],
            gnn_score=gnn_result['fraud_score'],
            rule_score=rule_result['risk_score'],
            recommendation=recommendation
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transaction: {str(e)}")


@router.get("/transaction/{transaction_id}", response_model=ExplanationResponse)
async def get_transaction_explanation(transaction_id: str):
    """Get detailed explanation for a transaction."""
    try:
        txn = db.get_transaction(transaction_id)
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Reconstruct transaction dict
        txn_dict = {
            'transaction_id': txn.transaction_id,
            'amount': txn.amount,
            'sender_upi': txn.sender_upi,
            'receiver_upi': txn.receiver_upi,
            'timestamp': txn.timestamp.isoformat() if txn.timestamp else None,
            'device_id': txn.device_id,
            'location': txn.location
        }
        
        # Get historical data
        historical_txns = db.get_recent_transactions(limit=1000)
        historical_data = pd.DataFrame([
            {
                'sender_upi': t.sender_upi,
                'receiver_upi': t.receiver_upi,
                'amount': t.amount,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            for t in historical_txns
        ])
        
        # Extract features
        features = feature_engineer.extract_features(txn_dict, historical_data if len(historical_data) > 0 else None)
        
        # Get predictions
        ml_result = ensemble_model.predict_with_explanations(features)
        historical_list = [
            {
                'sender_upi': t.sender_upi,
                'receiver_upi': t.receiver_upi,
                'amount': t.amount,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            for t in historical_txns
        ]
        gnn_result = gnn_detector.detect_fraud(txn_dict, historical_list)
        rule_result = rule_engine.evaluate(txn_dict, historical_list)
        
        # Generate explanation
        explanation = explainer.explain(txn_dict, ml_result, gnn_result, rule_result)
        
        return ExplanationResponse(**explanation)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting explanation: {str(e)}")


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        all_txns = db.get_recent_transactions(limit=10000)
        
        total_transactions = len(all_txns)
        fraud_transactions = sum(1 for t in all_txns if t.is_fraud)
        fraud_rate = (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        total_amount = sum(t.amount for t in all_txns)
        fraud_amount = sum(t.amount for t in all_txns if t.is_fraud)
        
        recent_frauds = [
            {
                'transaction_id': t.transaction_id,
                'amount': t.amount,
                'sender_upi': t.sender_upi,
                'receiver_upi': t.receiver_upi,
                'fraud_score': t.fraud_score,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            for t in sorted(all_txns, key=lambda x: x.timestamp or datetime.min, reverse=True)[:10]
            if t.is_fraud
        ]
        
        return DashboardStatsResponse(
            total_transactions=total_transactions,
            fraud_transactions=fraud_transactions,
            fraud_rate=round(fraud_rate, 2),
            total_amount=round(total_amount, 2),
            fraud_amount=round(fraud_amount, 2),
            recent_frauds=recent_frauds
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/graph/network", response_model=NetworkGraphResponse)
async def get_network_graph():
    """Get fraud network graph data."""
    try:
        all_txns = db.get_recent_transactions(limit=500)
        
        nodes = {}
        edges = []
        
        for txn in all_txns:
            if txn.is_fraud:
                # Add nodes
                if txn.sender_upi not in nodes:
                    nodes[txn.sender_upi] = {'count': 0, 'fraud_count': 0}
                if txn.receiver_upi not in nodes:
                    nodes[txn.receiver_upi] = {'count': 0, 'fraud_count': 0}
                
                nodes[txn.sender_upi]['count'] += 1
                nodes[txn.sender_upi]['fraud_count'] += 1
                nodes[txn.receiver_upi]['count'] += 1
                nodes[txn.receiver_upi]['fraud_count'] += 1
                
                # Add edge
                edges.append({
                    'source': txn.sender_upi,
                    'target': txn.receiver_upi,
                    'value': txn.amount
                })
        
        # Convert nodes to list
        node_list = [
            {
                'id': upi_id,
                'label': upi_id[:20] + '...' if len(upi_id) > 20 else upi_id,
                'group': 'high_risk' if data['fraud_count'] > 5 else 'medium_risk' if data['fraud_count'] > 2 else 'low_risk',
                'value': data['count']
            }
            for upi_id, data in nodes.items()
        ]
        
        return NetworkGraphResponse(
            nodes=node_list,
            edges=edges[:100]  # Limit edges for performance
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting network graph: {str(e)}")



