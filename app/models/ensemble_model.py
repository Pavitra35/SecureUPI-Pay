"""Ensemble model combining multiple ML algorithms."""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
from app.config import settings


class EnsembleFraudDetector:
    """Ensemble model combining XGBoost, LightGBM, and Random Forest."""
    
    def __init__(self):
        self.xgb_model = None
        self.lgb_model = None
        self.rf_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Train ensemble models.
        
        Args:
            X: Feature matrix
            y: Target labels (0=legitimate, 1=fraud)
        """
        self.feature_names = list(X.columns)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=self.feature_names)
        
        # Train XGBoost
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        self.xgb_model.fit(X_scaled, y)
        
        # Train LightGBM
        self.lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        self.lgb_model.fit(X_scaled, y)
        
        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_scaled, y)
        
        self.is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Tuple[float, bool]:
        """
        Predict fraud probability using ensemble.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Tuple of (fraud_score, is_fraud)
        """
        if not self.is_trained:
            # Return default prediction if model not trained
            return 0.5, False
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        # Reorder columns to match training
        feature_df = feature_df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(feature_df)
        X_scaled = pd.DataFrame(X_scaled, columns=self.feature_names)
        
        # Get predictions from each model
        xgb_proba = self.xgb_model.predict_proba(X_scaled)[0][1]
        lgb_proba = self.lgb_model.predict_proba(X_scaled)[0][1]
        rf_proba = self.rf_model.predict_proba(X_scaled)[0][1]
        
        # Weighted ensemble (can be adjusted based on performance)
        weights = {'xgb': 0.4, 'lgb': 0.4, 'rf': 0.2}
        fraud_score = (
            weights['xgb'] * xgb_proba +
            weights['lgb'] * lgb_proba +
            weights['rf'] * rf_proba
        )
        
        is_fraud = fraud_score >= settings.FRAUD_THRESHOLD
        
        return float(fraud_score), bool(is_fraud)
    
    def predict_with_explanations(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict with individual model scores for explainability.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Dictionary with predictions and explanations
        """
        if not self.is_trained:
            return {
                'fraud_score': 0.5,
                'is_fraud': False,
                'model_scores': {
                    'xgb': 0.5,
                    'lgb': 0.5,
                    'rf': 0.5
                }
            }
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        # Reorder columns
        feature_df = feature_df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(feature_df)
        X_scaled = pd.DataFrame(X_scaled, columns=self.feature_names)
        
        # Get individual predictions
        xgb_proba = float(self.xgb_model.predict_proba(X_scaled)[0][1])
        lgb_proba = float(self.lgb_model.predict_proba(X_scaled)[0][1])
        rf_proba = float(self.rf_model.predict_proba(X_scaled)[0][1])
        
        # Ensemble score
        weights = {'xgb': 0.4, 'lgb': 0.4, 'rf': 0.2}
        fraud_score = (
            weights['xgb'] * xgb_proba +
            weights['lgb'] * lgb_proba +
            weights['rf'] * rf_proba
        )
        
        return {
            'fraud_score': float(fraud_score),
            'is_fraud': fraud_score >= settings.FRAUD_THRESHOLD,
            'model_scores': {
                'xgb': xgb_proba,
                'lgb': lgb_proba,
                'rf': rf_proba
            }
        }
    
    def save(self, filepath: str):
        """Save the ensemble model."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'xgb_model': self.xgb_model,
                'lgb_model': self.lgb_model,
                'rf_model': self.rf_model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }, f)
    
    def load(self, filepath: str):
        """Load the ensemble model."""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.xgb_model = data['xgb_model']
                self.lgb_model = data['lgb_model']
                self.rf_model = data['rf_model']
                self.scaler = data['scaler']
                self.feature_names = data['feature_names']
                self.is_trained = data['is_trained']
        else:
            # Initialize with default models if file doesn't exist
            self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize models with default parameters (for demo purposes)."""
        # Create dummy training data to initialize models
        n_samples = 100
        n_features = 20
        
        X_dummy = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        y_dummy = np.random.randint(0, 2, n_samples)
        
        self.train(X_dummy, pd.Series(y_dummy))
        self.is_trained = True



