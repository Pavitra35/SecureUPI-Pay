"""Setup script for the UPI Fraud Detection System."""
from setuptools import setup, find_packages

setup(
    name="upi-fraud-detection",
    version="1.0.0",
    description="Real-time UPI fraud detection system using ensemble ML and GNN",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "scikit-learn>=1.3.2",
        "xgboost>=2.0.2",
        "lightgbm>=4.1.0",
        "torch>=2.1.1",
        "torch-geometric>=2.4.0",
        "pandas>=2.1.3",
        "numpy>=1.24.3",
    ],
    python_requires=">=3.9",
)



