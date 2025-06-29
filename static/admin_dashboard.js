// DOM elements
const totalUsersEl = document.getElementById('totalUsers');
const totalBalanceEl = document.getElementById('totalBalance');
const totalTransactionsEl = document.getElementById('totalTransactions');
const transactionsTableEl = document.getElementById('transactionsTable');
const usersTableEl = document.getElementById('usersTable');
const refreshTransactionsBtn = document.getElementById('refreshTransactions');
const logoutBtn = document.getElementById('logoutBtn');

// Fetch dashboard data
async function fetchDashboardData() {
    try {
        const response = await fetch('/admin/dashboard/data');
        if (!response.ok) throw new Error('Failed to fetch dashboard data');
        const data = await response.json();
        totalUsersEl.textContent = data.total_users;
        totalTransactionsEl.textContent = data.total_transactions;
        totalBalanceEl.textContent = `$${data.total_balance.toFixed(2)}`;
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

// Fetch recent transactions
async function fetchRecentTransactions() {
    try {
        const response = await fetch('/admin/transactions');
        if (!response.ok) throw new Error('Failed to fetch transactions');
        const { transactions } = await response.json();
        renderTransactions(transactions);
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

// Fetch users
async function fetchUsers() {
    try {
        const response = await fetch('/admin/users');
        if (!response.ok) throw new Error('Failed to fetch users');
        const { users } = await response.json();
        renderUsers(users);
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

// Render transactions
function renderTransactions(transactions) {
    transactionsTableEl.innerHTML = '';
    transactions.forEach(txn => {
        const row = document.createElement('tr');
        let badgeClass = 'bg-secondary';
        if (txn.type === 'deposit') badgeClass = 'bg-success';
        if (txn.type === 'withdraw') badgeClass = 'bg-danger';
        if (txn.type === 'transfer') badgeClass = 'bg-primary';
        row.innerHTML = `
            <td>${txn.transaction_id}</td>
            <td><span class="badge ${badgeClass}">${txn.type.toUpperCase()}</span></td>
            <td>$${parseFloat(txn.amount).toFixed(2)}</td>
            <td>${txn.account_id}</td>
            <td>${txn.user_id}</td>
            <td>${txn.timestamp}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" data-bs-toggle="tooltip" title="View Details">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" data-bs-toggle="tooltip" title="Flag as Fraud">
                    <i class="bi bi-flag"></i>
                </button>
            </td>
        `;
        transactionsTableEl.appendChild(row);
    });
}

// Render users
function renderUsers(users) {
    usersTableEl.innerHTML = '';
    users.forEach(user => {
        const row = document.createElement('tr');
        let statusBadge = '';
        if (user.is_admin) {
            statusBadge = '<span class="badge bg-primary">Admin</span>';
        } else if (user.is_blocked) {
            statusBadge = '<span class="badge bg-danger">Blocked</span>';
        } else {
            statusBadge = '<span class="badge bg-success">Active</span>';
        }
        row.innerHTML = `
            <td>${user.user_id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.joined}</td>
            <td>${statusBadge}</td>
            <td>
                ${!user.is_admin ? `
                    ${user.is_blocked ? `
                        <button class="btn btn-sm btn-success action-btn unblock-btn" data-user="${user.user_id}">
                            Unblock
                        </button>
                    ` : `
                        <button class="btn btn-sm btn-warning action-btn block-btn" data-user="${user.user_id}">
                            Block
                        </button>
                    `}
                ` : ''}
                <button class="btn btn-sm btn-outline-info action-btn" data-bs-toggle="tooltip" title="View Profile">
                    <i class="bi bi-person"></i>
                </button>
            </td>
        `;
        usersTableEl.appendChild(row);
    });
    document.querySelectorAll('.block-btn').forEach(btn => {
        btn.addEventListener('click', () => blockUser(btn.dataset.user));
    });
    document.querySelectorAll('.unblock-btn').forEach(btn => {
        btn.addEventListener('click', () => unblockUser(btn.dataset.user));
    });
}

// Block user
async function blockUser(userId) {
    try {
        const response = await fetch(`/admin/users/${userId}/block`, {
            method: 'POST'
        });
        if (response.ok) {
            alert(`User ${userId} blocked successfully`);
            fetchUsers();
        } else {
            throw new Error('Failed to block user');
        }
    } catch (error) {
        console.error('Error blocking user:', error);
        alert('Failed to block user');
    }
}

// Unblock user
async function unblockUser(userId) {
    try {
        const response = await fetch(`/admin/users/${userId}/unblock`, {
            method: 'POST'
        });
        if (response.ok) {
            alert(`User ${userId} unblocked successfully`);
            fetchUsers();
        } else {
            throw new Error('Failed to unblock user');
        }
    } catch (error) {
        console.error('Error unblocking user:', error);
        alert('Failed to unblock user');
    }
}

// Logout
async function logout() {
    try {
        const response = await fetch('/admin/logout', {
            method: 'POST'
        });
        if (response.ok) {
            window.location.href = '/login';
        } else {
            throw new Error('Logout failed');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('Failed to logout');
    }
}

// Initialize dashboard
function initDashboard() {
    fetchDashboardData();
    fetchRecentTransactions();
    fetchUsers();
    refreshTransactionsBtn.addEventListener('click', fetchRecentTransactions);
    logoutBtn.addEventListener('click', logout);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initDashboard);
