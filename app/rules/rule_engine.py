"""Rule-based fraud detection engine."""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.config import settings


class RuleEngine:
    """Rule-based fraud detection engine."""
    
    def __init__(self):
        self.rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize fraud detection rules."""
        self.rules = [
            self._check_minimum_amount,
            self._check_amount_threshold,
            self._check_rapid_transactions,
            self._check_unusual_hours,
            self._check_same_sender_receiver,
            self._check_missing_device_info,
            self._check_amount_rounding,
        ]
    
    def evaluate(self, transaction: Dict[str, Any], historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate transaction against all rules.
        
        Args:
            transaction: Transaction to evaluate
            historical_data: Historical transactions for context
            
        Returns:
            Dictionary with rule evaluation results
        """
        violations = []
        risk_score = 0.0
        
        for rule in self.rules:
            result = rule(transaction, historical_data or [])
            if result['violated']:
                violations.append(result)
                risk_score += result['risk_weight']
        
        # Normalize risk score to 0-1
        risk_score = min(1.0, risk_score / len(self.rules))
        
        return {
            'violations': violations,
            'risk_score': risk_score,
            'is_fraud': len(violations) >= 2 or risk_score >= 0.7,
            'violation_count': len(violations)
        }
    
    def _check_minimum_amount(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if transaction meets minimum amount threshold."""
        amount = float(transaction.get('amount', 0))
        violated = amount < settings.MIN_TRANSACTION_AMOUNT
        
        return {
            'rule_name': 'Minimum Amount Check',
            'violated': violated,
            'risk_weight': 0.1 if violated else 0.0,
            'message': f'Transaction amount ({amount}) below minimum threshold ({settings.MIN_TRANSACTION_AMOUNT})' if violated else 'Amount check passed'
        }
    
    def _check_amount_threshold(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for unusually high transaction amounts."""
        amount = float(transaction.get('amount', 0))
        high_threshold = 100000  # ₹1 lakh
        very_high_threshold = 500000  # ₹5 lakhs
        
        violated = amount > very_high_threshold
        risk_weight = 0.3 if amount > very_high_threshold else (0.15 if amount > high_threshold else 0.0)
        
        return {
            'rule_name': 'High Amount Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': f'Unusually high transaction amount: ₹{amount:,.2f}' if violated else 'Amount within normal range'
        }
    
    def _check_rapid_transactions(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for rapid successive transactions from same sender."""
        sender = transaction.get('sender_upi', '')
        timestamp = transaction.get('timestamp', '')
        
        if not sender or not timestamp:
            return {
                'rule_name': 'Rapid Transactions Check',
                'violated': False,
                'risk_weight': 0.0,
                'message': 'Insufficient data for rapid transaction check'
            }
        
        try:
            current_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return {
                'rule_name': 'Rapid Transactions Check',
                'violated': False,
                'risk_weight': 0.0,
                'message': 'Invalid timestamp format'
            }
        
        # Check transactions in last 5 minutes
        recent_txns = [
            txn for txn in historical
            if txn.get('sender_upi') == sender
            and self._is_recent(txn.get('timestamp', ''), current_time, minutes=5)
        ]
        
        violated = len(recent_txns) >= 5
        risk_weight = 0.4 if len(recent_txns) >= 10 else (0.2 if violated else 0.0)
        
        return {
            'rule_name': 'Rapid Transactions Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': f'{len(recent_txns)} transactions from same sender in last 5 minutes' if violated else 'No rapid transaction pattern detected'
        }
    
    def _check_unusual_hours(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for transactions at unusual hours."""
        timestamp = transaction.get('timestamp', '')
        
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            hour = dt.hour
        except:
            return {
                'rule_name': 'Unusual Hours Check',
                'violated': False,
                'risk_weight': 0.0,
                'message': 'Invalid timestamp'
            }
        
        # Flag transactions between 2 AM and 5 AM
        violated = 2 <= hour <= 5
        risk_weight = 0.15 if violated else 0.0
        
        return {
            'rule_name': 'Unusual Hours Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': f'Transaction at unusual hour: {hour}:00' if violated else 'Transaction time is normal'
        }
    
    def _check_same_sender_receiver(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if sender and receiver are the same."""
        sender = transaction.get('sender_upi', '')
        receiver = transaction.get('receiver_upi', '')
        
        violated = sender == receiver and sender != ''
        risk_weight = 0.3 if violated else 0.0
        
        return {
            'rule_name': 'Same Sender-Receiver Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': 'Sender and receiver are the same' if violated else 'Sender and receiver are different'
        }
    
    def _check_missing_device_info(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for missing device or location information."""
        device_id = transaction.get('device_id', '')
        location = transaction.get('location', '')
        
        violated = not device_id or not location
        risk_weight = 0.1 if violated else 0.0
        
        return {
            'rule_name': 'Missing Device Info Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': 'Missing device ID or location information' if violated else 'Device and location info present'
        }
    
    def _check_amount_rounding(self, transaction: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for suspicious round number amounts."""
        amount = float(transaction.get('amount', 0))
        
        # Flag exact round numbers (e.g., 10000, 50000, 100000)
        round_numbers = [10000, 20000, 50000, 100000, 200000, 500000]
        violated = amount in round_numbers
        
        risk_weight = 0.1 if violated else 0.0
        
        return {
            'rule_name': 'Amount Rounding Check',
            'violated': violated,
            'risk_weight': risk_weight,
            'message': f'Suspicious round number amount: ₹{amount:,.2f}' if violated else 'Amount is not a round number'
        }
    
    def _is_recent(self, timestamp: str, current_time: datetime, minutes: int = 5) -> bool:
        """Check if timestamp is within specified minutes of current time."""
        try:
            if isinstance(timestamp, str):
                txn_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                txn_time = timestamp
            
            time_diff = abs((current_time - txn_time).total_seconds() / 60)
            return time_diff <= minutes
        except:
            return False



