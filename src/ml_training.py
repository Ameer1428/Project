
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging
import json
from typing import Dict, Tuple, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkloadPredictor:
    def __init__(self, config_path: str = "../configs/ml_hyperparameters.json"):
        """Initialize the WorkloadPredictor with configurations."""
        self.load_config(config_path)
        self.setup_models()
        
    def load_config(self, config_path: str) -> None:
        """Load ML model configurations from JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise
            
    def setup_models(self) -> None:
        """Initialize ML models."""
        self.workload_model = RandomForestRegressor(
            n_estimators=self.config.get('n_estimators', 100),
            max_depth=self.config.get('max_depth', 10),
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare and preprocess training data."""
        try:
            # Load historical workload data
            df = pd.read_csv(data_path)
            
            # Feature engineering
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['month'] = pd.to_datetime(df['timestamp']).dt.month
            
            # Select features for training
            features = [
                'hour', 'day_of_week', 'month',
                'cpu_utilization', 'memory_usage',
                'network_in', 'network_out'
            ]
            
            X = df[features].values
            y = df['workload_demand'].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            return X_scaled, y
            
        except Exception as e:
            logger.error(f"Failed to prepare data: {str(e)}")
            raise
            
    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train the workload prediction model."""
        try:
            # Split data into training and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.workload_model.fit(X_train, y_train)
            
            # Evaluate model
            train_predictions = self.workload_model.predict(X_train)
            val_predictions = self.workload_model.predict(X_val)
            
            metrics = {
                'train_mse': mean_squared_error(y_train, train_predictions),
                'val_mse': mean_squared_error(y_val, val_predictions),
                'train_r2': r2_score(y_train, train_predictions),
                'val_r2': r2_score(y_val, val_predictions)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            raise
            
    def save_models(self, model_dir: str = "../models") -> None:
        """Save trained models to disk."""
        try:
            # Save the Random Forest model
            joblib.dump(
                self.workload_model,
                f"{model_dir}/workload_prediction.pkl"
            )
            # Save the scaler
            joblib.dump(
                self.scaler,
                f"{model_dir}/workload_scaler.pkl"
            )
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {str(e)}")
            raise
            
    def load_models(self, model_dir: str = "../models") -> None:
        """Load trained models from disk."""
        try:
            self.workload_model = joblib.load(
                f"{model_dir}/workload_prediction.pkl"
            )
            self.scaler = joblib.load(
                f"{model_dir}/workload_scaler.pkl"
            )
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            raise
            
    def predict_workload(self, features: Dict[str, Any]) -> float:
        """Predict workload demand for given features."""
        try:
            # Prepare features
            feature_vector = np.array([[
                features.get('hour', datetime.now().hour),
                features.get('day_of_week', datetime.now().weekday()),
                features.get('month', datetime.now().month),
                features.get('cpu_utilization', 0),
                features.get('memory_usage', 0),
                features.get('network_in', 0),
                features.get('network_out', 0)
            ]])
            
            # Scale features
            scaled_features = self.scaler.transform(feature_vector)
            
            # Make prediction
            prediction = self.workload_model.predict(scaled_features)[0]
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict workload: {str(e)}")
            raise
            
def train_and_save_model():
    """Utility function to train and save the model."""
    try:
        predictor = WorkloadPredictor()
        
        # Prepare data
        X, y = predictor.prepare_data("../data/workload_data.csv")
        
        # Train model
        metrics = predictor.train_model(X, y)
        logger.info(f"Training metrics: {metrics}")
        
        # Save models
        predictor.save_models()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to train and save model: {str(e)}")
        raise
        
if __name__ == "__main__":
    metrics = train_and_save_model()
    print(f"Model training completed with metrics: {metrics}")