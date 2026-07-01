# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) Docker and Docker Compose

## Installation Steps

### Option 1: Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create data directory:**
   ```bash
   mkdir -p data/models
   ```

3. **Train models (optional, for better accuracy):**
   ```bash
   python scripts/train_models.py
   ```

4. **Start the server:**
   ```bash
   python run.py
   ```
   Or:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the application:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/frontend/index.html

### Option 2: Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/frontend/index.html

## Testing the System

### 1. Test with a Legitimate Transaction

```bash
curl -X POST "http://localhost:8000/api/v1/transaction/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN001",
    "amount": 15000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T14:30:00",
    "device_id": "DEVICE123",
    "location": "Mumbai"
  }'
```

### 2. Test with a Suspicious Transaction

```bash
curl -X POST "http://localhost:8000/api/v1/transaction/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN002",
    "amount": 100000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T03:30:00",
    "device_id": "",
    "location": ""
  }'
```

### 3. View Dashboard

Open your browser and navigate to:
```
http://localhost:8000/frontend/index.html
```

## API Endpoints

- `POST /api/v1/transaction/analyze` - Analyze a transaction
- `GET /api/v1/transaction/{transaction_id}` - Get transaction explanation
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/graph/network` - Get fraud network graph data
- `GET /health` - Health check

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, change it in `app/config.py` or set the `PORT` environment variable.

### Model Not Found
The system will use default initialized models if trained models are not found. For better accuracy, run:
```bash
python scripts/train_models.py
```

### Frontend Not Loading
Make sure the `frontend` directory exists and contains `index.html`, `css/style.css`, and `js/dashboard.js`.

### Database Errors
The system uses SQLite by default. Make sure the `data` directory exists and is writable.

## Next Steps

1. Train models with your actual transaction data
2. Adjust fraud threshold in `app/config.py` based on your requirements
3. Customize rules in `app/rules/rule_engine.py`
4. Configure monitoring tools (Prometheus/Grafana) for production
5. Set up proper authentication and authorization
6. Configure CORS origins for production deployment



