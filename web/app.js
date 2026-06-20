const CATEGORY_ICONS = {
    "Makanan & Minuman": "🍜",
    "Belanja Kebutuhan": "🛒",
    "Sewa & Tempat Tinggal": "🏠",
    "Transportasi": "🚗",
    "Kesehatan": "💊",
    "Pendidikan": "📚",
    "Hiburan": "🎮",
    "Pakaian": "👗",
    "Pulsa & Internet": "📱",
    "Tabungan": "💰",
    "Perawatan": "🔧",
    "Gaji": "💼",
    "Investasi": "📈",
    "Bonus/Hadiah": "🎁",
    "Freelance": "💼",
    "Pinjaman Masuk": "💵",
    "Lainnya": "📦",
};

const CATEGORY_COLORS = {
    "Makanan & Minuman": "#f97316",
    "Belanja Kebutuhan": "#8b5cf6",
    "Sewa & Tempat Tinggal": "#ec4899",
    "Transportasi": "#06b6d4",
    "Kesehatan": "#ef4444",
    "Pendidikan": "#3b82f6",
    "Hiburan": "#a855f7",
    "Pakaian": "#f472b6",
    "Pulsa & Internet": "#22d3ee",
    "Tabungan": "#22c55e",
    "Perawatan": "#f59e0b",
    "Gaji": "#10b981",
    "Investasi": "#6366f1",
    "Bonus/Hadiah": "#f43f5e",
    "Freelance": "#14b8a6",
    "Pinjaman Masuk": "#84cc16",
    "Lainnya": "#64748b",
};

const API_BASE = window.location.origin;
const REFRESH_INTERVAL = 30000;

let transactions = [];
let categoryChart = null;
let trendChart = null;
let refreshTimer = null;
let isLoading = false;

document.addEventListener("DOMContentLoaded", () => {
    loadData();
    setupEventListeners();
    startAutoRefresh();
});

function setupEventListeners() {
    document.getElementById("apply-filter").addEventListener("click", applyFilters);
    document.getElementById("reset-filter").addEventListener("click", resetFilters);
    document.getElementById("filter-type").addEventListener("change", updateCategoryFilter);

    const refreshBtn = document.getElementById("manual-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => loadData(true));
    }
}

async function loadData(forceRefresh = false) {
    if (isLoading) return;
    isLoading = true;

    showLoading(true);

    try {
        const url = forceRefresh ? `${API_BASE}/api/refresh` : `${API_BASE}/api/data`;
        const response = await fetch(url, {
            cache: "no-store",
            headers: { "Cache-Control": "no-cache" },
        });

        if (response.ok) {
            const data = await response.json();
            transactions = data.transactions || [];

            updateDataSource(data.source);
            updateSummaryFromAPI(data.summary);
        } else {
            throw new Error("API response not ok");
        }
    } catch (error) {
        console.error("Fetch error:", error);
        showConnectionError(true);
    } finally {
        isLoading = false;
        showLoading(false);
    }

    updateUI();
}

function updateSummaryFromAPI(summary) {
    if (!summary) return;

    const incomeEl = document.getElementById("total-income");
    const expenseEl = document.getElementById("total-expense");
    const balanceEl = document.getElementById("balance");

    if (incomeEl) incomeEl.textContent = `Rp ${(summary.total_income || 0).toLocaleString("id-ID")}`;
    if (expenseEl) expenseEl.textContent = `Rp ${(summary.total_expense || 0).toLocaleString("id-ID")}`;
    if (balanceEl) balanceEl.textContent = `Rp ${(summary.balance || 0).toLocaleString("id-ID")}`;
}

function updateDataSource(source) {
    const indicator = document.getElementById("data-source");
    if (!indicator) return;

    const sources = {
        google_sheets: { text: "🟢 Synced with Google Sheets", color: "#22c55e" },
        local_file: { text: "🟡 Using local data.json", color: "#f59e0b" },
        none: { text: "🔴 No data available", color: "#ef4444" },
        error: { text: "🔴 Connection error", color: "#ef4444" },
    };

    const s = sources[source] || sources.none;
    indicator.textContent = s.text;
    indicator.style.color = s.color;
}

function showLoading(show) {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
        overlay.style.display = show ? "flex" : "none";
    }
}

function showConnectionError(show) {
    const banner = document.getElementById("error-banner");
    if (banner) {
        banner.style.display = show ? "block" : "none";
    }
}

function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => {
        loadData(false);
    }, REFRESH_INTERVAL);

    updateRefreshStatus();
}

function updateRefreshStatus() {
    const status = document.getElementById("refresh-status");
    if (status) {
        status.textContent = `Auto-refresh: ${REFRESH_INTERVAL / 1000}s`;
    }
}

function updateUI() {
    updateSummaryCards();
    updateTransactionsTable();
    updateCategoriesGrid();
    updateCharts();
    updateLastUpdate();
}

function updateSummaryCards() {
    const income = transactions
        .filter((t) => t.type === "pemasukan")
        .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);
    const expense = transactions
        .filter((t) => t.type === "pengeluaran")
        .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);
    const balance = income - expense;

    const incomeEl = document.getElementById("total-income");
    const expenseEl = document.getElementById("total-expense");
    const balanceEl = document.getElementById("balance");

    if (incomeEl) incomeEl.textContent = `Rp ${income.toLocaleString("id-ID")}`;
    if (expenseEl) expenseEl.textContent = `Rp ${expense.toLocaleString("id-ID")}`;
    if (balanceEl) balanceEl.textContent = `Rp ${balance.toLocaleString("id-ID")}`;
}

function updateTransactionsTable() {
    const tbody = document.getElementById("transactions-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    const filteredTransactions = getFilteredTransactions();

    if (filteredTransactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">
                    📭 Tidak ada transaksi ditemukan
                </td>
            </tr>
        `;
        return;
    }

    filteredTransactions.forEach((t) => {
        const icon = CATEGORY_ICONS[t.category] || t.icon || "📦";
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${icon}</td>
            <td>${formatDate(t.date)}</td>
            <td><span class="type-badge type-${t.type}">${t.type === "pengeluaran" ? "💸 Pengeluaran" : "💰 Pemasukan"}</span></td>
            <td>${t.category}</td>
            <td class="${t.type === "pemasukan" ? "amount-positive" : "amount-negative"}">
                ${t.type === "pemasukan" ? "+" : "-"} Rp ${parseFloat(t.amount || 0).toLocaleString("id-ID")}
            </td>
            <td>${t.note || "-"}</td>
        `;
        tbody.appendChild(row);
    });
}

function updateCategoriesGrid() {
    const grid = document.getElementById("categories-grid");
    if (!grid) return;
    grid.innerHTML = "";

    const categoryTotals = {};
    transactions.forEach((t) => {
        if (!categoryTotals[t.category]) {
            categoryTotals[t.category] = { total: 0, count: 0, type: t.type };
        }
        categoryTotals[t.category].total += parseFloat(t.amount || 0);
        categoryTotals[t.category].count += 1;
    });

    if (Object.keys(categoryTotals).length === 0) {
        grid.innerHTML = '<p style="color:#94a3b8; text-align:center;">Belum ada data kategori</p>';
        return;
    }

    Object.entries(categoryTotals).forEach(([cat, data]) => {
        const icon = CATEGORY_ICONS[cat] || "📦";
        const card = document.createElement("div");
        card.className = "category-card";
        card.innerHTML = `
            <div class="category-icon">${icon}</div>
            <div class="category-info">
                <h4>${cat}</h4>
                <p>Rp ${data.total.toLocaleString("id-ID")} • ${data.count} transaksi</p>
            </div>
        `;
        grid.appendChild(card);
    });
}

function updateCharts() {
    updateCategoryChart();
    updateTrendChart();
}

function updateCategoryChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const categoryTotals = {};
    transactions
        .filter((t) => t.type === "pengeluaran")
        .forEach((t) => {
            categoryTotals[t.category] = (categoryTotals[t.category] || 0) + parseFloat(t.amount || 0);
        });

    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);
    const colors = labels.map((cat) => CATEGORY_COLORS[cat] || "#64748b");

    if (categoryChart) {
        categoryChart.destroy();
    }

    if (labels.length === 0) return;

    categoryChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [
                {
                    data: data,
                    backgroundColor: colors,
                    borderColor: "#1e293b",
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#94a3b8",
                        padding: 15,
                        usePointStyle: true,
                    },
                },
            },
        },
    });
}

function updateTrendChart() {
    const canvas = document.getElementById("trendChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const monthlyData = {};
    transactions.forEach((t) => {
        const month = t.date ? t.date.substring(0, 7) : "";
        if (!month) return;
        if (!monthlyData[month]) {
            monthlyData[month] = { income: 0, expense: 0 };
        }
        if (t.type === "pemasukan") {
            monthlyData[month].income += parseFloat(t.amount || 0);
        } else {
            monthlyData[month].expense += parseFloat(t.amount || 0);
        }
    });

    const labels = Object.keys(monthlyData).sort();
    const incomeData = labels.map((m) => monthlyData[m].income);
    const expenseData = labels.map((m) => monthlyData[m].expense);

    if (trendChart) {
        trendChart.destroy();
    }

    if (labels.length === 0) return;

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels.map((l) => formatMonth(l)),
            datasets: [
                {
                    label: "Pemasukan",
                    data: incomeData,
                    borderColor: "#22c55e",
                    backgroundColor: "rgba(34, 197, 94, 0.1)",
                    fill: true,
                    tension: 0.4,
                },
                {
                    label: "Pengeluaran",
                    data: expenseData,
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239, 68, 68, 0.1)",
                    fill: true,
                    tension: 0.4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#94a3b8",
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#94a3b8" },
                    grid: { color: "#334155" },
                },
                y: {
                    ticks: {
                        color: "#94a3b8",
                        callback: (value) => `Rp ${(value / 1000000).toFixed(1)}jt`,
                    },
                    grid: { color: "#334155" },
                },
            },
        },
    });
}

function getFilteredTransactions() {
    const typeFilter = document.getElementById("filter-type").value;
    const categoryFilter = document.getElementById("filter-category").value;
    const monthFilter = document.getElementById("filter-month").value;

    return transactions.filter((t) => {
        if (typeFilter !== "all" && t.type !== typeFilter) return false;
        if (categoryFilter !== "all" && t.category !== categoryFilter) return false;
        if (monthFilter && t.date && !t.date.startsWith(monthFilter)) return false;
        return true;
    });
}

function applyFilters() {
    updateTransactionsTable();
    updateSummaryCards();
}

function resetFilters() {
    document.getElementById("filter-type").value = "all";
    document.getElementById("filter-category").value = "all";
    document.getElementById("filter-month").value = "";
    updateTransactionsTable();
    updateSummaryCards();
}

function updateCategoryFilter() {
    const typeFilter = document.getElementById("filter-type").value;
    const categorySelect = document.getElementById("filter-category");

    const categories = new Set();
    transactions.forEach((t) => {
        if (typeFilter === "all" || t.type === typeFilter) {
            categories.add(t.category);
        }
    });

    categorySelect.innerHTML = '<option value="all">Semua Kategori</option>';
    Array.from(categories).sort().forEach((cat) => {
        const icon = CATEGORY_ICONS[cat] || "📦";
        categorySelect.innerHTML += `<option value="${cat}">${icon} ${cat}</option>`;
    });
}

function updateLastUpdate() {
    const el = document.getElementById("last-update");
    if (el) el.textContent = new Date().toLocaleString("id-ID");
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
        day: "numeric",
        month: "short",
        year: "numeric",
    });
}

function formatMonth(monthStr) {
    const [year, month] = monthStr.split("-");
    const months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
    return `${months[parseInt(month) - 1]} ${year}`;
}
