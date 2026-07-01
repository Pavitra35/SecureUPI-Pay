"""Explainable AI module for fraud detection."""
from typing import Dict, List, Any
import numpy as np


class FraudExplainer:
    """Provides explanations for fraud detection decisions."""
    
    def __init__(self):
        pass
    
    def explain(self, transaction: Dict[str, Any], ml_result: Dict[str, Any], 
                gnn_result: Dict[str, Any], rule_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for fraud detection.
        
        Args:
            transaction: Original transaction data
            ml_result: ML model prediction results
            gnn_result: GNN analysis results
            rule_result: Rule engine results
            
        Returns:
            Dictionary with explanation details
        """
        explanations = {
            'transaction_id': transaction.get('transaction_id', 'N/A'),
            'overall_fraud_score': self._calculate_overall_score(ml_result, gnn_result, rule_result),
            'is_fraud': self._determine_fraud(ml_result, gnn_result, rule_result),
            'explanations': {
                'ml_model': self._explain_ml(ml_result),
                'gnn_analysis': self._explain_gnn(gnn_result),
                'rule_engine': self._explain_rules(rule_result),
                'key_factors': self._identify_key_factors(transaction, ml_result, gnn_result, rule_result)
            },
            'recommendation': self._generate_recommendation(ml_result, gnn_result, rule_result)
        }
        
        return explanations
    
    def _calculate_overall_score(self, ml_result: Dict, gnn_result: Dict, rule_result: Dict) -> float:
        """Calculate overall fraud score from all components."""
        ml_score = ml_result.get('fraud_score', 0.5)
        gnn_score = gnn_result.get('fraud_score', 0.5)
        rule_score = rule_result.get('risk_score', 0.5)
        
        # Weighted combination
        overall = (0.5 * ml_score + 0.3 * gnn_score + 0.2 * rule_score)
        return float(overall)
    
    def _determine_fraud(self, ml_result: Dict, gnn_result: Dict, rule_result: Dict) -> bool:
        """Determine if transaction is fraudulent based on all components."""
        overall_score = self._calculate_overall_score(ml_result, gnn_result, rule_result)
        return overall_score >= 0.7
    
    def _explain_ml(self, ml_result: Dict) -> Dict[str, Any]:
        """Explain ML model predictions."""
        fraud_score = ml_result.get('fraud_score', 0.5)
        model_scores = ml_result.get('model_scores', {})
        
        explanation = {
            'fraud_score': fraud_score,
            'confidence': 'high' if abs(fraud_score - 0.5) > 0.3 else 'medium' if abs(fraud_score - 0.5) > 0.15 else 'low',
            'model_contributions': {}
        }
        
        if model_scores:
            explanation['model_contributions'] = {
                'XGBoost': {
                    'score': model_scores.get('xgb', 0.5),
                    'contribution': '40%'
                },
                'LightGBM': {
                    'score': model_scores.get('lgb', 0.5),
                    'contribution': '40%'
                },
                'Random Forest': {
                    'score': model_scores.get('rf', 0.5),
                    'contribution': '20%'
                }
            }
        
        if fraud_score >= 0.7:
            explanation['reason'] = f'ML models indicate high fraud probability ({fraud_score:.2%})'
        elif fraud_score >= 0.5:
            explanation['reason'] = f'ML models show moderate risk ({fraud_score:.2%})'
        else:
            explanation['reason'] = f'ML models indicate low fraud probability ({fraud_score:.2%})'
        
        return explanation
    
    def _explain_gnn(self, gnn_result: Dict) -> Dict[str, Any]:
        """Explain GNN analysis results."""
        network_risk = gnn_result.get('network_risk', 'low')
        connected_entities = gnn_result.get('connected_entities', 0)
        reasons = gnn_result.get('reasons', [])
        
        explanation = {
            'network_risk_level': network_risk,
            'connected_entities': connected_entities,
            'reasons': reasons,
            'interpretation': self._interpret_network_risk(network_risk, connected_entities)
        }
        
        return explanation
    
    def _explain_rules(self, rule_result: Dict) -> Dict[str, Any]:
        """Explain rule engine results."""
        violations = rule_result.get('violations', [])
        risk_score = rule_result.get('risk_score', 0.0)
        
        explanation = {
            'violation_count': len(violations),
            'risk_score': risk_score,
            'violations': [
                {
                    'rule': v.get('rule_name', 'Unknown'),
                    'message': v.get('message', ''),
                    'severity': 'high' if v.get('risk_weight', 0) > 0.2 else 'medium' if v.get('risk_weight', 0) > 0.1 else 'low'
                }
                for v in violations
            ],
            'summary': f'{len(violations)} rule violation(s) detected with risk score of {risk_score:.2%}'
        }
        
        return explanation
    
    def _identify_key_factors(self, transaction: Dict, ml_result: Dict, 
                             gnn_result: Dict, rule_result: Dict) -> List[str]:
        """Identify key factors contributing to fraud detection."""
        factors = []
        
        amount = float(transaction.get('amount', 0))
        if amount >= 100000:
            factors.append(f'High transaction amount (₹{amount:,.2f})')
        
        ml_score = ml_result.get('fraud_score', 0.5)
        if ml_score >= 0.7:
            factors.append('ML models indicate high fraud probability')
        
        network_risk = gnn_result.get('network_risk', 'low')
        if network_risk == 'high':
            factors.append('High network risk detected')
        
        violations = rule_result.get('violations', [])
        if len(violations) >= 2:
            factors.append(f'Multiple rule violations ({len(violations)})')
        
        connected_entities = gnn_result.get('connected_entities', 0)
        if connected_entities > 50:
            factors.append(f'Unusually high number of connected entities ({connected_entities})')
        
        return factors if factors else ['No significant fraud indicators detected']
    
    def _interpret_network_risk(self, risk_level: str, connected_entities: int) -> str:
        """Interpret network risk level."""
        if risk_level == 'high':
            return f'High network risk: Transaction involves entities with suspicious connection patterns ({connected_entities} connected entities). This may indicate money laundering or fraud rings.'
        elif risk_level == 'medium':
            return f'Medium network risk: Some unusual connection patterns detected ({connected_entities} connected entities). Monitor for further suspicious activity.'
        else:
            return f'Low network risk: Normal transaction patterns detected ({connected_entities} connected entities).'
    
    def _generate_recommendation(self, ml_result: Dict, gnn_result: Dict, rule_result: Dict) -> str:
        """Generate recommendation based on analysis."""
        overall_score = self._calculate_overall_score(ml_result, gnn_result, rule_result)
        
        if overall_score >= 0.8:
            return 'BLOCK: High confidence fraud detected. Recommend blocking transaction and flagging accounts for review.'
        elif overall_score >= 0.7:
            return 'FLAG: Suspicious transaction detected. Recommend manual review before processing.'
        elif overall_score >= 0.5:
            return 'MONITOR: Moderate risk detected. Process transaction but monitor account for further suspicious activity.'
        else:
            return 'APPROVE: Low fraud risk. Transaction appears legitimate and can be processed normally.'



