# Project Structure

```
UPI Fraud Detection Final/
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration settings
│   │
│   ├── api/                      # API routes and schemas
│   │   ├── __init__.py
│   │   ├── routes.py             # API endpoints
│   │   └── schemas.py            # Pydantic models for requests/responses
│   │
│   ├── models/                   # Machine Learning models
│   │   ├── __init__.py
│   │   ├── feature_engineering.py  # Feature extraction
│   │   └── ensemble_model.py       # Ensemble ML model (XGBoost, LightGBM, RF)
│   │
│   ├── gnn/                      # Graph Neural Network module
│   │   ├── __init__.py
│   │   └── fraud_graph.py        # GNN for network-based fraud detection
│   │
│   ├── rules/                    # Rule engine
│   │   ├── __init__.py
│   │   └── rule_engine.py        # Rule-based fraud detection
│   │
│   ├── explainability/           # Explainable AI
│   │   ├── __init__.py
│   │   └── explainer.py         # Fraud detection explanations
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── database.py          # Database operations
│
├── frontend/                     # Frontend dashboard
│   ├── index.html               # Main dashboard page
│   ├── css/
│   │   └── style.css           # Stylesheets
│   └── js/
│       └── dashboard.js        # Dashboard JavaScript
│
├── scripts/                      # Utility scripts
│   ├── __init__.py
│   └── train_models.py         # Model training script
│
├── data/                        # Data storage
│   └── models/                 # Trained model files
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── setup.py                    # Package setup script
├── run.py                      # Application runner script
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
└── PROJECT_STRUCTURE.md        # This file
```

## Key Components

### Backend (FastAPI)
- **Main Application** (`app/main.py`): FastAPI app with CORS, static file serving
- **API Routes** (`app/api/routes.py`): Transaction analysis, explanations, dashboard stats
- **ML Models** (`app/models/`): Ensemble model combining XGBoost, LightGBM, Random Forest
- **GNN Module** (`app/gnn/`): Graph Neural Network for network-based fraud detection
- **Rule Engine** (`app/rules/`): Rule-based validation and fraud checks
- **Explainability** (`app/explainability/`): Provides detailed explanations for fraud decisions

### Frontend (HTML/CSS/JavaScript)
- **Dashboard** (`frontend/index.html`): Interactive web interface
- **Visualizations**: Charts using Chart.js and Plotly
- **Real-time Updates**: Auto-refresh every 30 seconds

### Infrastructure
- **Docker**: Containerized deployment
- **Database**: SQLite for transaction storage
- **Configuration**: Environment-based settings

## Data Flow

1. **Transaction Input** → API receives transaction data
2. **Feature Engineering** → Extract features from transaction
3. **ML Prediction** → Ensemble model predicts fraud probability
4. **GNN Analysis** → Network-based pattern detection
5. **Rule Engine** → Rule-based validation
6. **Combination** → Weighted combination of all scores
7. **Explanation** → Generate detailed explanation
8. **Response** → Return fraud score, status, and reasons

## Model Architecture

### Ensemble Model
- **XGBoost** (40% weight): Gradient boosting
- **LightGBM** (40% weight): Light gradient boosting
- **Random Forest** (20% weight): Ensemble of decision trees

### Graph Neural Network
- **GCN Layers**: Graph convolutional networks
- **GAT Layer**: Graph attention mechanism
- **Network Analysis**: Detects fraud rings and collusion

### Rule Engine
- Minimum amount check
- High amount threshold
- Rapid transaction detection
- Unusual hours check
- Same sender-receiver check
- Missing device info check
- Amount rounding check



