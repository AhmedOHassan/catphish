import React, { useState, useEffect } from 'react';
import './AuditPage.css';

// TODO: In production, this should come from secure configuration or user authentication
const DEMO_API_KEY = import.meta.env.VITE_CATPHISH_API_KEY || 'demo_key_123';
const API_BASE = import.meta.env.VITE_CATPHISH_API_URL || '';

function AuditPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(null);

  useEffect(() => {
    fetchAuditEvents();
  }, []);

  const fetchAuditEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE}/v1/audit/events?limit=100`, {
        headers: {
          'X-Catphish-Key': DEMO_API_KEY,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch audit events: ${response.status}`);
      }

      const data = await response.json();
      setEvents(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching audit events:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const truncateHash = (hash) => {
    if (!hash) return 'N/A';
    if (hash.length <= 16) return hash;
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  };

  const getSolanaExplorerUrl = (hash, cluster = 'devnet') => {
    if (!hash) return null;
    return `https://explorer.solana.com/tx/${hash}?cluster=${cluster}`;
  };

  const getStatusBadgeClass = (status) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return 'audit-status-badge audit-status-verified';
      case 'failed':
        return 'audit-status-badge audit-status-failed';
      default:
        return 'audit-status-badge audit-status-unknown';
    }
  };

  return (
    <div className="audit-page">
      <div className="audit-container">
        <header className="audit-header">
          <div className="audit-header-content">
            <span className="audit-kicker">BLOCKCHAIN AUDIT TRAIL</span>
            <h1 className="audit-title">Verification Events</h1>
            <p className="audit-subtitle">
              Each verification event is anchored on Solana, creating an immutable 
              audit trail for compliance and fraud investigation.
            </p>
          </div>
        </header>

        {error && (
          <div className="audit-error">
            <p>❌ {error}</p>
            <button onClick={fetchAuditEvents} className="audit-retry-btn">
              Retry
            </button>
          </div>
        )}

        {loading ? (
          <div className="audit-loading">
            <div className="audit-spinner"></div>
            <p>Loading audit trail...</p>
          </div>
        ) : events.length === 0 ? (
          <div className="audit-empty">
            <p>No verification events recorded yet.</p>
            <p className="audit-empty-hint">
              Verification events will appear here after users complete voice verification.
            </p>
          </div>
        ) : (
          <div className="audit-table-wrapper">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Timestamp</th>
                  <th>Result</th>
                  <th>Confidence</th>
                  <th>Solana Hash</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.challenge_id || `${event.external_user_id}-${event.timestamp}`} className="audit-row">
                    <td className="audit-cell-user">
                      <code>{event.external_user_id}</code>
                    </td>
                    <td className="audit-cell-timestamp">
                      {formatTimestamp(event.timestamp)}
                    </td>
                    <td className="audit-cell-status">
                      <span className={getStatusBadgeClass(event.result_status)}>
                        {event.result_status === 'verified' ? '✓ ' : '✗ '}
                        {event.result_status}
                      </span>
                    </td>
                    <td className="audit-cell-confidence">
                      {((event.confidence_score || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="audit-cell-hash">
                      {event.solana_tx_hash ? (
                        <div className="audit-hash-actions">
                          <code className="audit-hash-code">
                            {truncateHash(event.solana_tx_hash)}
                          </code>
                          <button
                            className="audit-btn audit-btn-copy"
                            onClick={() => copyToClipboard(event.solana_tx_hash, event.challenge_id || event.timestamp)}
                            title="Copy full hash"
                          >
                            {copied === (event.challenge_id || event.timestamp) ? '✓' : '📋'}
                          </button>
                          <a
                            href={getSolanaExplorerUrl(event.solana_tx_hash)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="audit-btn audit-btn-explorer"
                            title="View on Solana Explorer"
                          >
                            🔗
                          </a>
                        </div>
                      ) : (
                        <span className="audit-hash-null">No TX</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <footer className="audit-footer">
          <p>
            <strong>Immutability:</strong> Transaction hashes are cryptographically 
            secured on Solana blockchain and cannot be altered or deleted.
          </p>
        </footer>
      </div>
    </div>
  );
}

export default AuditPage;
