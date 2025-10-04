#!/usr/bin/env python3
"""
Adjust store sales data to create logical correlations with weather data
"""

import pandas as pd
import numpy as np
from datetime import datetime

def adjust_sales_with_weather():
    """Adjust sales data to correlate logically with weather patterns"""
    
    print("Loading data...")
    # Load existing data
    sales = pd.read_csv('data/store_sales_2024.csv')
    weather = pd.read_csv('data/daily_weather_data.csv')
    
    # Convert dates
    sales['date'] = pd.to_datetime(sales['date'])
    weather['date'] = pd.to_datetime(weather['date'])
    
    # Merge sales with weather
    merged = sales.merge(weather, on='date', how='left')
    
    print("Applying weather correlations...")
    
    # Create a copy for modifications
    adjusted_sales = sales.copy()
    
    # Apply weather-based adjustments for each product
    for idx, row in merged.iterrows():
        date = row['date']
        temp = row['temperature_2m_mean']
        precip = row['precipitation_sum']
        product = row['product_name']
        base_quantity = row['quantity_sold']
        is_weekend = row['is_weekend']
        
        # Calculate adjustment factors
        adjustment_factor = 1.0
        
        if product == 'Hot Dogs (8-pack)':
            # Hot dogs: higher sales on warm, dry days (grilling weather)
            # Especially strong on weekends
            temp_factor = 1.0
            if temp > 70:  # Warm grilling weather
                temp_factor = 1.2 + (temp - 70) * 0.01  # Up to 1.35x at 85°F
            elif temp > 50:  # Mild weather
                temp_factor = 1.0 + (temp - 50) * 0.01  # Up to 1.2x at 70°F
            elif temp < 35:  # Cold weather reduces grilling
                temp_factor = 0.8 - (35 - temp) * 0.01  # Down to 0.6x at 10°F
            
            precip_factor = 1.0
            if precip == 0:  # No rain = better grilling
                precip_factor = 1.15
            elif precip > 0.5:  # Heavy rain reduces grilling
                precip_factor = 0.7
            elif precip > 0.1:  # Light rain somewhat reduces grilling
                precip_factor = 0.85
            
            weekend_boost = 1.3 if is_weekend else 1.0
            adjustment_factor = temp_factor * precip_factor * weekend_boost
            
        elif product == 'Organic Strawberries':
            # Strawberries: higher sales in warm weather (fresh fruit appeal)
            # People want fresh fruit when it's warm and sunny
            temp_factor = 1.0
            if temp > 65:  # Warm weather increases fresh fruit consumption
                temp_factor = 1.1 + (temp - 65) * 0.015  # Up to 1.4x at 85°F
            elif temp > 45:  # Mild weather
                temp_factor = 1.0 + (temp - 45) * 0.005  # Up to 1.1x at 65°F
            elif temp < 35:  # Cold weather reduces fresh fruit appeal
                temp_factor = 0.9 - (35 - temp) * 0.01  # Down to 0.65x at 10°F
            
            precip_factor = 1.0
            if precip == 0:  # Sunny days = more fresh fruit sales
                precip_factor = 1.1
            elif precip > 0.3:  # Rainy days reduce fresh produce shopping
                precip_factor = 0.9
            
            # Seasonal factor - strawberries are more popular in spring/summer
            month = date.month
            if month in [5, 6, 7]:  # Peak strawberry season
                seasonal_factor = 1.2
            elif month in [4, 8]:  # Good strawberry months
                seasonal_factor = 1.1
            elif month in [3, 9]:  # Okay strawberry months
                seasonal_factor = 1.0
            else:  # Off-season
                seasonal_factor = 0.8
            
            adjustment_factor = temp_factor * precip_factor * seasonal_factor
            
        elif product == 'Whole Milk (1 gallon)':
            # Milk: more stable but slight increases in cold weather (comfort foods, hot drinks)
            # and during rainy days (people stock up)
            temp_factor = 1.0
            if temp < 40:  # Cold weather increases milk consumption (hot drinks, baking)
                temp_factor = 1.05 + (40 - temp) * 0.003  # Up to 1.14x at 10°F
            elif temp > 75:  # Very hot weather slightly reduces milk consumption
                temp_factor = 0.98 - (temp - 75) * 0.002  # Down to 0.96x at 85°F
            
            precip_factor = 1.0
            if precip > 0.5:  # Heavy rain = people stock up on essentials
                precip_factor = 1.08
            elif precip > 0.1:  # Light rain = slight increase
                precip_factor = 1.03
            
            weekend_factor = 1.05 if is_weekend else 1.0  # Slight weekend increase for family shopping
            
            adjustment_factor = temp_factor * precip_factor * weekend_factor
        
        # Apply bounds to prevent unrealistic values
        adjustment_factor = max(0.5, min(2.0, adjustment_factor))
        
        # Apply adjustment with some randomness to make it realistic
        noise = np.random.normal(1.0, 0.05)  # 5% random variation
        final_factor = adjustment_factor * noise
        final_factor = max(0.4, min(2.5, final_factor))
        
        # Calculate new quantity
        new_quantity = int(round(base_quantity * final_factor))
        new_quantity = max(1, new_quantity)  # Ensure at least 1 unit sold
        
        # Update the sales data
        mask = (adjusted_sales['date'] == date) & (adjusted_sales['product_name'] == product)
        adjusted_sales.loc[mask, 'quantity_sold'] = new_quantity
        
        # Adjust waste proportionally but cap it
        original_waste = adjusted_sales.loc[mask, 'quantity_wasted'].iloc[0]
        waste_ratio = original_waste / base_quantity if base_quantity > 0 else 0
        new_waste = int(round(new_quantity * waste_ratio * 0.8))  # Slightly reduce waste ratio
        new_waste = max(0, min(new_waste, new_quantity // 3))  # Cap waste at 1/3 of sales
        adjusted_sales.loc[mask, 'quantity_wasted'] = new_waste
    
    # Save the adjusted data
    adjusted_sales.to_csv('data/store_sales_2024.csv', index=False)
    
    print("Sales data adjusted successfully!")
    print("\nSummary of changes:")
    
    # Show summary statistics
    for product in adjusted_sales['product_name'].unique():
        orig_data = sales[sales['product_name'] == product]['quantity_sold']
        adj_data = adjusted_sales[adjusted_sales['product_name'] == product]['quantity_sold']
        
        print(f"\n{product}:")
        print(f"  Original range: {orig_data.min()}-{orig_data.max()} (avg: {orig_data.mean():.1f})")
        print(f"  Adjusted range: {adj_data.min()}-{adj_data.max()} (avg: {adj_data.mean():.1f})")
        print(f"  Change in average: {((adj_data.mean() / orig_data.mean() - 1) * 100):+.1f}%")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    adjust_sales_with_weather()
