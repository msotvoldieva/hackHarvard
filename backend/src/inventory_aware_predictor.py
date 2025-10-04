"""
Inventory-Aware Demand Prediction
Considers current inventory levels and expiration dates for better ordering decisions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class InventoryAwarePredictor:
    def __init__(self, inventory_data: List[Dict]):
        """
        Initialize with current inventory data
        
        inventory_data format:
        [
            {
                'product': 'Milk',
                'batch': 'A',
                'date_bought': '2025-09-25',
                'expiration_date': '2025-10-09',
                'quantity': 8
            },
            ...
        ]
        """
        self.inventory_data = inventory_data
        self.current_date = datetime.now()
        
    def get_inventory_summary(self) -> Dict:
        """Get summary of current inventory by product"""
        summary = {}
        
        for item in self.inventory_data:
            product = item['product']
            exp_date = datetime.strptime(item['expiration_date'], '%Y-%m-%d')
            days_to_exp = (exp_date - self.current_date).days
            
            if product not in summary:
                summary[product] = {
                    'total_quantity': 0,
                    'expiring_soon': 0,  # ≤5 days
                    'expiring_warning': 0,  # 6-14 days
                    'expiring_good': 0,  # 15+ days
                    'expired': 0,
                    'batches': []
                }
            
            summary[product]['total_quantity'] += item['quantity']
            summary[product]['batches'].append({
                'batch': item['batch'],
                'quantity': item['quantity'],
                'days_to_exp': days_to_exp,
                'expiration_date': item['expiration_date']
            })
            
            # Categorize by expiration status
            if days_to_exp < 0:
                summary[product]['expired'] += item['quantity']
            elif days_to_exp <= 5:
                summary[product]['expiring_soon'] += item['quantity']
            elif days_to_exp <= 14:
                summary[product]['expiring_warning'] += item['quantity']
            else:
                summary[product]['expiring_good'] += item['quantity']
        
        return summary
    
    def calculate_optimal_order_quantity(self, 
                                       product: str, 
                                       predicted_demand: List[float], 
                                       days_ahead: int = 7) -> Dict:
        """
        Calculate optimal order quantity considering:
        - Predicted demand
        - Current inventory
        - Expiration dates
        - Waste reduction goals
        """
        
        inventory_summary = self.get_inventory_summary()
        
        if product not in inventory_summary:
            return {
                'product': product,
                'recommended_order': 0,
                'reason': 'No current inventory data',
                'confidence': 'low'
            }
        
        current_inventory = inventory_summary[product]
        total_current = current_inventory['total_quantity']
        expiring_soon = current_inventory['expiring_soon']
        
        # Calculate demand for the period
        total_demand = sum(predicted_demand[:days_ahead])
        avg_daily_demand = total_demand / days_ahead
        
        # Calculate days of inventory remaining
        days_of_inventory = total_current / avg_daily_demand if avg_daily_demand > 0 else 999
        
        # Calculate waste risk (items expiring soon that won't be sold)
        waste_risk = max(0, expiring_soon - (avg_daily_demand * 5))  # 5 days to sell expiring items
        
        # Determine order recommendation
        if days_of_inventory < 3:  # Critical stock
            recommended_order = max(0, total_demand - total_current + avg_daily_demand * 2)  # 2 days buffer
            confidence = 'high'
            reason = 'Critical stock level - immediate order needed'
            
        elif days_of_inventory < 7:  # Low stock
            recommended_order = max(0, total_demand - total_current + avg_daily_demand * 3)  # 3 days buffer
            confidence = 'high'
            reason = 'Low stock level - order recommended'
            
        elif waste_risk > avg_daily_demand:  # High waste risk
            recommended_order = max(0, total_demand - total_current)
            confidence = 'medium'
            reason = 'High waste risk - order only if needed'
            
        elif days_of_inventory > 14:  # Overstocked
            recommended_order = 0
            confidence = 'high'
            reason = 'Overstocked - no order needed'
            
        else:  # Normal stock
            recommended_order = max(0, total_demand - total_current + avg_daily_demand * 2)
            confidence = 'medium'
            reason = 'Normal stock level - standard order'
        
        # Apply waste reduction factor (reduce order if high waste risk)
        if waste_risk > avg_daily_demand * 2:
            recommended_order = recommended_order * 0.7  # Reduce by 30%
            reason += ' (reduced due to waste risk)'
        
        return {
            'product': product,
            'current_inventory': total_current,
            'expiring_soon': expiring_soon,
            'predicted_demand': total_demand,
            'days_of_inventory': round(days_of_inventory, 1),
            'waste_risk': round(waste_risk, 1),
            'recommended_order': round(recommended_order),
            'confidence': confidence,
            'reason': reason,
            'order_priority': self._get_order_priority(days_of_inventory, waste_risk)
        }
    
    def _get_order_priority(self, days_of_inventory: float, waste_risk: float) -> str:
        """Determine order priority based on inventory and waste risk"""
        if days_of_inventory < 3:
            return 'URGENT'
        elif days_of_inventory < 7 or waste_risk > 10:
            return 'HIGH'
        elif days_of_inventory < 14:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_waste_reduction_recommendations(self) -> List[Dict]:
        """Get recommendations for reducing waste"""
        recommendations = []
        inventory_summary = self.get_inventory_summary()
        
        for product, data in inventory_summary.items():
            if data['expiring_soon'] > 0:
                recommendations.append({
                    'product': product,
                    'action': 'PROMOTE',
                    'quantity': data['expiring_soon'],
                    'priority': 'HIGH',
                    'suggestion': f'Promote {product} - {data["expiring_soon"]} units expiring within 5 days'
                })
            
            if data['expired'] > 0:
                recommendations.append({
                    'product': product,
                    'action': 'DISCARD',
                    'quantity': data['expired'],
                    'priority': 'URGENT',
                    'suggestion': f'Discard {product} - {data["expired"]} units already expired'
                })
        
        return recommendations
    
    def generate_inventory_report(self) -> Dict:
        """Generate comprehensive inventory report"""
        inventory_summary = self.get_inventory_summary()
        
        total_products = len(inventory_summary)
        total_inventory = sum(data['total_quantity'] for data in inventory_summary.values())
        total_expiring_soon = sum(data['expiring_soon'] for data in inventory_summary.values())
        total_expired = sum(data['expired'] for data in inventory_summary.values())
        
        waste_percentage = (total_expired / total_inventory * 100) if total_inventory > 0 else 0
        
        return {
            'summary': {
                'total_products': total_products,
                'total_inventory': total_inventory,
                'total_expiring_soon': total_expiring_soon,
                'total_expired': total_expired,
                'waste_percentage': round(waste_percentage, 2)
            },
            'products': inventory_summary,
            'recommendations': self.get_waste_reduction_recommendations(),
            'generated_at': datetime.now().isoformat()
        }

# Example usage and integration
def integrate_with_predictions(predictions: Dict, inventory_data: List[Dict]) -> Dict:
    """
    Integrate inventory data with demand predictions
    """
    predictor = InventoryAwarePredictor(inventory_data)
    
    enhanced_predictions = {}
    
    for product, pred_data in predictions.items():
        if isinstance(pred_data, dict) and 'predictions' in pred_data:
            predicted_demand = [p['predicted_demand'] for p in pred_data['predictions']]
            
            order_recommendation = predictor.calculate_optimal_order_quantity(
                product, predicted_demand, days_ahead=7
            )
            
            enhanced_predictions[product] = {
                'demand_forecast': pred_data,
                'order_recommendation': order_recommendation
            }
    
    return {
        'enhanced_predictions': enhanced_predictions,
        'inventory_report': predictor.generate_inventory_report()
    }

if __name__ == "__main__":
    # Example usage
    sample_inventory = [
        {'product': 'Milk', 'batch': 'A', 'date_bought': '2025-09-25', 'expiration_date': '2025-10-09', 'quantity': 8},
        {'product': 'Milk', 'batch': 'B', 'date_bought': '2025-09-30', 'expiration_date': '2025-10-14', 'quantity': 20},
        {'product': 'Strawberries', 'batch': 'A', 'date_bought': '2025-10-02', 'expiration_date': '2025-10-09', 'quantity': 12},
    ]
    
    predictor = InventoryAwarePredictor(sample_inventory)
    report = predictor.generate_inventory_report()
    print(json.dumps(report, indent=2))
