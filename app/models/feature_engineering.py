"""Feature engineering for transaction data."""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any


class FeatureEngineer:
    """Engineers features from raw transaction data."""
    
    def __init__(self):
        self.historical_stats = {}
    
    def extract_features(self, transaction: Dict[str, Any], historical_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Extract features from a transaction.
        
        Args:
            transaction: Raw transaction data
            historical_data: Historical transactions for context
            
        Returns:
            Dictionary of engineered features
        """
        features = {}
        
        # Basic features
        features['amount'] = float(transaction.get('amount', 0))
        features['hour'] = self._extract_hour(transaction.get('timestamp'))
        features['day_of_week'] = self._extract_day_of_week(transaction.get('timestamp'))
        features['is_weekend'] = 1 if features['day_of_week'] in [5, 6] else 0
        features['is_night'] = 1 if features['hour'] < 6 or features['hour'] > 22 else 0
        
        # Amount-based features
        features['amount_log'] = np.log1p(features['amount'])
        features['is_high_value'] = 1 if features['amount'] >= 10000 else 0
        features['is_very_high_value'] = 1 if features['amount'] >= 50000 else 0
        
        # Sender features
        sender_upi = transaction.get('sender_upi', '')
        features['sender_domain'] = self._extract_domain(sender_upi)
        features['sender_length'] = len(sender_upi)
        
        # Receiver features
        receiver_upi = transaction.get('receiver_upi', '')
        features['receiver_domain'] = self._extract_domain(receiver_upi)
        features['receiver_length'] = len(receiver_upi)
        
        # Transaction relationship
        features['same_domain'] = 1 if features['sender_domain'] == features['receiver_domain'] else 0
        
        # Historical features (if available)
        if historical_data is not None and len(historical_data) > 0:
            sender_history = historical_data[historical_data['sender_upi'] == sender_upi]
            receiver_history = historical_data[historical_data['receiver_upi'] == receiver_upi]
            
            # Sender statistics
            if len(sender_history) > 0:
                features['sender_txn_count'] = len(sender_history)
                features['sender_avg_amount'] = sender_history['amount'].mean()
                features['sender_max_amount'] = sender_history['amount'].max()
                features['sender_amount_std'] = sender_history['amount'].std()
                features['sender_unique_receivers'] = sender_history['receiver_upi'].nunique()
            else:
                features['sender_txn_count'] = 0
                features['sender_avg_amount'] = 0
                features['sender_max_amount'] = 0
                features['sender_amount_std'] = 0
                features['sender_unique_receivers'] = 0
            
            # Receiver statistics
            if len(receiver_history) > 0:
                features['receiver_txn_count'] = len(receiver_history)
                features['receiver_avg_amount'] = receiver_history['amount'].mean()
                features['receiver_unique_senders'] = receiver_history['sender_upi'].nunique()
            else:
                features['receiver_txn_count'] = 0
                features['receiver_avg_amount'] = 0
                features['receiver_unique_senders'] = 0
            
            # Amount deviation
            if features['sender_avg_amount'] > 0:
                features['amount_deviation'] = abs(features['amount'] - features['sender_avg_amount']) / features['sender_avg_amount']
            else:
                features['amount_deviation'] = 1.0
        else:
            # Default values when no history
            features.update({
                'sender_txn_count': 0,
                'sender_avg_amount': 0,
                'sender_max_amount': 0,
                'sender_amount_std': 0,
                'sender_unique_receivers': 0,
                'receiver_txn_count': 0,
                'receiver_avg_amount': 0,
                'receiver_unique_senders': 0,
                'amount_deviation': 1.0
            })
        
        # Device and location features
        features['device_id_present'] = 1 if transaction.get('device_id') else 0
        features['location_present'] = 1 if transaction.get('location') else 0
        
        return features
    
    def _extract_hour(self, timestamp: str) -> int:
        """Extract hour from timestamp."""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            return dt.hour
        except:
            return 12  # Default to noon
    
    def _extract_day_of_week(self, timestamp: str) -> int:
        """Extract day of week (0=Monday, 6=Sunday)."""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            return dt.weekday()
        except:
            return 0  # Default to Monday
    
    def _extract_domain(self, upi_id: str) -> str:
        """Extract domain from UPI ID."""
        if '@' in upi_id:
            return upi_id.split('@')[1]
        return 'unknown'



