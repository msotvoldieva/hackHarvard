import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SALES_FILE = os.path.join(BASE_DIR, 'data', 'store_sales_2024.csv')

df = pd.read_csv(SALES_FILE)

# Check actual sales distributions
print("\n=== SALES STATISTICS ===")
for product in ['Organic Strawberries', 'Whole Milk (1 gallon)', 'Hot Dogs (8-pack)']:
    product_df = df[df['product_name'] == product]
    
    print(f"\n{product}:")
    print(f"  Daily sales - Mean: {product_df['quantity_sold'].mean():.1f}")
    print(f"  Daily sales - Median: {product_df['quantity_sold'].median():.1f}")
    print(f"  Daily sales - Min: {product_df['quantity_sold'].min()}")
    print(f"  Daily sales - Max: {product_df['quantity_sold'].max()}")

# Check for duplicate dates
print("\n=== CHECKING FOR DUPLICATES ===")
duplicates = df.groupby(['date', 'product_name']).size()
dupes_found = duplicates[duplicates > 1]
if len(dupes_found) > 0:
    print("⚠️  DUPLICATES FOUND:")
    print(dupes_found.head(10))
else:
    print("✓ No duplicates found")

# Check train vs test distributions
print("\n=== TRAIN VS TEST COMPARISON ===")
df['date'] = pd.to_datetime(df['date'])
for product in ['Organic Strawberries', 'Whole Milk (1 gallon)', 'Hot Dogs (8-pack)']:
    product_df = df[df['product_name'] == product]
    train = product_df[product_df['date'] <= '2024-08-31']
    test = product_df[product_df['date'] > '2024-08-31']
    
    print(f"\n{product}:")
    print(f"  Train avg: {train['quantity_sold'].mean():.1f} units/day")
    print(f"  Test avg: {test['quantity_sold'].mean():.1f} units/day")
    print(f"  Difference: {((test['quantity_sold'].mean() - train['quantity_sold'].mean()) / train['quantity_sold'].mean() * 100):.1f}%")
