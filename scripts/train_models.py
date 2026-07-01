"""Script to train ML models with sample data."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from app.models.feature_engineering import FeatureEngineer
from app.models.ensemble_model import EnsembleFraudDetector
from app.config import settings
import os

def generate_sample_data(n_samples=1000):
    """Generate sample training data."""
    np.random.seed(42)
    
    transactions = []
    for i in range(n_samples):
        # Generate legitimate transactions
        is_fraud = np.random.random() < 0.1  # 10% fraud rate
        
        if is_fraud:
            # Fraudulent transaction characteristics
            amount = np.random.choice([10000, 20000, 50000, 100000, 200000])
            hour = np.random.choice([2, 3, 4, 5])  # Unusual hours
            sender_txn_count = np.random.randint(50, 200)  # High activity
        else:
            # Legitimate transaction characteristics
            amount = np.random.uniform(10000, 50000)
            hour = np.random.randint(8, 20)  # Normal hours
            sender_txn_count = np.random.randint(1, 20)  # Normal activity
        
        transaction = {
            'transaction_id': f'TXN{i:06d}',
            'amount': amount,
            'sender_upi': f'sender{np.random.randint(1, 100)}@paytm',
            'receiver_upi': f'receiver{np.random.randint(1, 100)}@upi',
            'timestamp': f'2024-01-{np.random.randint(1, 28):02d}T{hour:02d}:00:00',
            'device_id': f'DEVICE{np.random.randint(1, 50)}',
            'location': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']),
            'is_fraud': 1 if is_fraud else 0
        }
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)


def train_models():
    """Train ensemble models."""
    print("Generating sample training data...")
    df = generate_sample_data(n_samples=2000)
    
    print(f"Generated {len(df)} transactions ({df['is_fraud'].sum()} fraudulent)")
    
    # Feature engineering
    print("Extracting features...")
    feature_engineer = FeatureEngineer()
    
    features_list = []
    for _, row in df.iterrows():
        txn_dict = row.to_dict()
        features = feature_engineer.extract_features(txn_dict)
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    y = df['is_fraud'].values
    
    print(f"Feature matrix shape: {features_df.shape}")
    print(f"Features: {list(features_df.columns)}")
    
    # Train ensemble model
    print("Training ensemble model...")
    ensemble_model = EnsembleFraudDetector()
    ensemble_model.train(features_df, pd.Series(y))
    
    # Save model
    model_path = os.path.join(settings.MODEL_PATH, "ensemble_model.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    ensemble_model.save(model_path)
    print(f"Model saved to {model_path}")
    
    # Evaluate
    predictions = []
    for _, row in df.iterrows():
        txn_dict = row.to_dict()
        features = feature_engineer.extract_features(txn_dict)
        _, is_fraud = ensemble_model.predict(features)
        predictions.append(is_fraud)
    
    accuracy = np.mean(predictions == y)
    print(f"\nTraining Accuracy: {accuracy:.2%}")
    print(f"Fraud Detection Rate: {np.mean(predictions[y == 1]) * 100:.2f}%")
    print(f"False Positive Rate: {np.mean(predictions[y == 0]) * 100:.2f}%")


if __name__ == "__main__":
    train_models()



