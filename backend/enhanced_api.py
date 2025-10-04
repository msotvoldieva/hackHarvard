"""
Enhanced API with improved prediction capabilities
Integrates weather data, inventory awareness, and ensemble models
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import pickle

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather_service import WeatherDataManager
from inventory_aware_predictor import InventoryAwarePredictor, integrate_with_predictions

app = Flask(__name__)

# Configuration
MODELS_DIR = 'models'
ENHANCED_MODELS_DIR = 'models'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/forecast/enhanced', methods=['POST'])
def generate_enhanced_forecast():
    """Generate enhanced forecast with weather and inventory integration"""
    try:
        data = request.get_json()
        product_name = data.get('product')
        days_ahead = data.get('days', 30)
        include_inventory = data.get('include_inventory', True)
        inventory_data = data.get('inventory_data', [])
        
        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400
        
        # Try to load enhanced model first, fallback to basic Prophet
        enhanced_model_path = os.path.join(ENHANCED_MODELS_DIR, f'enhanced_{product_name.replace(" ", "_")}_model.pkl')
        basic_model_path = os.path.join(MODELS_DIR, f'{product_name.replace(" ", "_")}_model.pkl')
        
        if os.path.exists(enhanced_model_path):
            # Use enhanced ensemble model
            with open(enhanced_model_path, 'rb') as f:
                forecaster = pickle.load(f)
            
            # Get real-time weather data
            weather_manager = WeatherDataManager()
            weather_data = weather_manager.get_weather_for_predictions(days_ahead)
            
            # Generate future dates
            future_dates = pd.date_range(
                start=datetime.now(),
                periods=days_ahead
            )
            
            # Create future dataframe with real weather data
            future_df = pd.DataFrame({
                'ds': future_dates,
                'is_weekend': [1 if d.dayofweek >= 5 else 0 for d in future_dates],
                'is_holiday': [0] * days_ahead,  # Could be enhanced with holiday calendar
                'temperature': weather_data['temperature'].values[:days_ahead],
                'precipitation': weather_data['precipitation'].values[:days_ahead],
                'humidity': weather_data['humidity'].values[:days_ahead],
                'wind_speed': weather_data['wind_speed'].values[:days_ahead],
                'cloud_cover': weather_data['cloud_cover'].values[:days_ahead]
            })
            
            # Get feature columns (this would be stored with the model in production)
            feature_cols = [col for col in future_df.columns if col != 'ds']
            
            # Make ensemble predictions
            ensemble_pred, prophet_pred = forecaster.predict_ensemble(future_df, feature_cols)
            
            # Format predictions
            predictions = []
            for i, (date, pred) in enumerate(zip(future_dates, ensemble_pred)):
                predictions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_demand': round(pred),
                    'lower_bound': round(pred * 0.85),  # 15% lower bound
                    'upper_bound': round(pred * 1.15),  # 15% upper bound
                    'confidence': 'high' if i < 7 else 'medium'  # Higher confidence for near-term
                })
            
            model_type = 'enhanced_ensemble'
            
        elif os.path.exists(basic_model_path):
            # Fallback to basic Prophet model
            with open(basic_model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Generate future dates
            future_dates = pd.date_range(
                start=datetime.now(),
                periods=days_ahead
            )
            
            # Create future dataframe with default values
            future = pd.DataFrame({
                'ds': future_dates,
                'is_weekend': [1 if d.dayofweek >= 5 else 0 for d in future_dates],
                'is_holiday': [0] * days_ahead,
                'temperature': [20] * days_ahead,  # Default temperature
                'precipitation': [0] * days_ahead   # Default precipitation
            })
            
            # Generate predictions
            forecast = model.predict(future)
            
            # Format predictions
            predictions = []
            for i, row in forecast.iterrows():
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_demand': round(row['yhat']),
                    'lower_bound': round(row['yhat_lower']),
                    'upper_bound': round(row['yhat_upper']),
                    'confidence': 'medium'
                })
            
            model_type = 'basic_prophet'
            
        else:
            return jsonify({'error': f'No model found for {product_name}'}), 404
        
        # Prepare response
        response = {
            'product': product_name,
            'model_type': model_type,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat(),
            'days_ahead': days_ahead
        }
        
        # Add inventory-aware recommendations if requested
        if include_inventory and inventory_data:
            inventory_predictor = InventoryAwarePredictor(inventory_data)
            order_recommendation = inventory_predictor.calculate_optimal_order_quantity(
                product_name, 
                [p['predicted_demand'] for p in predictions[:7]],  # Next 7 days
                days_ahead=7
            )
            
            response['inventory_recommendation'] = order_recommendation
            response['waste_reduction_tips'] = inventory_predictor.get_waste_reduction_recommendations()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/report', methods=['POST'])
def generate_inventory_report():
    """Generate comprehensive inventory report"""
    try:
        data = request.get_json()
        inventory_data = data.get('inventory_data', [])
        
        if not inventory_data:
            return jsonify({'error': 'Inventory data is required'}), 400
        
        predictor = InventoryAwarePredictor(inventory_data)
        report = predictor.generate_inventory_report()
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/current', methods=['GET'])
def get_current_weather():
    """Get current weather data"""
    try:
        weather_manager = WeatherDataManager()
        current_weather = weather_manager.weather_service.get_current_weather()
        
        return jsonify({
            'current_weather': current_weather,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/forecast', methods=['GET'])
def get_weather_forecast():
    """Get weather forecast"""
    try:
        days = request.args.get('days', 7, type=int)
        weather_manager = WeatherDataManager()
        forecast = weather_manager.weather_service.get_weather_forecast(days)
        
        return jsonify({
            'forecast': forecast,
            'days': days,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/insights', methods=['POST'])
def get_analytics_insights():
    """Get analytics insights combining predictions, inventory, and weather"""
    try:
        data = request.get_json()
        products = data.get('products', ['Milk', 'Eggs', 'Strawberries', 'Chocolate', 'Hot-Dogs'])
        inventory_data = data.get('inventory_data', [])
        
        insights = {
            'summary': {
                'total_products_analyzed': len(products),
                'analysis_date': datetime.now().isoformat()
            },
            'products': {},
            'recommendations': []
        }
        
        # Analyze each product
        for product in products:
            # Get basic forecast
            forecast_response = generate_enhanced_forecast()
            if forecast_response[1] == 200:  # Success
                forecast_data = forecast_response[0].get_json()
                
                # Add inventory analysis if data available
                if inventory_data:
                    inventory_predictor = InventoryAwarePredictor(inventory_data)
                    order_rec = inventory_predictor.calculate_optimal_order_quantity(
                        product, 
                        [p['predicted_demand'] for p in forecast_data['predictions'][:7]]
                    )
                    
                    insights['products'][product] = {
                        'forecast': forecast_data,
                        'order_recommendation': order_rec
                    }
                    
                    # Add to recommendations
                    if order_rec['order_priority'] in ['URGENT', 'HIGH']:
                        insights['recommendations'].append({
                            'type': 'ORDER',
                            'product': product,
                            'priority': order_rec['order_priority'],
                            'message': order_rec['reason']
                        })
                else:
                    insights['products'][product] = {
                        'forecast': forecast_data
                    }
        
        # Add waste reduction recommendations
        if inventory_data:
            inventory_predictor = InventoryAwarePredictor(inventory_data)
            waste_recommendations = inventory_predictor.get_waste_reduction_recommendations()
            insights['recommendations'].extend(waste_recommendations)
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
