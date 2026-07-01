# UPI Fraud Detection System

A comprehensive real-time fraud detection system for UPI transactions using ensemble machine learning, graph neural networks, and explainable AI.

## Features

- **Multi-model Ensemble Detection**: Combines XGBoost, LightGBM, and other ML models for robust fraud detection
- **Graph Neural Networks**: Identifies network-based fraud patterns and collusion
- **Explainable AI**: Provides clear reasoning for fraud alerts
- **Real-time Processing**: Fast detection for transactions above ₹10,000
- **Scalable Architecture**: Docker-based deployment with monitoring support
- **Interactive Dashboard**: Visual analytics and fraud pattern visualization

## System Requirements

### Hardware
- Processor: Intel Core i5 or higher
- RAM: Minimum 8 GB
- Storage: Minimum 500 GB HDD or 256 GB SSD
- GPU: NVIDIA GPU with CUDA support (optional, for GNN acceleration)

### Software
- Python 3.9+
- Docker & Docker Compose (for deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "UPI Fraud Detection Final"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode

1. Start the backend:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open the frontend:
```bash
# Open frontend/index.html in a web browser
# Or serve using a simple HTTP server:
cd frontend
python -m http.server 8080
```

### Docker Deployment

```bash
docker-compose up --build
```

The application will be available at:
- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:8080
- API Documentation: http://localhost:8000/docs

## API Endpoints

- `POST /api/v1/transaction/analyze` - Analyze a transaction for fraud
- `GET /api/v1/transaction/{transaction_id}` - Get transaction details
- `GET /api/v1/explain/{transaction_id}` - Get explainability report
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/graph/network` - Get fraud network visualization data

## Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # ML models and ensemble
│   ├── gnn/                    # Graph Neural Network components
│   ├── rules/                  # Rule engine
│   ├── explainability/         # Explainable AI module
│   ├── api/                    # API routes
│   └── utils/                  # Utility functions
├── frontend/
│   ├── index.html             # Main dashboard
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── assets/                # Static assets
├── data/                      # Data storage and models
├── tests/                     # Unit tests
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Docker image definition
└── requirements.txt           # Python dependencies
```

## Usage Example

### Python API Client

```python
import requests

# Analyze a transaction
response = requests.post('http://localhost:8000/api/v1/transaction/analyze', json={
    "transaction_id": "TXN123456",
    "amount": 15000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T10:30:00",
    "device_id": "DEVICE123",
    "location": "Mumbai"
})

result = response.json()
print(f"Fraud Score: {result['fraud_score']}")
print(f"Is Fraud: {result['is_fraud']}")
print(f"Reasons: {result['reasons']}")
print(f"Recommendation: {result['recommendation']}")
```

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/transaction/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "amount": 15000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T10:30:00",
    "device_id": "DEVICE123",
    "location": "Mumbai"
  }'
```

## Training Models

To train the ensemble models with sample data:

```bash
python scripts/train_models.py
```

This will generate sample training data and train the ensemble model. In production, you should train with your actual historical transaction data.

## License

MIT License

