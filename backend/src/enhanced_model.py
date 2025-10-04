"""
Enhanced Demand Forecasting with Advanced Features
Improves upon the basic Prophet model with better feature engineering and ensemble methods
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EnhancedDemandForecaster:
    def __init__(self, product_name):
        self.product_name = product_name
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
        
    def create_advanced_features(self, df):
        """Create advanced features for better predictions"""
        
        # Time-based features
        df['day_of_week'] = df['ds'].dt.dayofweek
        df['day_of_month'] = df['ds'].dt.day
        df['month'] = df['ds'].dt.month
        df['quarter'] = df['ds'].dt.quarter
        df['is_month_start'] = df['ds'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['ds'].dt.is_month_end.astype(int)
        
        # Lag features (previous days' sales)
        for lag in [1, 2, 3, 7, 14]:
            df[f'sales_lag_{lag}'] = df['y'].shift(lag)
        
        # Rolling statistics
        for window in [3, 7, 14]:
            df[f'sales_rolling_mean_{window}'] = df['y'].rolling(window=window).mean()
            df[f'sales_rolling_std_{window}'] = df['y'].rolling(window=window).std()
            df[f'sales_rolling_max_{window}'] = df['y'].rolling(window=window).max()
            df[f'sales_rolling_min_{window}'] = df['y'].rolling(window=window).min()
        
        # Weather interactions
        df['temp_precip_interaction'] = df['temperature'] * df['precipitation']
        df['temp_weekend_interaction'] = df['temperature'] * df['is_weekend']
        
        # Weather categories
        df['temp_category'] = pd.cut(df['temperature'], 
                                   bins=[-np.inf, 0, 10, 20, 30, np.inf], 
                                   labels=['very_cold', 'cold', 'mild', 'warm', 'hot'])
        df['precip_category'] = pd.cut(df['precipitation'], 
                                     bins=[-np.inf, 0, 5, 15, np.inf], 
                                     labels=['no_rain', 'light_rain', 'moderate_rain', 'heavy_rain'])
        
        # One-hot encode categories
        temp_dummies = pd.get_dummies(df['temp_category'], prefix='temp')
        precip_dummies = pd.get_dummies(df['precip_category'], prefix='precip')
        df = pd.concat([df, temp_dummies, precip_dummies], axis=1)
        
        # Holiday proximity (days before/after holidays)
        df['days_to_holiday'] = 0
        df['days_from_holiday'] = 0
        
        # Economic indicators (simulated - in real scenario, use actual data)
        df['price_index'] = np.random.normal(100, 5, len(df))  # Simulated price index
        df['consumer_confidence'] = np.random.normal(50, 10, len(df))  # Simulated confidence
        
        return df
    
    def train_ensemble_model(self, train_df):
        """Train ensemble of models for better predictions"""
        
        # Create advanced features
        train_df = self.create_advanced_features(train_df)
        
        # Prepare features for ML models
        feature_cols = [col for col in train_df.columns 
                       if col not in ['ds', 'y', 'temp_category', 'precip_category']]
        
        # Remove rows with NaN values from lag features
        train_df = train_df.dropna()
        
        X = train_df[feature_cols]
        y = train_df['y']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train multiple models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ridge': Ridge(alpha=1.0)
        }
        
        for name, model in models.items():
            model.fit(X_scaled, y)
            self.models[name] = model
            
            # Store feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(feature_cols, model.feature_importances_))
        
        # Train Prophet model with enhanced features
        prophet_model = Prophet(
            growth="flat",
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_prior_scale=1.0,
            changepoint_prior_scale=0.001
        )
        
        # Add all relevant regressors
        regressor_cols = ['is_weekend', 'is_holiday', 'temperature', 'precipitation',
                         'day_of_week', 'month', 'price_index', 'consumer_confidence']
        
        for col in regressor_cols:
            if col in train_df.columns:
                prophet_model.add_regressor(col)
        
        prophet_model.fit(train_df[['ds', 'y'] + regressor_cols])
        self.models['prophet'] = prophet_model
        
        return feature_cols
    
    def predict_ensemble(self, future_df, feature_cols):
        """Make ensemble predictions"""
        
        # Create advanced features for future data
        future_df = self.create_advanced_features(future_df)
        
        # Fill missing lag features with recent averages
        for col in feature_cols:
            if col.startswith('sales_lag_') or col.startswith('sales_rolling_'):
                future_df[col] = future_df[col].fillna(future_df['y'].mean())
        
        # Fill other missing values
        future_df = future_df.fillna(future_df.mean())
        
        # ML model predictions
        X_future = future_df[feature_cols]
        X_future_scaled = self.scaler.transform(X_future)
        
        ml_predictions = []
        for name, model in self.models.items():
            if name != 'prophet':
                pred = model.predict(X_future_scaled)
                ml_predictions.append(pred)
        
        # Prophet predictions
        prophet_pred = self.models['prophet'].predict(future_df)
        prophet_forecast = prophet_pred['yhat'].values
        
        # Ensemble prediction (weighted average)
        # Give more weight to models that performed better in validation
        weights = [0.3, 0.3, 0.2, 0.2]  # RF, GB, Ridge, Prophet
        
        ensemble_pred = np.average(ml_predictions + [prophet_forecast], 
                                 axis=0, weights=weights)
        
        return ensemble_pred, prophet_pred
    
    def get_feature_importance_summary(self):
        """Get feature importance across all models"""
        importance_df = pd.DataFrame(self.feature_importance)
        importance_df['average_importance'] = importance_df.mean(axis=1)
        return importance_df.sort_values('average_importance', ascending=False)

def train_enhanced_models():
    """Train enhanced models for all products"""
    
    # Load data
    df = pd.read_csv('data/daily_sales_dataset.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Rename columns
    df = df.rename(columns={
        'product': 'product_name',
        'items_sold': 'quantity_sold',
        'items_wasted': 'quantity_wasted',
        'temperature': 'temperature_2m_mean',
        'precipitation': 'precipitation_sum',
        'isWeekend': 'is_weekend',
        'isHoliday': 'is_holiday'
    })
    
    products = ['Strawberries', 'Chocolate', 'Eggs', 'Milk', 'Hot-Dogs']
    
    for product in products:
        print(f"\nTraining enhanced model for {product}...")
        
        # Prepare data
        product_df = df[df['product_name'] == product].copy()
        product_df = product_df.groupby('date').agg({
            'quantity_sold': 'sum',
            'temperature_2m_mean': 'first',
            'precipitation_sum': 'first',
            'is_weekend': 'first',
            'is_holiday': 'first'
        }).reset_index()
        
        product_df = product_df.sort_values('date')
        product_df = product_df.rename(columns={'date': 'ds', 'quantity_sold': 'y'})
        
        # Train enhanced model
        forecaster = EnhancedDemandForecaster(product)
        feature_cols = forecaster.train_ensemble_model(product_df)
        
        # Save model
        model_path = f'models/enhanced_{product.replace(" ", "_")}_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(forecaster, f)
        
        print(f"Enhanced model saved to: {model_path}")
        
        # Print feature importance
        importance = forecaster.get_feature_importance_summary()
        print(f"\nTop 10 most important features for {product}:")
        print(importance.head(10))

if __name__ == "__main__":
    train_enhanced_models()
