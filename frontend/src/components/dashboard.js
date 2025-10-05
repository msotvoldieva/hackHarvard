import React, { useState } from 'react';
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Bar, BarChart, PieChart, Pie, Cell } from 'recharts';
import { Menu, Search, Bell, Settings, LogOut, LayoutDashboard, Package, Calendar, MessageSquare, TrendingUp, Users, Box, Warehouse } from 'lucide-react';
import StoreInventory from './StoreInventory';
import hotdogImage from '../hotdog.jpg';
import logoImage from '../logo.png';
import Chat from './chat.js';

const WasteLess = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedProduct, setSelectedProduct] = useState('Milk');
  const [showProductDropdown, setShowProductDropdown] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  
  const csvData = {
    Strawberries: Array.from({ length: 7 }, (_, i) => ({
      date: `Jan ${i + 1}`,
      predicted: [43, 45, 50, 57, 57, 39, 41][i % 7],
      lower: [38, 40, 45, 51, 51, 33, 35][i % 7],
      upper: [49, 51, 56, 63, 62, 44, 46][i % 7],
      waste: 8 + Math.floor(i % 4),
      
      total: [51, 54, 60, 68, 68, 47, 49][i % 7]
    })),
    Chocolate: Array.from({ length: 7 }, (_, i) => ({
      date: `Jan ${i + 1}`,
      predicted: [59, 62, 68, 68, 67, 53, 56][i % 7],
      lower: [52, 55, 60, 60, 60, 45, 48][i % 7],
      upper: [67, 69, 74, 75, 75, 61, 63][i % 7],
      waste: 11 + Math.floor(i % 4),
      total: [71, 74, 82, 82, 80, 64, 67][i % 7]
    })),
    Eggs: Array.from({ length: 7 }, (_, i) => ({
      date: `Jan ${i + 1}`,
      predicted: [74, 79, 82, 104, 106, 75, 69][i % 7],
      lower: [65, 70, 72, 95, 96, 64, 59][i % 7],
      upper: [84, 89, 92, 115, 116, 85, 79][i % 7],
      waste: 14 + Math.floor(i % 7),
      total: [89, 95, 98, 125, 127, 90, 83][i % 7]
    })),
    Milk: Array.from({ length: 7 }, (_, i) => ({
      date: `Jan ${i + 1}`,
      predicted: [92, 98, 101, 116, 120, 98, 92][i % 7],
      lower: [80, 86, 89, 104, 108, 86, 81][i % 7],
      upper: [103, 110, 113, 128, 131, 109, 104][i % 7],
      waste: 18 + Math.floor(i % 7),
      total: [110, 118, 121, 139, 144, 118, 110][i % 7]
    })),
    'Hot-Dogs': Array.from({ length: 7 }, (_, i) => ({
      date: `Jan ${i + 1}`,
      predicted: [48, 51, 57, 72, 72, 43, 46][i % 7],
      lower: [41, 45, 50, 65, 65, 36, 40][i % 7],
      upper: [55, 59, 64, 79, 78, 50, 53][i % 7],
      waste: 9 + Math.floor(i % 6),
      total: [58, 61, 68, 86, 86, 52, 55][i % 7]
    }))
  };

  const products = [
    { name: 'Strawberries', avgDemand: 47, image: 'https://images.unsplash.com/photo-1543528176-61b239494933?w=400' },
    { name: 'Chocolate', avgDemand: 62, image: 'https://images.unsplash.com/photo-1511381939415-e44015466834?w=400' },
    { name: 'Eggs', avgDemand: 84, image: 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400' },
    { name: 'Milk', avgDemand: 102, image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400' },
    { name: 'Hot-Dogs', avgDemand: 55, image: hotdogImage }
  ];

  const calculateInsights = () => {
    const productCategories = {
      fruits: ['Strawberries'],
      vegetables: [],
      dairy: ['Milk', 'Eggs'],
      food: ['Hot-Dogs', 'Chocolate']
    };
    
    const wasteByCategory = { fruits: 0, vegetables: 0, dairy: 0, food: 0 };
    
    Object.entries(csvData).forEach(([product, data]) => {
      const monthlyWaste = data.reduce((sum, day) => sum + day.waste, 0);
      if (productCategories.fruits.includes(product)) wasteByCategory.fruits += monthlyWaste;
      else if (productCategories.vegetables.includes(product)) wasteByCategory.vegetables += monthlyWaste;
      else if (productCategories.dairy.includes(product)) wasteByCategory.dairy += monthlyWaste;
      else wasteByCategory.food += monthlyWaste;
    });
    
    return [
      {
        title: 'You will save around',
        amount: `3800 ibs`,
        subtitle: 'of strawberries in a year from waste.',
        equivalent: '2.5 months of electricity use for an average American home',
        icon: <Users className="w-8 h-8 text-emerald-500" />,
        bgColor: '#dbeafe'
      },
      {
        title: 'You will save around',
        amount: '2890 dozen',
        subtitle: 'eggs in a year from waste.',
        equivalent: 'driving from New York to Los Angeles 5 times',
        icon: <Box className="w-8 h-8 text-emerald-500" />,
        bgColor: '#d1fae5'
      },
      {
        title: 'You will save around',
        amount: `2300 packs`,
        subtitle: 'of hot-dogs in a year from waste.',
        equivalent: '1.1 million full smartphone charges',
        icon: <Users className="w-8 h-8 text-emerald-500" />,
        bgColor: '#dbeafe'
      },
      {
        title: 'You will save around',
        amount: `5670 gallons`,
        subtitle: 'of milk in a year from waste.',
        equivalent: 'nearly 2 full years of heating and cooling a typical home',
        icon: <Box className="w-8 h-8 text-emerald-500" />,
        bgColor: '#d1fae5'
      }
    ];
  };
  
  const insightsData = calculateInsights();
  
  const getProductColor = (product) => {
    const colors = {
      'Strawberries': { stroke: '#ef4444' },
      'Chocolate': { stroke: '#8b4513' },
      'Eggs': { stroke: '#fbbf24' },
      'Milk': { stroke: '#3b82f6' },
      'Hot-Dogs': { stroke: '#f59e0b' }
    };
    return colors[product] || colors['Milk'];
  };

  // Real data from daily_sales_dataset.csv (aggregated by product)
  const realSalesData = {
    Strawberries: { totalSold: 19100, totalWasted: 3817, wasteRate: 16.7 },
    Chocolate: { totalSold: 29054, totalWasted: 1246, wasteRate: 4.1 },
    Eggs: { totalSold: 38609, totalWasted: 2891, wasteRate: 7.0 },
    Milk: { totalSold: 47031, totalWasted: 5669, wasteRate: 10.8 },
    'Hot-Dogs': { totalSold: 24885, totalWasted: 2315, wasteRate: 8.5 }
  };

  // Convert to chart data format
  const salesChartData = Object.entries(realSalesData).map(([product, data]) => ({
    product,
    sold: data.totalSold,
    wasted: data.totalWasted,
    total: data.totalSold + data.totalWasted,
    wasteRate: data.wasteRate
  }));

  // Pie chart data for waste distribution
  const wastePieData = Object.entries(realSalesData).map(([product, data]) => ({
    name: product,
    value: data.totalWasted,
    color: getProductColor(product).stroke
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const color = getProductColor(selectedProduct).stroke;
      const data = payload[0].payload;
      return (
        <div style={{ 
          backgroundColor: 'white', 
          border: `2px solid ${color}`,
          padding: '12px', 
          borderRadius: '8px', 
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontWeight: '600', color: '#1f2937', marginBottom: '4px' }}>
            {data.date}
          </div>
          <div style={{ color: color, fontWeight: '600' }}>
            Predicted: {data.predicted} units
          </div>
          <div style={{ color: '#7c3aed', fontWeight: '600', marginTop: '4px' }}>
            Usually bought: {data.total} units
          </div>
          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            Range: {data.lower} - {data.upper}
          </div>
        </div>
      );
    }
    return null;
  };

  const Sidebar = () => (
    <div style={{ width: '256px', backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <img 
            src={logoImage} 
            alt="WasteLess Logo" 
            style={{ width: '50px', height: '50px', objectFit: 'contain' }}
          />
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
            <span style={{ color: '#10b981' }}>Waste</span>
            <span style={{ color: '#1f2937' }}>Less</span>
          </h1>
        </div>
      </div>
      
      <nav style={{ marginTop: '24px', flex: 1 }}>
        <div style={{ padding: '0 16px', marginBottom: '8px' }}>
          <div 
            onClick={() => setCurrentPage('dashboard')}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '12px 16px', 
              backgroundColor: currentPage === 'dashboard' ? '#10b981' : 'transparent', 
              color: currentPage === 'dashboard' ? 'white' : '#6b7280', 
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <LayoutDashboard size={20} />
            <span style={{ fontWeight: '500' }}>Dashboard</span>
          </div>
        </div>
        
        <div style={{ padding: '0 16px' }}>
          <div 
            onClick={() => setCurrentPage('products')}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '12px 16px', 
              backgroundColor: currentPage === 'products' ? '#10b981' : 'transparent',
              color: currentPage === 'products' ? 'white' : '#6b7280',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <Package size={20} />
            <span>Products</span>
          </div>
          
          <div 
            onClick={() => setCurrentPage('inventory')}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '12px 16px', 
              backgroundColor: currentPage === 'inventory' ? '#10b981' : 'transparent',
              color: currentPage === 'inventory' ? 'white' : '#6b7280',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <Warehouse size={20} />
            <span>Inventory</span>
          </div>
          
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '12px', 
            padding: '12px 16px', 
            color: '#6b7280',
            borderRadius: '8px',
            cursor: 'pointer'
          }}>
            <Calendar size={20} />
            <span>Calendar</span>
          </div>
          
          <div 
            onClick={() => setIsChatOpen(true)}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '12px 16px', 
              color: isChatOpen ? '#3b82f6' : '#6b7280',
              backgroundColor: isChatOpen ? '#eff6ff' : 'transparent',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              if (!isChatOpen) {
                e.target.style.backgroundColor = '#f3f4f6';
              }
            }}
            onMouseLeave={(e) => {
              if (!isChatOpen) {
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            <MessageSquare size={20} />
            <span>Chat</span>
          </div>
        </div>
      </nav>
      
      <div style={{ padding: '16px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px', 
          padding: '12px 16px', 
          color: '#6b7280',
          borderRadius: '8px',
          cursor: 'pointer'
        }}>
          <Settings size={20} />
          <span>Settings</span>
        </div>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px', 
          padding: '12px 16px', 
          color: '#6b7280',
          borderRadius: '8px',
          cursor: 'pointer'
        }}>
          <LogOut size={20} />
          <span>Logout</span>
        </div>
      </div>
    </div>
  );

  const Header = () => (
    <div style={{ backgroundColor: 'white', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', borderBottom: '1px solid #e5e7eb' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Menu size={24} style={{ color: '#6b7280', cursor: 'pointer' }} />
          <div style={{ position: 'relative' }}>
            <Search size={20} style={{ 
              color: '#9ca3af', 
              position: 'absolute', 
              left: '12px', 
              top: '50%', 
              transform: 'translateY(-50%)'
            }} />
            <input
              type="text"
              placeholder="Search"
              style={{
                paddingLeft: '40px',
                paddingRight: '16px',
                paddingTop: '8px',
                paddingBottom: '8px',
                width: '320px',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                outline: 'none',
                fontSize: '14px'
              }}
            />
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ position: 'relative', cursor: 'pointer' }}>
            <Bell size={24} style={{ color: '#6b7280' }} />
            <span style={{ 
              position: 'absolute', 
              top: '-4px', 
              right: '-4px', 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#ef4444', 
              color: 'white', 
              fontSize: '12px', 
              borderRadius: '50%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontWeight: '600'
            }}>
              3
            </span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <img src="https://flagcdn.com/w40/us.png" alt="US Flag" style={{ width: '32px', height: '24px' }} />
            <span style={{ color: '#6b7280', fontSize: '14px' }}>English</span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
            <img
              src="https://i.pravatar.cc/150?img=47"
              alt="Admin"
              style={{ width: '40px', height: '40px', borderRadius: '50%' }}
            />
            <div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#1f2937' }}>Monir Esc</div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Admin</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const ProductsPage = () => (
    <div style={{ padding: '32px', flex: 1 }}>
      <h2 style={{ fontSize: '30px', fontWeight: 'bold', color: '#1f2937', marginBottom: '32px', marginTop: 0 }}>Products</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {products.map((product, index) => (
          <div 
            key={index} 
            onClick={() => {
              setSelectedProduct(product.name);
              setCurrentPage('dashboard');
            }}
            style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
              overflow: 'hidden',
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
            }}
          >
            <div style={{ position: 'relative', height: '280px', backgroundColor: '#f3f4f6' }}>
              <img 
                src={product.image} 
                alt={product.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </div>
            <div style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937', margin: '0 0 8px 0' }}>
                {product.name}
              </h3>
              <p style={{ fontSize: '16px', color: '#3b82f6', fontWeight: '500', margin: 0 }}>
                Avg: {product.avgDemand} units/day
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const DashboardPage = () => (
    <div style={{ padding: '32px', flex: 1 }}>
      <h2 style={{ fontSize: '30px', fontWeight: 'bold', color: '#1f2937', marginBottom: '32px', marginTop: 0 }}>Dashboard</h2>
      
      <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937', margin: 0 }}>
            Product Demand Forecast: {selectedProduct} - January 2025
          </h3>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setShowProductDropdown(!showProductDropdown)}
                style={{
                  padding: '8px 16px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  color: '#6b7280',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                Products
              </button>
              {showProductDropdown && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '8px',
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                  zIndex: 10,
                  minWidth: '150px'
                }}>
                  {products.map((product) => (
                    <div
                      key={product.name}
                      onClick={() => {
                        setSelectedProduct(product.name);
                        setShowProductDropdown(false);
                      }}
                      style={{
                        padding: '12px 16px',
                        cursor: 'pointer',
                        color: selectedProduct === product.name ? '#10b981' : '#6b7280',
                        fontWeight: selectedProduct === product.name ? '600' : '400',
                        backgroundColor: selectedProduct === product.name ? '#f0fdf4' : 'transparent'
                      }}
                      onMouseEnter={(e) => {
                        if (selectedProduct !== product.name) {
                          e.currentTarget.style.backgroundColor = '#f9fafb';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (selectedProduct !== product.name) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      {product.name}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={csvData[selectedProduct]} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={getProductColor(selectedProduct).stroke} stopOpacity={0.2}/>
                <stop offset="95%" stopColor={getProductColor(selectedProduct).stroke} stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '13px' }}
            />
            <YAxis 
              label={{ value: 'Demand (units)', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
              stroke="#9ca3af"
              style={{ fontSize: '13px' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="upper" 
              stroke="none"
              fill="url(#colorRange)"
            />
            <Area 
              type="monotone" 
              dataKey="lower" 
              stroke="none"
              fill="white"
            />
            <Line 
              type="monotone" 
              dataKey="predicted" 
              stroke={getProductColor(selectedProduct).stroke}
              strokeWidth={3}
              dot={{ fill: getProductColor(selectedProduct).stroke, strokeWidth: 2, r: 5 }}
              activeDot={{ r: 7 }}
            />
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#7c3aed"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ fill: '#7c3aed', strokeWidth: 2, r: 5 }}
              activeDot={{ r: 7 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
        
        <div style={{ marginTop: '16px', display: 'flex', gap: '24px', justifyContent: 'center', fontSize: '14px', color: '#6b7280' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: getProductColor(selectedProduct).stroke, opacity: 0.2, borderRadius: '2px' }}></div>
            <span>Confidence Range</span>
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1f2937', marginBottom: '24px', marginTop: 0 }}>Forecast Insights</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
        {insightsData.map((insight, index) => (
          <div key={index} style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
            padding: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <p style={{ color: '#6b7280', fontSize: '14px', margin: '0 0 8px 0' }}>{insight.title}</p>
                <h4 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1f2937', margin: '0 0 4px 0' }}>{insight.amount}</h4>
                <p style={{ color: '#6b7280', fontSize: '14px', margin: 0 }}>{insight.subtitle}</p>
              </div>
              <div style={{ 
                backgroundColor: insight.bgColor, 
                padding: '12px', 
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {insight.icon}
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontSize: '14px', marginTop: '16px' }}>
              <TrendingUp size={16} />
              <span>{insight.equivalent}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Real Sales Data Visualization */}
      <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1f2937', marginBottom: '24px', marginTop: '48px' }}>
        Real Sales Data Analysis (2024-2025)
      </h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        {/* Products Bought vs Wasted Bar Chart */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
          padding: '24px'
        }}>
          <h4 style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937', marginBottom: '20px', marginTop: 0 }}>
            Products Bought vs Wasted by Product
          </h4>
          
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={salesChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="product" 
                stroke="#9ca3af"
                style={{ fontSize: '12px' }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                stroke="#9ca3af"
                style={{ fontSize: '12px' }}
                label={{ value: 'Units', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
              />
              <Tooltip 
                formatter={(value, name) => [value.toLocaleString(), name === 'sold' ? 'Sold' : 'Wasted']}
                labelFormatter={(label) => `Product: ${label}`}
              />
              <Bar dataKey="sold" fill="#10b981" name="sold" radius={[4, 4, 0, 0]} />
              <Bar dataKey="wasted" fill="#ef4444" name="wasted" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          
          <div style={{ marginTop: '16px', display: 'flex', gap: '24px', justifyContent: 'center', fontSize: '14px', color: '#6b7280' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#10b981', borderRadius: '2px' }}></div>
              <span>Products Sold</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#ef4444', borderRadius: '2px' }}></div>
              <span>Products Wasted</span>
            </div>
          </div>
        </div>

        {/* Waste Distribution Pie Chart */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
          padding: '24px'
        }}>
          <h4 style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937', marginBottom: '20px', marginTop: 0 }}>
            Waste Distribution by Product
          </h4>
          
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={wastePieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {wastePieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [value.toLocaleString() + ' units', 'Wasted']}
                labelFormatter={(label) => `Product: ${label}`}
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '12px' }}>
            {wastePieData.map((item, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '12px', height: '12px', backgroundColor: item.color, borderRadius: '2px' }}></div>
                <span style={{ color: '#6b7280' }}>{item.name}: {item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f9fafb', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <Sidebar />
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        <Header />
        {currentPage === 'dashboard' ? <DashboardPage /> : currentPage === 'products' ? <ProductsPage /> : <StoreInventory />}
      </div>
      
      {/* Chat Drawer Overlay */}
      {isChatOpen && (
        <>
          {/* Backdrop */}
          <div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              zIndex: 998,
              transition: 'opacity 0.3s ease'
            }}
            onClick={() => setIsChatOpen(false)}
          />
          
          {/* Chat Drawer */}
          <div
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              height: '100vh',
              width: '450px',
              backgroundColor: 'white',
              boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.15)',
              zIndex: 999,
              transform: isChatOpen ? 'translateX(0)' : 'translateX(100%)',
              transition: 'transform 0.3s ease',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {/* Chat Header */}
            <div
              style={{
                padding: '20px',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: '#f8fafc'
              }}
            >
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>
                WasteLess Assistant
              </h3>
              <button
                onClick={() => setIsChatOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#6b7280',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#f3f4f6'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                <X size={20} />
              </button>
            </div>
            
            {/* Chat Content */}
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <Chat />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default WasteLess;
