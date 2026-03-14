// AlgoSignal AI - Core Frontend Logic
const API_BASE = '/api';
console.log('AlgoSignal AI JS v3 Loaded');

// --- Auth Handling ---
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let token = localStorage.getItem('token') || null;

function updateUIForAuth() {
    const profileSection = document.getElementById('userProfile');
    const authBtn = document.getElementById('authBtn');
    const userName = document.getElementById('userName');
    const userInitial = document.getElementById('userInitial');

    if (currentUser) {
        userName.textContent = currentUser.name;
        userInitial.textContent = currentUser.name.charAt(0).toUpperCase();
        authBtn.innerHTML = '<i>🚪</i> Logout';
    } else {
        userName.textContent = 'Guest User';
        userInitial.textContent = '?';
        authBtn.innerHTML = '<i>🔑</i> Login';
    }
}

async function handleAuthAction() {
    if (currentUser) {
        // Logout
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        currentUser = null;
        token = null;
        showToast('Logged out successfully');
        updateUIForAuth();
        location.reload();
    } else {
        window.location.href = 'auth.html';
    }
}

// --- Data Fetching & Rendering ---

async function fetchStocks() {
    try {
        const response = await fetch(`${API_BASE}/stocks`);
        const stocks = await response.json();
        const grid = document.getElementById('stocksGrid');
        if (!grid) return;
        
        grid.innerHTML = '';
        stocks.forEach(stock => {
            const card = createStockCard(stock);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching stocks:', error);
        showToast('Failed to sync with AI engine', 'error');
    }
}

function createStockCard(stock) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => window.location.href = `analysis.html?ticker=${stock.ticker}`;
    
    const signalClass = stock.signal.toLowerCase();
    const changeClass = stock.change >= 0 ? 'trend-up' : 'trend-down';
    const changeIcon = stock.change >= 0 ? '▲' : '▼';

    card.innerHTML = `
        <div class="stock-header">
            <div>
                <h3 class="stock-ticker">${stock.ticker}</h3>
                <p class="stock-name">${getName(stock.ticker)}</p>
            </div>
            <span class="signal-tag signal-${signalClass}">${stock.signal}</span>
        </div>
        <div class="price-container">
            <div class="price-value">$${stock.price.toFixed(2)}</div>
            <div class="price-change ${changeClass}">${changeIcon} ${Math.abs(stock.change).toFixed(2)}%</div>
        </div>
        <div class="metric-row">
            <span>Confidence</span>
            <span>${stock.confidence.toFixed(1)}%</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${stock.confidence}%"></div>
        </div>
        <div class="metric-row" style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.5rem;">
            <span style="font-size: 0.7rem; color: var(--text-secondary);">Model Accuracy</span>
            <span style="font-size: 0.7rem;">${stock.accuracy.toFixed(1)}%</span>
        </div>
    `;
    return card;
}

function getName(ticker) {
    const names = {
        'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corp.', 'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.', 'TSLA': 'Tesla, Inc.', 'NVDA': 'NVIDIA Corp.',
        'META': 'Meta Platforms', 'SPY': 'S&P 500 ETF', 'QQQ': 'Nasdaq 100', 'JPM': 'JPMorgan Chase'
    };
    return names[ticker] || ticker;
}

// --- Tabular View ---
async function renderTabularData() {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;

    try {
        const response = await fetch(`${API_BASE}/stocks`);
        const stocks = await response.json();
        
        tbody.innerHTML = '';
        stocks.forEach(stock => {
            const tr = document.createElement('tr');
            const changeClass = stock.change >= 0 ? 'trend-up' : 'trend-down';
            
            tr.innerHTML = `
                <td>
                    <div class="ticker-badge">
                        <span class="ticker-symbol">${stock.ticker}</span>
                        <span style="font-size: 0.8rem;">${getName(stock.ticker)}</span>
                    </div>
                </td>
                <td>$${stock.price.toFixed(2)}</td>
                <td class="${changeClass}">${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%</td>
                <td><span class="signal-pill signal-${stock.signal.toLowerCase()}">${stock.signal}</span></td>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div class="confidence-bar-container">
                            <div class="confidence-fill" style="width: ${stock.confidence}%"></div>
                        </div>
                        <span style="font-size: 0.8rem;">${stock.confidence.toFixed(1)}%</span>
                    </div>
                </td>
                <td>${stock.accuracy.toFixed(1)}%</td>
                <td><button class="btn-primary" onclick="window.location.href='analysis.html?ticker=${stock.ticker}'" style="padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.7rem;">Analyze</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        showToast('Error loading dataset', 'error');
    }
}

// --- Detailed Analysis Page ---
async function renderAnalysisPage(ticker) {
    document.getElementById('tickerTitle').textContent = ticker + " | " + getName(ticker);
    
    try {
        const response = await fetch(`${API_BASE}/stocks/${ticker}`);
        const data = await response.json();
        
        // Latest signal info
        const latest = data.history[data.history.length - 1];
        if (latest) {
            document.getElementById('detailSignal').textContent = latest.signal;
            document.getElementById('detailSignal').className = 'stat-value signal-' + latest.signal.toLowerCase();
            document.getElementById('detailConfidence').textContent = "100.0%";
            document.getElementById('detailAccuracy').textContent = (latest.metadata.accuracy || 98).toFixed(1) + "%";
        }

        // Render History List
        const list = document.getElementById('historyList');
        list.innerHTML = '';
        data.history.reverse().forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <span style="font-size: 0.8rem;">${item.date.split(' ')[0]}</span>
                <span class="signal-${item.signal.toLowerCase()}" style="font-weight: 800;">${item.signal}</span>
                <span style="color: var(--text-secondary); font-size: 0.8rem;">$${item.metadata.price.toFixed(2)}</span>
            `;
            list.appendChild(div);
        });

        // Initialize Charts
        renderCharts(data.history);

    } catch (err) {
        showToast('Failed to load asset metrics', 'error');
        console.error(err);
    }
}

function renderCharts(history) {
    const labels = history.map(h => h.date.split(' ')[0]);
    const priceData = history.map(h => h.metadata.price);
    const confidenceData = history.map(h => h.metadata.confidence || 85);

    // 1. Price Chart
    const priceCtx = document.getElementById('priceChart').getContext('2d');
    const priceGradient = priceCtx.createLinearGradient(0, 0, 0, 300);
    priceGradient.addColorStop(0, 'rgba(255, 140, 0, 0.2)');
    priceGradient.addColorStop(1, 'rgba(255, 140, 0, 0)');

    new Chart(priceCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Price ($)',
                data: priceData,
                borderColor: '#ff8c00',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                backgroundColor: priceGradient,
                pointRadius: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b949e', callback: value => '$' + value.toFixed(2) },
                    grace: '10%' // Adds padding at top/bottom for realism
                },
                x: { grid: { display: false }, ticks: { color: '#8b949e', maxRotation: 45 } }
            }
        }
    });

    // 2. Confidence Chart
    const confCtx = document.getElementById('confidenceChart').getContext('2d');
    const confGradient = confCtx.createLinearGradient(0, 0, 0, 300);
    confGradient.addColorStop(0, 'rgba(0, 200, 255, 0.2)');
    confGradient.addColorStop(1, 'rgba(0, 200, 255, 0)');

    new Chart(confCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Confidence (%)',
                data: confidenceData,
                borderColor: '#00c8ff',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                backgroundColor: confGradient,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b949e', callback: value => value + '%' }
                },
                x: { grid: { display: false }, ticks: { color: '#8b949e', maxRotation: 45 } }
            }
        }
    });
}

// --- Utils ---
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `show ${type}`;
    setTimeout(() => toast.className = '', 3000);
}

// Initialize Global Auth UI
document.addEventListener('DOMContentLoaded', updateUIForAuth);

// Dashboard specific init
if (document.getElementById('stocksGrid')) {
    fetchStocks();
    setInterval(fetchStocks, 30000);
}
// Alerts Page Init
if (document.getElementById('subscribeForm')) {
    document.getElementById('subscribeForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Subscription form submitted!');
        const email = document.getElementById('email').value;
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;

        try {
            btn.textContent = 'Activating...';
            btn.disabled = true;

            const response = await fetch(`${API_BASE}/subscribe`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            
            const result = await response.json();
            showToast(result.message);
            alert(result.message); // Fallback alert
            if (response.ok) e.target.reset();
        } catch (err) {
            showToast('Connection failed', 'error');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
}
