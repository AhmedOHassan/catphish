# Running Catphish with Audit Trail Locally

This guide will help you run the complete Catphish system locally, including the new audit trail feature.

## Prerequisites

- Docker and Docker Compose (for Valkey)
- Python 3.12+
- Node.js 18+ and npm
- Git

## Quick Start (Recommended)

### 1. Start Valkey Database

```bash
cd /path/to/catphish
docker compose up -d
```

This starts Valkey (Redis-compatible) on `localhost:6379`.

### 2. Seed Demo Data

```bash
./scripts/seed-valkey.sh
```

This creates:
- Demo tenant: `t_demo` with API key: `demo_key_123`
- Test users with voice embeddings

### 3. Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Start Backend API (Terminal 1)

From the project root:

```bash
cd catphish-api/server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🐟 CATPHISH API STARTING UP
🐟 Valkey: 127.0.0.1:6379
✅ Valkey connection: OK
```

The API will be available at: `http://localhost:8000`

### 5. Start Frontend (Terminal 2)

From the project root:

```bash
cd catphish-api
npm install  # First time only
npm run dev -- --port 3001
```

The frontend will be available at: `http://localhost:3001`

## Accessing the Audit Trail

Once both backend and frontend are running:

1. **Visit the Audit Page**: Navigate to `http://localhost:3001/audit`
2. **View Verification Events**: The page will display all verification events stored in Valkey
3. **Interact with Features**:
   - Click 📋 to copy Solana transaction hashes
   - Click 🔗 to view transactions on Solana Explorer
   - View color-coded status badges (green=verified, red=failed)

## Testing the Full Flow

### Option A: Using the Verification Frontend

1. Visit `http://localhost:3000` (demo website)
2. Sign up and complete voice verification
3. After verification, a Solana transaction is created and stored
4. Visit `http://localhost:3001/audit` to see the new audit event

### Option B: Using API Directly

#### Create a Verification Session
```bash
curl -X POST http://localhost:8000/v1/verification-sessions \
  -H "Content-Type: application/json" \
  -H "X-Catphish-Key: demo_key_123" \
  -d '{
    "external_user_id": "test_user_001",
    "return_url": "http://localhost:3000"
  }'
```

Response includes `session_id` and `verification_url`.

#### Complete Verification
Use the verification URL to record audio and complete verification through the UI.

#### View Audit Events
```bash
curl http://localhost:8000/v1/audit/events \
  -H "X-Catphish-Key: demo_key_123"
```

Or visit: `http://localhost:3001/audit`

## API Endpoints

### Backend (port 8000)

- `GET /health` - Health check
- `POST /v1/verification-sessions` - Create verification session
- `GET /v1/verification-sessions/{session_id}` - Get session info
- `GET /v1/session/{session_id}/status` - Get session status
- `POST /v1/session/{session_id}/enroll` - Enroll new user
- `POST /v1/session/{session_id}/verify` - Verify returning user
- **`GET /v1/audit/events`** - Get audit trail (NEW)
  - Query params: `external_user_id` (optional), `limit` (optional)
  - Requires: `X-Catphish-Key` header

### Frontend (port 3001)

- `/` - Verification page
- `/verify` - Verification page (with session_id param)
- `/success` - Success page
- `/failure` - Failure page
- **`/audit`** - Audit trail page (NEW)

## Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Valkey
VALKEY_HOST=127.0.0.1
VALKEY_PORT=6379

# Solana (optional - for actual blockchain submission)
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PRIVATE_KEY=<your_base58_key>

# Frontend URL
CATPHISH_FRONTEND_URL=http://localhost:3001
```

**Note**: Solana integration works without the private key - it will just log warnings and store events with `null` transaction hashes.

## Troubleshooting

### Valkey Connection Issues

```bash
# Check if Valkey is running
docker ps | grep valkey

# Check Valkey logs
docker logs catphish-valkey

# Test connection
docker exec -it catphish-valkey valkey-cli PING
```

### Backend Won't Start

```bash
# Check Python dependencies
pip list | grep -E "(fastapi|uvicorn|redis)"

# Reinstall if needed
pip install fastapi uvicorn redis python-dotenv pydantic
```

### Frontend Won't Start

```bash
# Clear node_modules and reinstall
cd catphish-api
rm -rf node_modules package-lock.json
npm install
```

### No Audit Events Showing

1. Make sure you've completed at least one verification
2. Check backend logs for any errors during audit storage
3. Test API directly: `curl -H "X-Catphish-Key: demo_key_123" http://localhost:8000/v1/audit/events`

## Creating Test Audit Data

You can manually create test audit events using Python:

```python
import sys
sys.path.insert(0, 'catphish-api/server')

from db.valkey_store import ValkeyStore

store = ValkeyStore(host="127.0.0.1", port=6379)

# Create test event
store.create_audit_event(
    tenant_id="t_demo",
    external_user_id="test_user_123",
    challenge_id="ch_test_001",
    result_status="verified",
    confidence_score=0.92,
    solana_tx_hash="4jH8TestHashABC123XYZ",
)

print("Test audit event created!")
```

## Viewing the Audit UI

The audit trail page features:

- **Dark/Noir Theme**: Matches the existing Catphish design
- **Table View**: Shows all verification events
- **Sortable**: Events displayed newest-first
- **Interactive**: Copy hashes and view on Solana Explorer
- **Status Indicators**: Color-coded badges for verification results
- **Responsive**: Works on desktop and mobile

### Screenshot

The audit page displays:
1. Header with blockchain messaging
2. Table with columns: User, Timestamp, Result, Confidence, Solana Hash
3. Action buttons for each hash (copy/explore)
4. Footer explaining immutability

## Architecture Overview

```
User → Demo Website (3000) → Backend API (8000) → Valkey
                                    ↓
                               Solana Devnet
                                    ↓
                            Audit Storage (Valkey)
                                    ↓
Admin → Audit Page (3001) → Backend API (8000) → Valkey
```

## Production Deployment

For production:

1. Set up proper Solana keypair with `SOLANA_PRIVATE_KEY`
2. Use production Solana RPC URL
3. Configure authentication for audit page access
4. Set up proper environment variables
5. Use a production-ready database (Redis/Valkey cluster)

## Additional Resources

- [AUDIT_TRAIL_IMPLEMENTATION.md](./AUDIT_TRAIL_IMPLEMENTATION.md) - Technical implementation details
- [README.md](./README.md) - Main project documentation
- [INTEGRATION_FLOW.md](./INTEGRATION_FLOW.md) - Integration guide

## Support

If you encounter issues:
1. Check that all services are running (`docker ps`, backend logs, frontend logs)
2. Verify Valkey is accessible and seeded with demo data
3. Check browser console for frontend errors
4. Review backend logs for API errors
