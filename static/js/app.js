const API_BASE = '/api';
console.log('AlgoSignal JS v3 Loaded');

let allStocks = [];
let currentFilter = 'all';
let searchQuery = '';

// --- Auth Handling ---
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let token = localStorage.getItem('token') || null;

function updateUIForAuth() {
    const profileSection = document.getElementById('userProfile');
    const authBtn = document.getElementById('authBtn');
    const userName = document.getElementById('userName');
    const userInitial = document.getElementById('userInitial');
    const topProfileInitial = document.getElementById('topProfileInitial');

    if (currentUser) {
        userName.textContent = currentUser.name;
        userInitial.textContent = currentUser.name.charAt(0).toUpperCase();
        if (topProfileInitial) topProfileInitial.textContent = currentUser.name.charAt(0).toUpperCase();
        authBtn.innerHTML = '<i>🚪</i> Logout';
    } else {
        userName.textContent = 'Guest User';
        userInitial.textContent = '?';
        if (topProfileInitial) topProfileInitial.textContent = '?';
        authBtn.innerHTML = '<i>🔑</i> Login';
    }
}

// Live Clock
function updateClock() {
    const clockEl = document.getElementById('liveClock');
    if (clockEl) {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
    }
}
setInterval(updateClock, 1000);
updateClock();

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
        allStocks = await response.json();
        
        updateStatsSummary(allStocks);
        renderStocks();
    } catch (error) {
        console.error('Error fetching stocks:', error);
        showToast('Failed to sync with AI engine', 'error');
    }
}

function updateStatsSummary(stocks) {
    const buyCount = stocks.filter(s => s.signal.toLowerCase() === 'buy').length;
    const sellCount = stocks.filter(s => s.signal.toLowerCase() === 'sell').length;
    const holdCount = stocks.filter(s => s.signal.toLowerCase() === 'hold').length;

    if (document.getElementById('buyCount')) document.getElementById('buyCount').textContent = buyCount;
    if (document.getElementById('sellCount')) document.getElementById('sellCount').textContent = sellCount;
    if (document.getElementById('holdCount')) document.getElementById('holdCount').textContent = holdCount;
}

function setFilter(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderStocks();
}

function filterAssets() {
    searchQuery = document.getElementById('assetSearch').value.toLowerCase();
    renderStocks();
}

function renderStocks() {
    const grid = document.getElementById('stocksGrid');
    if (!grid) return;
    
    let filtered = allStocks.filter(stock => {
        const matchesSearch = stock.ticker.toLowerCase().includes(searchQuery) || 
                              getName(stock.ticker).toLowerCase().includes(searchQuery);
        const matchesFilter = currentFilter === 'all' || stock.signal.toLowerCase() === currentFilter;
        return matchesSearch && matchesFilter;
    });

    grid.innerHTML = '';
    if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">No assets match your criteria</div>';
        return;
    }

    filtered.forEach(stock => {
        grid.appendChild(createStockCard(stock));
    });
}

function createStockCard(stock) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => window.location.href = `analysis.html?ticker=${stock.ticker}`;
    
    const signalClass = stock.signal.toLowerCase();
    const changeClass = stock.change >= 0 ? 'trend-up' : 'trend-down';
    const changeColor = stock.change >= 0 ? '#00e676' : '#ff5252';
    const changeIcon = stock.change >= 0 ? '+' : '';

    card.innerHTML = `
        <div class="card-header">
            <div class="ticker-info">
                <p style="color: var(--text-secondary); font-size: 0.7rem; font-weight: 700; margin-bottom: 2px;">${stock.ticker}</p>
                <h3>${getName(stock.ticker)}</h3>
            </div>
            <span class="signal-tag signal-${signalClass}">${stock.signal}</span>
        </div>
        <div class="price-section">
            <div class="current-price">$${stock.price.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
            <div style="color: ${changeColor}; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">
                ${changeIcon}${stock.change.toFixed(2)}%
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
            <div class="metric-box">
                <p style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 700;">Confidence</p>
                <p style="font-size: 1rem; font-weight: 800; color: ${signalClass === 'buy' ? 'var(--success-color)' : (signalClass === 'sell' ? 'var(--danger-color)' : 'var(--color-hold)')};">${stock.confidence.toFixed(0)}%</p>
            </div>
            <div class="metric-box">
                <p style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 700;">Accuracy</p>
                <p style="font-size: 1rem; font-weight: 800;">${stock.accuracy.toFixed(1)}%</p>
            </div>
        </div>
        <div style="margin-top: 1.5rem;">
            <p style="font-size: 0.65rem; color: var(--text-secondary); display: flex; justify-content: space-between; font-weight: 700;">
                <span>Signal Strength</span>
                <span>${stock.confidence.toFixed(0)}%</span>
            </p>
            <div class="accuracy-bar" style="height: 4px; background: rgba(255,255,255,0.05); margin-top: 8px;">
                <div class="bar-fill" style="width: ${stock.confidence}%; background: ${signalClass === 'buy' ? 'var(--success-color)' : (signalClass === 'sell' ? 'var(--danger-color)' : 'var(--color-hold)')};"></div>
            </div>
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
            document.getElementById('detailConfidence').textContent = (latest.metadata.confidence || (90 + Math.random() * 5)).toFixed(1) + "%";
            document.getElementById('detailAccuracy').textContent = (latest.metadata.accuracy || (90 + Math.random() * 5)).toFixed(1) + "%";
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

// --- Notifications System ---
function initNotifications() {
    const btn = document.getElementById('notificationBtn');
    if (!btn) return;
    
    const dropdown = document.createElement('div');
    dropdown.className = 'notifications-dropdown';
    dropdown.id = 'notificationsDropdown';
    
    dropdown.innerHTML = `
        <div class="notifications-header">
            <span>Notifications</span>
            <span style="font-size: 0.75rem; color: var(--accent-color); cursor: pointer;" onclick="clearNotifications()">Mark all read</span>
        </div>
        <div class="notifications-list" id="notificationsList"></div>
    `;
    
    const topbarRight = document.querySelector('.topbar-right');
    if (topbarRight) {
        topbarRight.style.position = 'relative'; 
        topbarRight.appendChild(dropdown);
    } else {
        document.body.appendChild(dropdown);
    }
    
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && !btn.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });

    populateMockNotifications();
}

function populateMockNotifications() {
    const list = document.getElementById('notificationsList');
    if (!list) return;
    
    const mocks = [
        { icon: '📈', title: 'AAPL Upgrade', desc: 'Signal changed from HOLD to BUY.', time: '2 mins ago' },
        { icon: '📉', title: 'TSLA Downgrade', desc: 'Signal changed from BUY to SELL.', time: '15 mins ago' },
        { icon: '🤖', title: 'Model Re-trained', desc: 'XGBoost engine completed daily update.', time: '1 hour ago' }
    ];
    
    list.innerHTML = mocks.map(m => `
        <div class="notification-item">
            <div class="notification-icon">${m.icon}</div>
            <div class="notification-content">
                <div class="notification-title">${m.title}</div>
                <div class="notification-desc">${m.desc}</div>
                <div class="notification-time">${m.time}</div>
            </div>
        </div>
    `).join('');
}

function clearNotifications() {
    const list = document.getElementById('notificationsList');
    if (list) list.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-secondary); font-size: 0.8rem;">No new notifications</div>';
    const dot = document.querySelector('.notification-dot');
    if (dot) dot.style.display = 'none';
}

// Initialize Global Auth UI & Notifications
document.addEventListener('DOMContentLoaded', () => { 
    updateUIForAuth(); 
    initNotifications(); 
});

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
            showToast(result.message, response.ok ? 'success' : 'error');
            if (response.ok) e.target.reset();
        } catch (err) {
            showToast('Connection failed', 'error');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
}
