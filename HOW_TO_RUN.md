# How to Run the UPI Fraud Detection System

## 🚀 Quick Start (Easiest Method)

### Step 1: Open Terminal/Command Prompt
- **Windows**: Press `Win + R`, type `cmd` or `powershell`, press Enter
- **Mac/Linux**: Open Terminal

### Step 2: Navigate to Project Directory
```bash
cd "C:\Users\kudri\OneDrive\Desktop\UPI Fraud Detection Final"
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If you get permission errors, use:
```bash
pip install --user -r requirements.txt
```

### Step 4: Create Data Directory (if not exists)
```bash
mkdir data\models
```

### Step 5: Start the Server
```bash
python run.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Open in Browser
Open your web browser and go to:
- **Dashboard**: http://localhost:8000/frontend/index.html
- **API Documentation**: http://localhost:8000/docs
- **Home Page**: http://localhost:8000

---

## 📋 Detailed Instructions

### Prerequisites Check

1. **Check Python Version**:
   ```bash
   python --version
   ```
   Should be Python 3.9 or higher. If not, install Python from python.org

2. **Check pip**:
   ```bash
   pip --version
   ```

### Installation Options

#### Option A: Standard Installation (Recommended)

1. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```

#### Option B: Using Uvicorn Directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: Docker (If you have Docker installed)

```bash
docker-compose up --build
```

---

## 🧪 Testing the Application

### Method 1: Using the Web Dashboard

1. Open http://localhost:8000/frontend/index.html
2. Fill in the transaction form:
   - Transaction ID: `TXN001`
   - Amount: `15000` (minimum ₹10,000)
   - Sender UPI: `user@paytm`
   - Receiver UPI: `merchant@upi`
   - Timestamp: Use current date/time
   - Device ID: `DEVICE123` (optional)
   - Location: `Mumbai` (optional)
3. Click "Analyze Transaction"
4. View the results and fraud score

### Method 2: Using API (PowerShell)

```powershell
$body = @{
    transaction_id = "TXN001"
    amount = 15000
    sender_upi = "user@paytm"
    receiver_upi = "merchant@upi"
    timestamp = "2024-01-15T14:30:00"
    device_id = "DEVICE123"
    location = "Mumbai"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transaction/analyze" -Method Post -Body $body -ContentType "application/json"
```

### Method 3: Using Python

Create a file `test_api.py`:
```python
import requests

response = requests.post('http://localhost:8000/api/v1/transaction/analyze', json={
    "transaction_id": "TXN001",
    "amount": 15000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T14:30:00",
    "device_id": "DEVICE123",
    "location": "Mumbai"
})

print(response.json())
```

Run it:
```bash
python test_api.py
```

---

## 🔧 Troubleshooting

### Problem: "Module not found" errors

**Solution**: Install missing packages
```bash
pip install fastapi uvicorn scikit-learn xgboost lightgbm torch pandas numpy
```

### Problem: Port 8000 already in use

**Solution 1**: Change the port in `app/config.py`:
```python
PORT: int = 8001  # Change to different port
```

**Solution 2**: Kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill
```

### Problem: "Permission denied" errors

**Solution**: Use `--user` flag:
```bash
pip install --user -r requirements.txt
```

### Problem: Frontend not loading

**Solution**: Make sure you're accessing:
- http://localhost:8000/frontend/index.html
- NOT http://localhost:8000/index.html

### Problem: Database errors

**Solution**: Create the data directory:
```bash
mkdir data
mkdir data\models
```

### Problem: Models not found

**Solution**: The system will work with default models. For better accuracy, train models:
```bash
python scripts/train_models.py
```

---

## 📊 What You Should See

### When Server Starts Successfully:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12346] using WatchFiles
```

### In Browser (Dashboard):
- A modern dashboard with statistics cards
- Transaction analysis form
- Charts and visualizations
- Recent fraudulent transactions table

### In Browser (API Docs):
- Interactive API documentation at http://localhost:8000/docs
- Try out endpoints directly from the browser

---

## 🎯 Quick Test Transaction

Try analyzing this suspicious transaction:

```json
{
    "transaction_id": "TXN_SUSPICIOUS",
    "amount": 100000,
    "sender_upi": "user@paytm",
    "receiver_upi": "merchant@upi",
    "timestamp": "2024-01-15T03:30:00",
    "device_id": "",
    "location": ""
}
```

This should trigger fraud detection because:
- High amount (₹1,00,000)
- Unusual hour (3:30 AM)
- Missing device ID and location

---

## 🛑 Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## 📝 Next Steps After Running

1. **Train Models** (for better accuracy):
   ```bash
   python scripts/train_models.py
   ```

2. **Explore the Dashboard**: 
   - Analyze different transactions
   - View explanations
   - Check network graphs

3. **Read API Documentation**: 
   - Visit http://localhost:8000/docs
   - Try out different endpoints

4. **Customize Settings**:
   - Edit `app/config.py` to adjust fraud threshold
   - Modify rules in `app/rules/rule_engine.py`

---

## 💡 Tips

- Keep the terminal window open while using the application
- The server auto-reloads when you change code (if using `--reload`)
- Check the terminal for any error messages
- Use the health endpoint to verify server is running: http://localhost:8000/health



