"""
Shelf Oracle - Prophet Demand Forecasting
Trains models for grocery store demand prediction using weather and sales data
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
import pickle
from datetime import datetime, timedelta
import os

# ============================================================================
# CONFIGURATION
# ============================================================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEATHER_FILE = os.path.join(BASE_DIR, 'data', 'daily_weather_data.csv')
SALES_FILE = os.path.join(BASE_DIR, 'data', 'daily_sales_dataset.csv')
TRAIN_END_DATE = '2024-12-31'  # Adjust based on your data range
OUTPUT_DIR = 'models'
PREDICTIONS_OUTPUT = 'predictions.csv'

# Products to train models for (None = all products)
TARGET_PRODUCTS = ['Strawberries', 'Chocolate', 'Eggs', 'Milk', 'Hot-Dogs']

# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_and_merge_data():
    """Load sales data (weather data is already included)"""
    print("Loading data...")
    
    # Load sales data (weather data is already included in daily_sales_dataset.csv)
    df = pd.read_csv(SALES_FILE)
    df['date'] = pd.to_datetime(df['date'])
    
    # Rename columns to match expected format
    df = df.rename(columns={
        'product': 'product_name',
        'items_sold': 'quantity_sold',
        'items_wasted': 'quantity_wasted',
        'temperature': 'temperature_2m_mean',
        'precipitation': 'precipitation_sum',
        'isWeekend': 'is_weekend',
        'isHoliday': 'is_holiday'
    })
    
    print(f"Loaded {len(df)} sales records")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Products: {df['product_name'].unique()}")
    
    return df

def prepare_product_data(df, product_name):
    """Prepare data for a specific product for Prophet"""
    
    # Filter for specific product
    product_df = df[df['product_name'] == product_name].copy()
    
    # Aggregate by date (in case there are multiple entries per day)
    product_df = product_df.groupby('date').agg({
        'quantity_sold': 'sum',
        'quantity_wasted': 'sum',
        'temperature_2m_mean': 'first',
        'precipitation_sum': 'first',
        'is_weekend': 'first',
        'is_holiday': 'first'
    }).reset_index()
    
    # Sort by date
    product_df = product_df.sort_values('date')
    
    # Prophet requires 'ds' (date) and 'y' (target variable) columns
    prophet_df = pd.DataFrame({
        'ds': product_df['date'],
        'y': product_df['quantity_sold'],
        'temperature': product_df['temperature_2m_mean'],
        'precipitation': product_df['precipitation_sum'],
        'is_weekend': product_df['is_weekend'].astype(int),
        'is_holiday': product_df['is_holiday'].astype(int)
    })
    
    return prophet_df

# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_prophet_model(train_df, product_name):
    """Train a Prophet model for a specific product"""
    
    print(f"\n{'='*60}")
    print(f"Training model for: {product_name}")
    print(f"{'='*60}")
    
    # Initialize Prophet with constrained settings to prevent overfitting
    model = Prophet(
        growth="flat",  # Disable trend detection - data shows no real growth
        yearly_seasonality=False,  # Only 1 year of data - not enough for yearly patterns
        weekly_seasonality=True,  # Keep weekly (Sat/Sun spike is real)
        daily_seasonality=False,
        seasonality_prior_scale=1.0,  # Less aggressive seasonality (default: 10)
        changepoint_prior_scale=0.001  # Very smooth trend (default: 0.05)
    )
    
    # Add only regressors that likely help
    model.add_regressor('is_weekend')
    model.add_regressor('is_holiday')
    model.add_regressor('temperature')
    model.add_regressor('precipitation')
    
    # Fit the model
    print("Fitting model...")
    model.fit(train_df[['ds', 'y', 'is_weekend', 'is_holiday', 'temperature', 'precipitation']])
    print("Model trained successfully!")
    
    return model

# ============================================================================
# VALIDATION & METRICS
# ============================================================================

def validate_model(model, test_df, product_name):
    """Validate model on test set and calculate metrics"""
    
    print(f"\nValidating model for {product_name}...")
    
    # Make predictions on test set
    forecast = model.predict(test_df)
    
    # Calculate metrics
    actual = test_df['y'].values
    predicted = forecast['yhat'].values
    
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted) * 100
    
    # Calculate baseline (naive forecast = historical average)
    baseline_prediction = test_df['y'].mean()
    baseline_mae = mean_absolute_error(actual, [baseline_prediction] * len(actual))
    
    improvement = ((baseline_mae - mae) / baseline_mae) * 100
    
    print(f"\n--- Validation Metrics for {product_name} ---")
    print(f"Mean Absolute Error (MAE): {mae:.2f} units")
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.1f}%")
    print(f"Baseline MAE: {baseline_mae:.2f} units")
    print(f"Improvement over baseline: {improvement:.1f}%")
    
    return {
        'product': product_name,
        'mae': mae,
        'mape': mape,
        'baseline_mae': baseline_mae,
        'improvement_pct': improvement
    }

# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualizations(model, train_df, test_df, forecast, product_name):
    """Create visualization plots for model performance"""
    
    print(f"\nCreating visualizations for {product_name}...")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Prophet Forecast Analysis - {product_name}', fontsize=16)
    
    # Plot 1: Forecast vs Actual (Test Period)
    ax1 = axes[0, 0]
    ax1.plot(test_df['ds'], test_df['y'], 'o-', label='Actual', color='black', markersize=4)
    ax1.plot(forecast['ds'], forecast['yhat'], 'o-', label='Predicted', color='blue', markersize=4)
    ax1.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                      alpha=0.3, color='blue', label='Confidence Interval')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Quantity Sold')
    ax1.set_title('Predictions vs Actual (Test Set)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Residuals
    ax2 = axes[0, 1]
    residuals = test_df['y'].values - forecast['yhat'].values
    ax2.scatter(forecast['yhat'], residuals, alpha=0.6)
    ax2.axhline(y=0, color='r', linestyle='--')
    ax2.set_xlabel('Predicted Values')
    ax2.set_ylabel('Residuals')
    ax2.set_title('Residual Plot')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Components (Trend + Seasonality)
    ax3 = axes[1, 0]
    # Create future dataframe for full visualization
    future = model.make_future_dataframe(periods=30)
    future['temperature'] = train_df['temperature'].mean()
    future['precipitation'] = train_df['precipitation'].mean()
    future['is_weekend'] = 0
    future['is_holiday'] = 0
    full_forecast = model.predict(future)
    
    ax3.plot(full_forecast['ds'], full_forecast['trend'], label='Trend')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Trend Component')
    ax3.set_title('Trend Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Weekly Seasonality
    ax4 = axes[1, 1]
    if 'weekly' in full_forecast.columns:
        # Group by day of week
        weekly_pattern = full_forecast.groupby(full_forecast['ds'].dt.dayofweek)['weekly'].mean()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ax4.bar(range(7), weekly_pattern.values)
        ax4.set_xticks(range(7))
        ax4.set_xticklabels(days)
        ax4.set_ylabel('Weekly Effect')
        ax4.set_title('Weekly Seasonality Pattern')
        ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    plt.savefig(f'visualizations/{product_name.replace(" ", "_")}_analysis.png', dpi=300, bbox_inches='tight')
    print(f"Saved visualization to: visualizations/{product_name.replace(' ', '_')}_analysis.png")
    
    plt.close()

def create_data_visualization(train_df, test_df, product_name):
    """Create visualization of the actual train and test data"""
    
    print(f"\nCreating data visualization for {product_name}...")
    
    # Create figure with specified dimensions
    f = plt.figure()
    f.set_figwidth(15)
    f.set_figheight(6)
    
    # Plot train and test series
    plt.plot(train_df['ds'], train_df['y'], linewidth=4, label="Train Series", color='blue')
    plt.plot(test_df['ds'], test_df['y'], linewidth=4, label="Test Series", color='orange')
    
    plt.legend(fontsize=25)
    plt.ylabel('Quantity Sold', fontsize=25)
    plt.xlabel('Date', fontsize=20)
    plt.title(f'Train/Test Data Split - {product_name}', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.grid(True, alpha=0.3)
    
    # Save figure
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    plt.savefig(f'visualizations/{product_name.replace(" ", "_")}_data.png', dpi=300, bbox_inches='tight')
    print(f"Saved data visualization to: visualizations/{product_name.replace(' ', '_')}_data.png")
    
    plt.close()

# ============================================================================
# FUTURE PREDICTIONS
# ============================================================================

def generate_future_predictions(model, train_df, product_name, days_ahead=7):
    """Generate predictions for future days"""
    
    print(f"\nGenerating {days_ahead}-day forecast for {product_name}...")
    
    # Create future dataframe
    future_dates = pd.date_range(
        start=train_df['ds'].max() + timedelta(days=1),
        periods=days_ahead
    )
    
    # Include all regressors that model was trained on
    future = pd.DataFrame({
        'ds': future_dates,
        'is_weekend': [1 if d.dayofweek >= 5 else 0 for d in future_dates],
        'is_holiday': [0] * days_ahead,  # Assume no holidays in next 7 days
        'temperature': [train_df['temperature'].mean()] * days_ahead,  # Use historical average
        'precipitation': [train_df['precipitation'].mean()] * days_ahead  # Use historical average
    })
    
    # Generate predictions
    forecast = model.predict(future)
    
    # Format output
    predictions = pd.DataFrame({
        'date': forecast['ds'],
        'product': product_name,
        'predicted_demand': forecast['yhat'].round(0),
        'lower_bound': forecast['yhat_lower'].round(0),
        'upper_bound': forecast['yhat_upper'].round(0),
    })
    
    print("\nFuture Predictions:")
    print(predictions.to_string(index=False))
    
    return predictions

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("="*60)
    print("SHELF ORACLE - PROPHET DEMAND FORECASTING")
    print("="*60)
    
    # Load data
    df = load_and_merge_data()
    
    # Get products to process
    if TARGET_PRODUCTS is None:
        products = df['product_name'].unique()
    else:
        products = TARGET_PRODUCTS
    
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Store metrics for all products
    all_metrics = []
    all_predictions = []
    
    # Process each product
    for product in products:
        try:
            # Prepare data
            product_df = prepare_product_data(df, product)
            
            # Split into train/test (chronological)
            train = product_df[product_df['ds'] <= TRAIN_END_DATE]
            test = product_df[product_df['ds'] > TRAIN_END_DATE]
            
            print(f"\nTrain set: {len(train)} days ({train['ds'].min()} to {train['ds'].max()})")
            print(f"Test set: {len(test)} days ({test['ds'].min()} to {test['ds'].max()})")
            
            # Create data visualization (train/test split)
            create_data_visualization(train, test, product)
            
            # Train model
            model = train_prophet_model(train, product)
            
            # Validate on test set
            if len(test) > 0:
                metrics = validate_model(model, test, product)
                all_metrics.append(metrics)
                
                # Create visualizations
                forecast = model.predict(test)
                create_visualizations(model, train, test, forecast, product)
            else:
                print(f"Warning: No test data available for {product}")
            
            # Generate future predictions
            predictions = generate_future_predictions(model, train, product)
            all_predictions.append(predictions)
            
            # Save model
            model_path = os.path.join(OUTPUT_DIR, f'{product.replace(" ", "_")}_model.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Model saved to: {model_path}")
            
        except Exception as e:
            print(f"Error processing {product}: {str(e)}")
            continue
    
    # Save summary metrics
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        metrics_df.to_csv('validation_metrics.csv', index=False)
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(metrics_df.to_string(index=False))
    
    # Save all predictions
    if all_predictions:
        predictions_df = pd.concat(all_predictions, ignore_index=True)
        predictions_df.to_csv(PREDICTIONS_OUTPUT, index=False)
        print(f"\nAll predictions saved to: {PREDICTIONS_OUTPUT}")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
