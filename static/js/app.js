// Global variables
let products = [];
let currentCart = [];
let transactions = [];
let miningResults = null;
let performanceChart = null; // Store chart instance for proper cleanup

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    loadTransactions();
    updateStats();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Range input listeners
    document.getElementById('min-support').addEventListener('input', function() {
        document.getElementById('support-value').textContent = this.value;
    });
    
    document.getElementById('min-confidence').addEventListener('input', function() {
        document.getElementById('confidence-value').textContent = this.value;
    });
}

// Tab Navigation
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Set active button
    event.target.classList.add('active');
    
    // Load data if needed
    if (tabName === 'query') {
        populateProductSelect();
    }
}

// Load products from server
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        products = await response.json();
        displayProducts();
    } catch (error) {
        console.error('Error loading products:', error);
        showNotification('Error loading products', 'error');
    }
}

// Display products in grid
function displayProducts() {
    const grid = document.querySelector('.product-grid');
    grid.innerHTML = '';
    
    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'product-item';
        item.textContent = product.product_name;
        item.dataset.id = product.product_id;
        item.dataset.name = product.product_name;
        
        item.onclick = function() {
            toggleProduct(this);
        };
        
        grid.appendChild(item);
    });
}

// Toggle product selection
function toggleProduct(element) {
    const productName = element.dataset.name;
    
    if (element.classList.contains('selected')) {
        element.classList.remove('selected');
        const index = currentCart.indexOf(productName);
        if (index > -1) {
            currentCart.splice(index, 1);
        }
    } else {
        element.classList.add('selected');
        currentCart.push(productName);
    }
    
    updateCartDisplay();
}

// Update cart display
function updateCartDisplay() {
    const cartDiv = document.getElementById('cart-items');
    cartDiv.innerHTML = '';
    
    if (currentCart.length === 0) {
        cartDiv.innerHTML = '<p style="color: #94a3b8;">No items in cart</p>';
    } else {
        currentCart.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.textContent = item;
            cartDiv.appendChild(itemDiv);
        });
    }
}

// Add transaction
async function addTransaction() {
    if (currentCart.length === 0) {
        showNotification('Cart is empty!', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ items: currentCart })
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification('Transaction added successfully!', 'success');
            clearCart();
            loadTransactions();
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        showNotification('Error adding transaction', 'error');
    }
}

// Clear cart
function clearCart() {
    currentCart = [];
    document.querySelectorAll('.product-item.selected').forEach(item => {
        item.classList.remove('selected');
    });
    updateCartDisplay();
}

// Upload CSV file
async function uploadCSV() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification(`Loaded ${result.loaded} transactions successfully!`, 'success');
            loadTransactions();
            fileInput.value = '';
        } else {
            showNotification(result.error || 'Error uploading file', 'error');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showNotification('Error uploading file', 'error');
    }
}

// Load transactions from server
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        transactions = await response.json();
        displayTransactions();
        updateStats();
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Display transactions
function displayTransactions() {
    const display = document.getElementById('transactions-display');
    const count = document.getElementById('transaction-count');
    
    count.textContent = transactions.length;
    
    if (transactions.length === 0) {
        display.innerHTML = '<p style="color: #94a3b8;">No transactions yet</p>';
        return;
    }
    
    display.innerHTML = '';
    transactions.slice(-10).reverse().forEach(transaction => {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        item.innerHTML = `
            <span class="transaction-id">Transaction #${transaction.id}:</span>
            ${transaction.items.join(', ')}
        `;
        display.appendChild(item);
    });
    
    if (transactions.length > 10) {
        const more = document.createElement('p');
        more.style.textAlign = 'center';
        more.style.color = '#94a3b8';
        more.textContent = `And ${transactions.length - 10} more...`;
        display.appendChild(more);
    }
}

// Run preprocessing
async function runPreprocessing() {
    try {
        showNotification('Running preprocessing...', 'info');
        
        const response = await fetch('/api/preprocess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        if (result.success) {
            displayPreprocessingReport(result.report);
            displayCleanedTransactions(result.cleaned_transactions);
            updateStats();
            showNotification('Preprocessing completed!', 'success');
        }
    } catch (error) {
        console.error('Error preprocessing data:', error);
        showNotification('Error preprocessing data', 'error');
    }
}

// Display preprocessing report
function displayPreprocessingReport(report) {
    const reportDiv = document.getElementById('preprocessing-report');
    const content = reportDiv.querySelector('.report-content');
    
    content.innerHTML = `
        <div class="report-item">
            <div class="report-label">Before Cleaning</div>
            <div class="report-value">${report.total_transactions} transactions</div>
        </div>
        <div class="report-item">
            <div class="report-label">Empty Transactions</div>
            <div class="report-value">${report.empty_transactions} removed</div>
        </div>
        <div class="report-item">
            <div class="report-label">Single-Item Transactions</div>
            <div class="report-value">${report.single_item_transactions} removed</div>
        </div>
        <div class="report-item">
            <div class="report-label">Duplicate Items</div>
            <div class="report-value">${report.duplicate_items_count} instances</div>
        </div>
        <div class="report-item">
            <div class="report-label">Case Inconsistencies</div>
            <div class="report-value">${report.case_inconsistencies} fixed</div>
        </div>
        <div class="report-item">
            <div class="report-label">Invalid Items</div>
            <div class="report-value">${report.invalid_items} removed</div>
        </div>
        <div class="report-item">
            <div class="report-label">Whitespace Issues</div>
            <div class="report-value">${report.whitespace_issues} fixed</div>
        </div>
        <div class="report-item">
            <div class="report-label">After Cleaning</div>
            <div class="report-value">${report.cleaned_transactions} valid</div>
        </div>
        <div class="report-item">
            <div class="report-label">Unique Products</div>
            <div class="report-value">${report.unique_products_after} products</div>
        </div>
    `;
    
    reportDiv.classList.remove('hidden');
}

// Display cleaned transactions
function displayCleanedTransactions(cleanedTransactions) {
    const cleanedDiv = document.getElementById('cleaned-transactions');
    const listDiv = document.getElementById('cleaned-list');
    
    listDiv.innerHTML = '';
    cleanedTransactions.slice(0, 5).forEach(transaction => {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        item.innerHTML = `
            <span class="transaction-id">Transaction #${transaction.id}:</span>
            ${transaction.items.join(', ')}
        `;
        listDiv.appendChild(item);
    });
    
    if (cleanedTransactions.length > 5) {
        const more = document.createElement('p');
        more.style.textAlign = 'center';
        more.style.color = '#94a3b8';
        more.textContent = `Showing 5 of ${cleanedTransactions.length} cleaned transactions`;
        listDiv.appendChild(more);
    }
    
    cleanedDiv.classList.remove('hidden');
}

// Run mining algorithms
async function runMining() {
    const minSupport = document.getElementById('min-support').value;
    const minConfidence = document.getElementById('min-confidence').value;
    
    try {
        showNotification('Running mining algorithms...', 'info');
        
        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                min_support: parseFloat(minSupport),
                min_confidence: parseFloat(minConfidence)
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            showNotification(errorData.error || 'Please preprocess data first!', 'warning');
            return;
        }
        
        const result = await response.json();
        miningResults = result;
        displayMiningResults(result);
        showNotification('Mining completed successfully!', 'success');
        
    } catch (error) {
        console.error('Error running mining:', error);
        showNotification('Error running mining algorithms', 'error');
    }
}

// Display mining results
function displayMiningResults(results) {
    const resultsDiv = document.getElementById('mining-results');
    const tbody = document.getElementById('comparison-body');
    
    tbody.innerHTML = '';
    
    // Display Apriori results
    const aprioriRow = document.createElement('tr');
    aprioriRow.innerHTML = `
        <td><strong>Apriori</strong></td>
        <td>${results.apriori.execution_time.toFixed(2)}</td>
        <td>${results.apriori.rules_generated}</td>
        <td>${results.apriori.frequent_itemsets}</td>
    `;
    tbody.appendChild(aprioriRow);
    
    // Display Eclat results
    const eclatRow = document.createElement('tr');
    eclatRow.innerHTML = `
        <td><strong>Eclat</strong></td>
        <td>${results.eclat.execution_time.toFixed(2)}</td>
        <td>${results.eclat.rules_generated}</td>
        <td>${results.eclat.frequent_itemsets}</td>
    `;
    tbody.appendChild(eclatRow);
    
    // Display CLOSET results
    if (results.closet) {
        const closetRow = document.createElement('tr');
        closetRow.innerHTML = `
            <td><strong>CLOSET</strong></td>
            <td>${results.closet.execution_time.toFixed(2)}</td>
            <td>${results.closet.rules_generated}</td>
            <td>${results.closet.frequent_itemsets}</td>
        `;
        tbody.appendChild(closetRow);
    }
    
    resultsDiv.classList.remove('hidden');
    
    // Draw performance chart
    drawPerformanceChart(results);
}

// Draw performance comparison chart
function drawPerformanceChart(results) {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (performanceChart) {
        performanceChart.destroy();
        performanceChart = null;
    }
    
    performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Execution Time (ms)', 'Rules Generated', 'Frequent Itemsets'],
            datasets: [
                {
                    label: 'Apriori',
                    data: [
                        results.apriori.execution_time,
                        results.apriori.rules_generated,
                        results.apriori.frequent_itemsets
                    ],
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Eclat',
                    data: [
                        results.eclat.execution_time,
                        results.eclat.rules_generated,
                        results.eclat.frequent_itemsets
                    ],
                    backgroundColor: 'rgba(118, 75, 162, 0.5)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                },
                ...(results.closet ? [{
                    label: 'CLOSET',
                    data: [
                        results.closet.execution_time,
                        results.closet.rules_generated,
                        results.closet.frequent_itemsets
                    ],
                    backgroundColor: 'rgba(34, 197, 94, 0.5)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 2
                }] : [])
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Populate product select dropdown
function populateProductSelect() {
    const select = document.getElementById('product-select');
    select.innerHTML = '<option value="">Choose a product...</option>';
    
    // Get unique products from cleaned transactions
    const uniqueProducts = new Set();
    
    // Use products list for now
    products.forEach(product => {
        const option = document.createElement('option');
        option.value = product.product_name;
        option.textContent = product.product_name;
        select.appendChild(option);
    });
}

// Query product associations
async function queryProduct() {
    const productSelect = document.getElementById('product-select');
    const product = productSelect.value;
    
    if (!product) {
        showNotification('Please select a product', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ product: product })
        });
        
        if (response.status === 400) {
            showNotification('Please run mining algorithms first!', 'warning');
            return;
        }
        
        const result = await response.json();
        displayQueryResults(result);
        
    } catch (error) {
        console.error('Error querying product:', error);
        showNotification('Error querying product associations', 'error');
    }
}

// Display query results
function displayQueryResults(result) {
    const resultsDiv = document.getElementById('query-results');
    const queryProduct = document.getElementById('query-product');
    const associationsList = document.getElementById('associations-list');
    const recommendations = document.getElementById('recommendations');
    
    queryProduct.textContent = result.query;
    
    // Display associations
    associationsList.innerHTML = '';
    
    if (result.associations.length === 0) {
        associationsList.innerHTML = '<p style="color: #94a3b8;">No associations found for this product</p>';
    } else {
        result.associations.forEach(assoc => {
            const item = document.createElement('div');
            item.className = 'association-item';
            
            let strengthLabel = 'Weak';
            let strengthClass = 'confidence-weak';
            if (assoc.confidence > 70) {
                strengthLabel = 'Strong';
                strengthClass = 'confidence-strong';
            } else if (assoc.confidence > 50) {
                strengthLabel = 'Moderate';
                strengthClass = 'confidence-moderate';
            }
            
            item.innerHTML = `
                <div class="association-name">${assoc.item}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${assoc.confidence}%">
                        ${assoc.confidence.toFixed(1)}%
                    </div>
                </div>
                <div class="confidence-label ${strengthClass}">${strengthLabel}</div>
            `;
            
            associationsList.appendChild(item);
        });
    }
    
    // Display recommendations
    recommendations.innerHTML = '';
    if (result.recommendations && result.recommendations.length > 0) {
        result.recommendations.forEach(rec => {
            const recItem = document.createElement('div');
            recItem.className = 'recommendation-item';
            recItem.textContent = rec;
            recommendations.appendChild(recItem);
        });
    }
    
    resultsDiv.classList.remove('hidden');
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total_transactions;
        document.getElementById('stat-cleaned').textContent = stats.cleaned_transactions;
        document.getElementById('stat-unique').textContent = stats.unique_products;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Reset all data
async function resetAll() {
    if (!confirm('Are you sure you want to reset all data? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification('All data has been reset', 'info');
            loadTransactions();
            updateStats();
            clearCart();
            
            // Hide results
            document.getElementById('preprocessing-report').classList.add('hidden');
            document.getElementById('cleaned-transactions').classList.add('hidden');
            document.getElementById('mining-results').classList.add('hidden');
            document.getElementById('query-results').classList.add('hidden');
        }
    } catch (error) {
        console.error('Error resetting data:', error);
        showNotification('Error resetting data', 'error');
    }
}

// Load sample data
async function loadSampleData() {
    try {
        await resetAll();
        
        // Simulate uploading the sample CSV
        showNotification('Loading sample data...', 'info');
        
        // The sample data should already be loaded on server startup
        // Just refresh the display
        loadTransactions();
        updateStats();
        
        showNotification('Sample data loaded successfully!', 'success');
    } catch (error) {
        console.error('Error loading sample data:', error);
        showNotification('Error loading sample data', 'error');
    }
}

// Toggle technical details
function toggleTechnical() {
    const content = document.getElementById('technical-content');
    content.classList.toggle('hidden');
    
    if (!content.classList.contains('hidden') && miningResults) {
        displayTechnicalDetails();
    }
}

// Display technical details
function displayTechnicalDetails() {
    const content = document.getElementById('technical-content');
    
    if (!miningResults) {
        content.innerHTML = '<p>No mining results available</p>';
        return;
    }
    
    let html = '<h4>Apriori Rules (Top 10)</h4><ul>';
    miningResults.apriori.rules.slice(0, 10).forEach(rule => {
        html += `<li>{${rule.antecedent.join(', ')}} → {${rule.consequent.join(', ')}} 
                 (support: ${(rule.support * 100).toFixed(1)}%, 
                  confidence: ${(rule.confidence * 100).toFixed(1)}%, 
                  lift: ${rule.lift.toFixed(2)})</li>`;
    });
    html += '</ul>';
    
    content.innerHTML = html;
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
