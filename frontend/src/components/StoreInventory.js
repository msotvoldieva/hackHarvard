import React, { useState } from 'react';
import { AlertCircle, Package } from 'lucide-react';

const StoreInventory = () => {
  const [inventory] = useState([
    // Chocolate
    { id: 1, product: 'Chocolate', batch: 'A', dateBought: '2025-09-15', expirationDate: '2026-03-15', quantity: 24 },
    { id: 2, product: 'Chocolate', batch: 'B', dateBought: '2025-09-28', expirationDate: '2026-03-28', quantity: 36 },
    { id: 3, product: 'Chocolate', batch: 'C', dateBought: '2025-10-01', expirationDate: '2026-04-01', quantity: 18 },
    
    // Strawberries
    { id: 4, product: 'Strawberries', batch: 'A', dateBought: '2025-10-02', expirationDate: '2025-10-09', quantity: 12 },
    { id: 5, product: 'Strawberries', batch: 'B', dateBought: '2025-10-03', expirationDate: '2025-10-10', quantity: 15 },
    
    // Milk
    { id: 6, product: 'Milk', batch: 'A', dateBought: '2025-09-25', expirationDate: '2025-10-09', quantity: 8 },
    { id: 7, product: 'Milk', batch: 'B', dateBought: '2025-09-30', expirationDate: '2025-10-14', quantity: 20 },
    { id: 8, product: 'Milk', batch: 'C', dateBought: '2025-10-02', expirationDate: '2025-10-16', quantity: 16 },
    
    // Hot Dogs
    { id: 9, product: 'Hot Dogs', batch: 'A', dateBought: '2025-09-20', expirationDate: '2025-10-20', quantity: 30 },
    { id: 10, product: 'Hot Dogs', batch: 'B', dateBought: '2025-10-01', expirationDate: '2025-10-31', quantity: 45 },
    
    // Eggs
    { id: 11, product: 'Eggs', batch: 'A', dateBought: '2025-09-28', expirationDate: '2025-10-26', quantity: 60 },
    { id: 12, product: 'Eggs', batch: 'B', dateBought: '2025-10-01', expirationDate: '2025-10-29', quantity: 48 },
    { id: 13, product: 'Eggs', batch: 'C', dateBought: '2025-10-03', expirationDate: '2025-10-31', quantity: 36 }
  ]);

  const [statusFilter, setStatusFilter] = useState('all');

  const today = new Date('2025-10-04');
  
  const getDaysUntilExpiration = (expirationDate) => {
    const expDate = new Date(expirationDate);
    const diffTime = expDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getExpirationStatus = (expirationDate) => {
    const days = getDaysUntilExpiration(expirationDate);
    if (days < 0) return 'expired';
    if (days <= 5) return 'critical';
    if (days <= 14) return 'warning';
    return 'good';
  };


  const filteredInventory = statusFilter === 'all' 
    ? inventory 
    : inventory.filter(item => getExpirationStatus(item.expirationDate) === statusFilter);

  const getStatusStyle = (status) => {
    const styles = {
      expired: { backgroundColor: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca' },
      critical: { backgroundColor: '#fff7ed', color: '#9a3412', border: '1px solid #fed7aa' },
      warning: { backgroundColor: '#fefce8', color: '#a16207', border: '1px solid #fde68a' },
      good: { backgroundColor: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0' }
    };
    return styles[status] || styles.good;
  };

  return (
    <div style={{ padding: '32px', flex: 1 }}>
      <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Package size={32} style={{ color: '#3b82f6' }} />
          <h1 style={{ fontSize: '30px', fontWeight: 'bold', color: '#1f2937', margin: 0 }}>Store Inventory</h1>
        </div>
        <p style={{ color: '#6b7280', margin: 0 }}>Current Date: {today.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>

      <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Filter by Status:</label>
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '8px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              outline: 'none',
              fontSize: '14px',
              backgroundColor: 'white'
            }}
          >
            <option value="all">All Items</option>
            <option value="critical">Critical (≤5 days)</option>
            <option value="warning">Warning (6-14 days)</option>
            <option value="good">Good (15+ days)</option>
          </select>
          <span style={{ fontSize: '14px', color: '#6b7280', marginLeft: 'auto' }}>
            Showing {filteredInventory.length} of {inventory.length} items
          </span>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%' }}>
            <thead style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              <tr>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Product</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Date Bought</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Expiration Date</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Days Until Exp.</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Quantity</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#374151' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map((item) => {
                const status = getExpirationStatus(item.expirationDate);
                const daysLeft = getDaysUntilExpiration(item.expirationDate);
                const statusStyle = getStatusStyle(status);
                
                return (
                  <tr key={item.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <td style={{ padding: '16px 24px', fontSize: '14px', fontWeight: '500', color: '#111827' }}>{item.product}</td>
                    <td style={{ padding: '16px 24px', fontSize: '14px', color: '#6b7280' }}>{item.dateBought}</td>
                    <td style={{ padding: '16px 24px', fontSize: '14px', color: '#6b7280' }}>{item.expirationDate}</td>
                    <td style={{ padding: '16px 24px', fontSize: '14px', color: '#6b7280' }}>
                      {daysLeft < 0 ? 'Expired' : `${daysLeft} days`}
                    </td>
                    <td style={{ padding: '16px 24px', fontSize: '14px', color: '#6b7280' }}>{item.quantity}</td>
                    <td style={{ padding: '16px 24px' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '4px 12px',
                        borderRadius: '9999px',
                        fontSize: '12px',
                        fontWeight: '500',
                        ...statusStyle
                      }}>
                        {status === 'critical' && <AlertCircle size={12} />}
                        {status === 'expired' ? 'Expired' : status === 'critical' ? 'Critical' : status === 'warning' ? 'Warning' : 'Good'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ marginTop: '24px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '16px', marginTop: 0 }}>Status Legend</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: '#10b981' }}></span>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>Good (15+ days)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></span>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>Warning (6-14 days)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: '#f97316' }}></span>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>Critical (≤5 days)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: '#ef4444' }}></span>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>Expired</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoreInventory;
