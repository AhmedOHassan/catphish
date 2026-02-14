import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, logout } from '../services/authService';
import Navbar from '../components/Navbar';

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const currentUser = getCurrentUser();
    if (!currentUser) {
      navigate('/');
      return;
    }
    setUser(currentUser);
  }, [navigate]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  // Fake banking data
  const balance = '$12,543.87';
  const transactions = [
    { id: 1, name: 'Starbucks Coffee', amount: '-$5.67', date: '2026-02-14', type: 'debit' },
    { id: 2, name: 'Direct Deposit', amount: '+$2,500.00', date: '2026-02-13', type: 'credit' },
    { id: 3, name: 'Amazon Purchase', amount: '-$89.32', date: '2026-02-12', type: 'debit' },
    { id: 4, name: 'Netflix Subscription', amount: '-$15.99', date: '2026-02-11', type: 'debit' },
    { id: 5, name: 'Refund - Store Credit', amount: '+$42.00', date: '2026-02-10', type: 'credit' },
  ];

  return (
    <div className="dashboard-page">
      <Navbar 
        isLoggedIn={true}
        userEmail={user.email}
        onLogout={handleLogout}
      />

      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Welcome back, {user.email}</h1>
          <p className="welcome-subtitle">Your account overview</p>
        </div>

        {/* Balance Card */}
        <div className="balance-card">
          <div className="balance-label">Total Balance</div>
          <div className="balance-amount">{balance}</div>
          <div className="balance-buttons">
            <button className="btn-secondary">Transfer</button>
            <button className="btn-secondary">Deposit</button>
            <button className="btn-secondary">Withdraw</button>
          </div>
        </div>

        {/* Transactions */}
        <div className="transactions-section">
          <h2>Recent Transactions</h2>
          <div className="transactions-list">
            {transactions.map(transaction => (
              <div key={transaction.id} className="transaction-item">
                <div className="transaction-info">
                  <div className="transaction-name">{transaction.name}</div>
                  <div className="transaction-date">{transaction.date}</div>
                </div>
                <div className={`transaction-amount ${transaction.type}`}>
                  {transaction.amount}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            <div className="action-card">
              <span className="action-icon">💳</span>
              <span className="action-label">Pay Bills</span>
            </div>
            <div className="action-card">
              <span className="action-icon">📊</span>
              <span className="action-label">View Statements</span>
            </div>
            <div className="action-card">
              <span className="action-icon">⚙️</span>
              <span className="action-label">Settings</span>
            </div>
            <div className="action-card">
              <span className="action-icon">💬</span>
              <span className="action-label">Support</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
