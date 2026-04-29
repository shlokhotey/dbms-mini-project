// static/js/app.js

document.addEventListener("DOMContentLoaded", () => {
    // Initialize application
    fetchStats();
    fetchStores();
    fetchProducts();
    fetchInventory();
    fetchSales();

    // Setup form listener
    document.getElementById("sale-form").addEventListener("submit", handleFormSubmit);
    
    // Live clock
    setInterval(() => {
        document.getElementById("clock").innerText = new Date().toLocaleString('en-IN');
    }, 1000);
});

// Helper functions for alerts
function showAlert(message, type) {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    document.getElementById("alert-container").innerHTML = alertHTML;
}

// Fetch dashboard stats
async function fetchStats() {
    try {
        const response = await fetch("/api/stats");
        const data = await response.json();
        
        document.getElementById("stat-revenue").innerText = `₹${data.total_revenue.toLocaleString('en-IN')}`;
        document.getElementById("stat-stores").innerText = data.total_stores;
        document.getElementById("stat-products").innerText = data.total_products;
        document.getElementById("stat-alerts").innerText = data.low_stock_alerts;
    } catch (err) {
        console.error("Failed to load stats", err);
    }
}

// Fetch stores for dropdown
async function fetchStores() {
    try {
        const response = await fetch("/api/stores");
        const stores = await response.json();
        
        const select = document.getElementById("store-select");
        select.innerHTML = '<option value="" disabled selected>Select a store...</option>';
        
        stores.forEach(store => {
            const option = document.createElement("option");
            option.value = store.storeid;
            option.textContent = `${store.location} (Mgr: ${store.managername})`;
            select.appendChild(option);
        });
        
        checkFormReady();
    } catch (err) {
        console.error("Failed to load stores", err);
        document.getElementById("store-select").innerHTML = '<option value="" disabled>Error loading stores</option>';
    }
}

// Fetch products for dropdown
async function fetchProducts() {
    try {
        const response = await fetch("/api/products");
        const products = await response.json();
        
        const select = document.getElementById("product-select");
        select.innerHTML = '<option value="" disabled selected>Select a product...</option>';
        
        products.forEach(product => {
            const option = document.createElement("option");
            option.value = product.productid;
            option.textContent = `${product.name} - ₹${product.unitprice}`;
            // Optional: attach price as data attr
            option.dataset.price = product.unitprice;
            select.appendChild(option);
        });
        
        checkFormReady();
    } catch (err) {
        console.error("Failed to load products", err);
        document.getElementById("product-select").innerHTML = '<option value="" disabled>Error loading products</option>';
    }
}

function checkFormReady() {
    const storeSelect = document.getElementById("store-select");
    const productSelect = document.getElementById("product-select");
    const btn = document.getElementById("submit-btn");
    
    if (storeSelect.options.length > 1 && productSelect.options.length > 1) {
        btn.disabled = false;
    }
}

// Fetch inventory data to populate the dynamic table
async function fetchInventory() {
    const tbody = document.querySelector("#inventory-table tbody");
    
    // UI state loading
    document.getElementById("refresh-btn").innerHTML = '<i class="spinner-border spinner-border-sm"></i> Refreshing';
    
    try {
        const response = await fetch("/api/inventory");
        const inventory = await response.json();
        
        tbody.innerHTML = '';
        
        if (inventory.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No inventory data available.</td></tr>';
        } else {
            inventory.forEach(item => {
                const tr = document.createElement("tr");
                const isLowStock = item.stockquantity < 20;
                
                const statusBadge = isLowStock 
                    ? `<span class="badge badge-low-stock">Low Stock</span>`
                    : `<span class="badge badge-in-stock">In Stock</span>`;
                
                tr.innerHTML = `
                    <td class="fw-bold text-secondary">${item.storelocation}</td>
                    <td><span class="text-muted small">${item.category}</span></td>
                    <td class="fw-semibold">${item.productname}</td>
                    <td>₹${Number(item.unitprice).toFixed(2)}</td>
                    <td class="text-center fw-bold ${isLowStock ? 'text-danger' : 'text-success'}">${item.stockquantity}</td>
                    <td class="text-center">${statusBadge}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Failed to load inventory", err);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger py-4">Error loading inventory data.</td></tr>';
    } finally {
        document.getElementById("refresh-btn").innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
    }
}

// Fetch sales history data to populate the dynamic table
async function fetchSales() {
    const tbody = document.querySelector("#sales-table tbody");
    
    // UI state loading
    document.getElementById("refresh-sales-btn").innerHTML = '<i class="spinner-border spinner-border-sm"></i> Refreshing';
    
    try {
        const response = await fetch("/api/sales");
        const sales = await response.json();
        
        tbody.innerHTML = '';
        
        if (sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No sales recorded yet.</td></tr>';
        } else {
            sales.forEach(sale => {
                const tr = document.createElement("tr");
                
                tr.innerHTML = `
                    <td class="text-muted small">${new Date(sale.saledate).toLocaleString('en-IN')}</td>
                    <td class="fw-bold text-secondary">${sale.storelocation}</td>
                    <td class="fw-semibold">${sale.productname}</td>
                    <td class="text-center">${sale.quantitysold}</td>
                    <td class="text-end fw-bold text-success">₹${Number(sale.totalamount).toFixed(2)}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-danger shadow-none" onclick="deleteSale(event, ${sale.saleid})" title="Delete sale">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Failed to load sales", err);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger py-4">Error loading sales data.</td></tr>';
    } finally {
        document.getElementById("refresh-sales-btn").innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
    }
}

async function deleteSale(event, saleId) {
    if (!confirm("Delete this sale and restore stock?")) {
        return;
    }

    const button = event.target.closest("button");
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }

    try {
        const response = await fetch(`/api/sales/${saleId}`, { method: "DELETE" });
        const data = await response.json();

        if (response.ok && data.success) {
            showAlert(data.message, "success");
            fetchSales();
            fetchInventory();
            fetchStats();
        } else {
            showAlert(data.errors ? data.errors.join("<br>") : "Unable to delete sale.", "danger");
        }
    } catch (err) {
        console.error("Delete sale error:", err);
        showAlert("A network error occurred while deleting the sale.", "danger");
    } finally {
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-trash"></i>';
        }
    }
}

// Handle the sale form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const storeId = document.getElementById("store-select").value;
    const productId = document.getElementById("product-select").value;
    const quantity = parseInt(document.getElementById("quantity-input").value);
    const btn = document.getElementById("submit-btn");
    
    if (!storeId || !productId || !quantity) {
        showAlert("Please fill in all fields correctly.", "warning");
        return;
    }
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    
    try {
        const response = await fetch("/api/sales", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                store_id: parseInt(storeId),
                product_id: parseInt(productId),
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showAlert(data.message, "success");
            // Reset quantity to 1 but keep store/product selections for rapid entry
            document.getElementById("quantity-input").value = 1;
            
            // Refresh data
            fetchInventory();
            fetchStats();
            fetchSales();
        } else {
            showAlert(data.errors.join("<br>"), "danger");
        }
    } catch (err) {
        console.error("Sale submission error:", err);
        showAlert("A network error occurred while processing the sale.", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Record Sale';
    }
}
