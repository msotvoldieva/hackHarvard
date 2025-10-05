"""
EcoPredict Backend API
Flask API server for demand forecasting
"""

import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
import numpy as np
from chatbot import WasteLessChatbot

chatbot = WasteLessChatbot()
sessions = {}

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'EcoPredict API is running'})

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get list of available products"""
    try:
        # Load sales data to get product list
        sales_file = os.path.join(DATA_DIR, 'daily_sales_dataset.csv')
        df = pd.read_csv(sales_file)
        products = df['product'].unique().tolist()
        
        return jsonify({
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<product_name>', methods=['GET'])
def get_predictions(product_name):
    """Get predictions for a specific product"""
    try:
        # Load predictions from CSV
        predictions_file = os.path.join(BASE_DIR, 'output', 'predictions.csv')
        if os.path.exists(predictions_file):
            df = pd.read_csv(predictions_file)
            product_predictions = df[df['product'] == product_name].to_dict('records')
            return jsonify({'predictions': product_predictions})
        else:
            return jsonify({'error': 'Predictions file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/all', methods=['GET'])
def get_all_predictions():
    """Get all predictions formatted for dashboard"""
    try:
        predictions_file = os.path.join(BASE_DIR, 'output', 'predictions.csv')
        if os.path.exists(predictions_file):
            df = pd.read_csv(predictions_file)
            
            # Group by product and format for dashboard
            formatted_data = {}
            for product in df['product'].unique():
                product_data = df[df['product'] == product].head(7)  # First 7 days
                
                formatted_product_data = []
                for _, row in product_data.iterrows():
                    # Parse date and format as "Jan 1", "Jan 2", etc.
                    date_obj = pd.to_datetime(row['date'])
                    formatted_date = date_obj.strftime('%b %d')
                    
                    formatted_product_data.append({
                        'date': formatted_date,
                        'predicted': int(row['predicted_demand']),
                        'lower': int(row['lower_bound']),
                        'upper': int(row['upper_bound']),
                        # Keep hardcoded waste and total for demonstration as requested
                        'waste': 8 + len(formatted_product_data) % 4 if product == 'Strawberries' else
                                11 + len(formatted_product_data) % 4 if product == 'Chocolate' else
                                14 + len(formatted_product_data) % 7 if product == 'Eggs' else
                                18 + len(formatted_product_data) % 7 if product == 'Milk' else
                                9 + len(formatted_product_data) % 6,
                        'total': int(row['predicted_demand']) + (
                            8 + len(formatted_product_data) % 4 if product == 'Strawberries' else
                            11 + len(formatted_product_data) % 4 if product == 'Chocolate' else
                            14 + len(formatted_product_data) % 7 if product == 'Eggs' else
                            18 + len(formatted_product_data) % 7 if product == 'Milk' else
                            9 + len(formatted_product_data) % 6
                        )
                    })
                
                formatted_data[product] = formatted_product_data
            
            return jsonify({'predictions': formatted_data})
        else:
            return jsonify({'error': 'Predictions file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get validation metrics for all products"""
    try:
        metrics_file = os.path.join(BASE_DIR, 'output', 'validation_metrics.csv')
        if os.path.exists(metrics_file):
            df = pd.read_csv(metrics_file)
            metrics = df.to_dict('records')
            return jsonify({'metrics': metrics})
        else:
            return jsonify({'error': 'Metrics file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast', methods=['POST'])
def generate_forecast():
    """Generate new forecast for a product"""
    try:
        data = request.get_json()
        product_name = data.get('product')
        days_ahead = data.get('days', 30)
        
        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400
        
        # Load model
        model_file = os.path.join(MODELS_DIR, f'{product_name.replace(" ", "_")}_model.pkl')
        if not os.path.exists(model_file):
            return jsonify({'error': f'Model for {product_name} not found'}), 404
        
        with open(model_file, 'rb') as f:
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
        
        # Format response
        predictions = []
        for i, row in forecast.iterrows():
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_demand': round(row['yhat']),
                'lower_bound': round(row['yhat_lower']),
                'upper_bound': round(row['yhat_upper'])
            })
        
        return jsonify({
            'product': product_name,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    # Get or create session
    if not session_id:
        session_id = str(uuid.uuid4())
    
    session_data = sessions.get(session_id, {"history": []})
    
    try:
        # Process message
        result = chatbot.handle_message(user_message, session_data)
        
        # Update session history
        session_data["history"].append({
            "user": user_message,
            "assistant": result["response"]
        })
        sessions[session_id] = session_data
        
        return jsonify({
            "response": result["response"],
            "session_id": session_id,
            "data_used": result.get("data_used")
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/greeting', methods=['GET'])
def get_greeting():
    """Get proactive greeting message"""
    try:
        greeting = chatbot.get_proactive_greeting()
        return jsonify({"greeting": greeting})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
