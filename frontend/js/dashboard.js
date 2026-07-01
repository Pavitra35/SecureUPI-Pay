// Dashboard JavaScript
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    loadDashboardStats();
    setDefaultTimestamp();
});

function initializeDashboard() {
    console.log('Dashboard initialized');
}

function setupEventListeners() {
    document.getElementById('analyzeBtn').addEventListener('click', analyzeTransaction);
    document.getElementById('refreshBtn').addEventListener('click', loadDashboardStats);
    document.getElementById('explainBtn').addEventListener('click', showExplanation);
    document.querySelector('.close').addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('explanationModal');
        if (event.target === modal) {
            closeModal();
        }
    });
}

function setDefaultTimestamp() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('timestamp').value = now.toISOString().slice(0, 16);
}

async function analyzeTransaction() {
    const transactionData = {
        transaction_id: document.getElementById('transactionId').value,
        amount: parseFloat(document.getElementById('amount').value),
        sender_upi: document.getElementById('senderUpi').value,
        receiver_upi: document.getElementById('receiverUpi').value,
        timestamp: new Date(document.getElementById('timestamp').value).toISOString(),
        device_id: document.getElementById('deviceId').value || null,
        location: document.getElementById('location').value || null
    };
    
    // Validate
    if (!transactionData.transaction_id || !transactionData.amount || 
        !transactionData.sender_upi || !transactionData.receiver_upi) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (transactionData.amount < 10000) {
        alert('Transaction amount must be at least ₹10,000');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/transaction/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transactionData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayResults(result);
        loadDashboardStats(); // Refresh stats
        
    } catch (error) {
        console.error('Error analyzing transaction:', error);
        alert('Error analyzing transaction. Please check if the backend server is running.');
    }
}

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');
    
    // Update fraud score
    const fraudScore = (result.fraud_score * 100).toFixed(1);
    document.getElementById('fraudScoreValue').textContent = `${fraudScore}%`;
    
    const scoreCircle = document.getElementById('fraudScoreCircle');
    scoreCircle.className = 'score-circle';
    if (result.fraud_score >= 0.7) {
        scoreCircle.classList.add('high-risk');
        document.getElementById('fraudStatus').textContent = 'FRAUD DETECTED';
        document.getElementById('fraudStatus').style.color = '#ff6b6b';
    } else if (result.fraud_score >= 0.5) {
        scoreCircle.classList.add('medium-risk');
        document.getElementById('fraudStatus').textContent = 'SUSPICIOUS';
        document.getElementById('fraudStatus').style.color = '#feca57';
    } else {
        scoreCircle.classList.add('low-risk');
        document.getElementById('fraudStatus').textContent = 'LEGITIMATE';
        document.getElementById('fraudStatus').style.color = '#48dbfb';
    }
    
    // Update model scores
    document.getElementById('mlScore').textContent = result.ml_score.toFixed(3);
    document.getElementById('gnnScore').textContent = result.gnn_score.toFixed(3);
    document.getElementById('ruleScore').textContent = result.rule_score.toFixed(3);
    
    // Update recommendation
    const recommendationEl = document.getElementById('recommendation');
    recommendationEl.textContent = result.recommendation;
    recommendationEl.className = 'recommendation-text ' + result.recommendation.toLowerCase();
    
    // Update reasons
    const reasonsList = document.getElementById('reasonsList');
    reasonsList.innerHTML = '';
    result.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.textContent = reason;
        reasonsList.appendChild(li);
    });
    
    // Store result for explanation
    window.lastResult = result;
    window.lastTransactionId = result.transaction_id;
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

async function showExplanation() {
    if (!window.lastTransactionId) {
        alert('Please analyze a transaction first');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/transaction/${window.lastTransactionId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const explanation = await response.json();
        displayExplanation(explanation);
        
    } catch (error) {
        console.error('Error fetching explanation:', error);
        alert('Error fetching explanation. Please try again.');
    }
}

function displayExplanation(explanation) {
    const content = document.getElementById('explanationContent');
    content.innerHTML = `
        <div class="explanation-section">
            <h4>Overall Assessment</h4>
            <p><strong>Fraud Score:</strong> ${(explanation.overall_fraud_score * 100).toFixed(2)}%</p>
            <p><strong>Status:</strong> ${explanation.is_fraud ? 'FRAUD DETECTED' : 'LEGITIMATE'}</p>
            <p><strong>Recommendation:</strong> ${explanation.recommendation}</p>
        </div>
        
        <div class="explanation-section">
            <h4>ML Model Analysis</h4>
            <p><strong>Fraud Score:</strong> ${(explanation.explanations.ml_model.fraud_score * 100).toFixed(2)}%</p>
            <p><strong>Confidence:</strong> ${explanation.explanations.ml_model.confidence}</p>
            <p>${explanation.explanations.ml_model.reason}</p>
            ${explanation.explanations.ml_model.model_contributions ? `
                <h5>Model Contributions:</h5>
                <ul>
                    ${Object.entries(explanation.explanations.ml_model.model_contributions).map(([name, data]) => 
                        `<li>${name}: ${(data.score * 100).toFixed(2)}% (${data.contribution})</li>`
                    ).join('')}
                </ul>
            ` : ''}
        </div>
        
        <div class="explanation-section">
            <h4>Network Analysis (GNN)</h4>
            <p><strong>Network Risk:</strong> ${explanation.explanations.gnn_analysis.network_risk_level}</p>
            <p><strong>Connected Entities:</strong> ${explanation.explanations.gnn_analysis.connected_entities}</p>
            <p>${explanation.explanations.gnn_analysis.interpretation}</p>
            ${explanation.explanations.gnn_analysis.reasons.length > 0 ? `
                <h5>Reasons:</h5>
                <ul>
                    ${explanation.explanations.gnn_analysis.reasons.map(r => `<li>${r}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
        
        <div class="explanation-section">
            <h4>Rule Engine Analysis</h4>
            <p><strong>Violations:</strong> ${explanation.explanations.rule_engine.violation_count}</p>
            <p><strong>Risk Score:</strong> ${(explanation.explanations.rule_engine.risk_score * 100).toFixed(2)}%</p>
            <p>${explanation.explanations.rule_engine.summary}</p>
            ${explanation.explanations.rule_engine.violations.length > 0 ? `
                <h5>Violations:</h5>
                <ul>
                    ${explanation.explanations.rule_engine.violations.map(v => 
                        `<li><strong>${v.rule}</strong> (${v.severity}): ${v.message}</li>`
                    ).join('')}
                </ul>
            ` : ''}
        </div>
        
        <div class="explanation-section">
            <h4>Key Factors</h4>
            <ul class="key-factors">
                ${explanation.explanations.key_factors.map(factor => `<li>${factor}</li>`).join('')}
            </ul>
        </div>
    `;
    
    document.getElementById('explanationModal').classList.add('show');
}

function closeModal() {
    document.getElementById('explanationModal').classList.remove('show');
}

async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        updateStats(stats);
        updateFraudsTable(stats.recent_frauds);
        updateCharts(stats);
        loadNetworkGraph();
        
        document.getElementById('lastUpdate').textContent = 
            `Last updated: ${new Date().toLocaleTimeString()}`;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        // Don't show alert on page load
    }
}

function updateStats(stats) {
    document.getElementById('totalTransactions').textContent = stats.total_transactions.toLocaleString();
    document.getElementById('fraudTransactions').textContent = stats.fraud_transactions.toLocaleString();
    document.getElementById('fraudRate').textContent = `${stats.fraud_rate.toFixed(2)}%`;
    document.getElementById('totalAmount').textContent = `₹${stats.total_amount.toLocaleString('en-IN')}`;
}

function updateFraudsTable(frauds) {
    const tbody = document.getElementById('fraudsTableBody');
    tbody.innerHTML = '';
    
    if (frauds.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No fraudulent transactions found</td></tr>';
        return;
    }
    
    frauds.forEach(fraud => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${fraud.transaction_id}</td>
            <td>₹${fraud.amount.toLocaleString('en-IN')}</td>
            <td>${fraud.sender_upi.substring(0, 20)}${fraud.sender_upi.length > 20 ? '...' : ''}</td>
            <td>${fraud.receiver_upi.substring(0, 20)}${fraud.receiver_upi.length > 20 ? '...' : ''}</td>
            <td><span style="color: ${fraud.fraud_score >= 0.7 ? '#ff6b6b' : '#feca57'}">${(fraud.fraud_score * 100).toFixed(1)}%</span></td>
            <td>${fraud.timestamp ? new Date(fraud.timestamp).toLocaleString() : 'N/A'}</td>
            <td><button class="btn-secondary" onclick="viewExplanation('${fraud.transaction_id}')">View</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function viewExplanation(transactionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/transaction/${transactionId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const explanation = await response.json();
        displayExplanation(explanation);
        
    } catch (error) {
        console.error('Error fetching explanation:', error);
        alert('Error fetching explanation. Please try again.');
    }
}

function updateCharts(stats) {
    // Fraud Distribution Chart
    const ctx1 = document.getElementById('fraudDistributionChart');
    if (ctx1 && window.Chart) {
        if (window.fraudDistChart) {
            window.fraudDistChart.destroy();
        }
        window.fraudDistChart = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Legitimate', 'Fraud'],
                datasets: [{
                    data: [
                        stats.total_transactions - stats.fraud_transactions,
                        stats.fraud_transactions
                    ],
                    backgroundColor: ['#48dbfb', '#ff6b6b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }
    
    // Model Comparison Chart (placeholder - would need actual model data)
    const ctx2 = document.getElementById('modelComparisonChart');
    if (ctx2 && window.Chart) {
        if (window.modelCompChart) {
            window.modelCompChart.destroy();
        }
        window.modelCompChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['ML Ensemble', 'GNN', 'Rule Engine'],
                datasets: [{
                    label: 'Average Score',
                    data: [0.5, 0.5, 0.5], // Placeholder
                    backgroundColor: ['#667eea', '#764ba2', '#feca57']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }
}

async function loadNetworkGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/network`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const graphData = await response.json();
        displayNetworkGraph(graphData);
        
    } catch (error) {
        console.error('Error loading network graph:', error);
    }
}

function displayNetworkGraph(graphData) {
    if (!window.Plotly) {
        console.error('Plotly not loaded');
        return;
    }
    
    const nodes = graphData.nodes.map(node => ({
        ...node,
        color: node.group === 'high_risk' ? '#ff6b6b' : 
               node.group === 'medium_risk' ? '#feca57' : '#48dbfb'
    }));
    
    const edges = graphData.edges;
    
    if (nodes.length === 0) {
        document.getElementById('networkGraph').innerHTML = 
            '<p style="text-align: center; padding: 50px; color: #999;">No network data available</p>';
        return;
    }
    
    // Create network visualization using Plotly
    const data = [{
        type: 'scatter',
        mode: 'markers+text',
        x: nodes.map((_, i) => Math.cos(2 * Math.PI * i / nodes.length)),
        y: nodes.map((_, i) => Math.sin(2 * Math.PI * i / nodes.length)),
        text: nodes.map(n => n.label),
        marker: {
            size: nodes.map(n => 10 + n.value * 2),
            color: nodes.map(n => n.color)
        },
        textposition: 'middle center',
        name: 'Nodes'
    }];
    
    const layout = {
        title: 'Fraud Network Visualization',
        showlegend: false,
        xaxis: { showgrid: false, zeroline: false, showticklabels: false },
        yaxis: { showgrid: false, zeroline: false, showticklabels: false },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        height: 500
    };
    
    Plotly.newPlot('networkGraph', data, layout, {responsive: true});
}

// Auto-refresh every 30 seconds
setInterval(loadDashboardStats, 30000);



