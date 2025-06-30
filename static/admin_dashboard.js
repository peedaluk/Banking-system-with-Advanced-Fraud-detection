document.addEventListener('DOMContentLoaded', () => {
  const totalUsersEl = document.getElementById('totalUsers');
  const totalBalanceEl = document.getElementById('totalBalance');
  const totalTransactionsEl = document.getElementById('totalTransactions');
  const transactionsTableEl = document.getElementById('transactionsTable');
  const usersTableEl = document.getElementById('usersTable');
  const refreshTransactionsBtn = document.getElementById('refreshTransactions');
  const logoutBtn = document.getElementById('logoutBtn');

  async function fetchDashboardData() {
    try {
      const res = await fetch('/admin/dashboard/data');
      if (!res.ok) throw new Error('Failed to fetch dashboard data');
      const data = await res.json();
      totalUsersEl.textContent = data.total_users;
      totalBalanceEl.textContent = `$${parseFloat(data.total_balance).toFixed(2)}`;
      totalTransactionsEl.textContent = data.total_transactions;
    } catch (err) {
      console.error(err);
    }
  }

  async function fetchRecentTransactions() {
    try {
      const res = await fetch('/admin/transactions');
      if (!res.ok) throw new Error('Failed to fetch transactions');
      const { transactions } = await res.json();
      transactionsTableEl.innerHTML = '';
      transactions.forEach(txn => {
        const tr = document.createElement('tr');
        let badgeClass = 'bg-secondary';
        if (txn.type === 'deposit') badgeClass = 'bg-success';
        else if (txn.type === 'withdraw') badgeClass = 'bg-danger';
        else if (txn.type === 'transfer') badgeClass = 'bg-primary';

        tr.innerHTML = `
          <td>${txn.transaction_id}</td>
          <td><span class="badge ${badgeClass}">${txn.type.toUpperCase()}</span></td>
          <td>$${parseFloat(txn.amount).toFixed(2)}</td>
          <td>${txn.account_id}</td>
          <td>${txn.user_id}</td>
          <td>${txn.timestamp}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary" title="View Details"><i class="bi bi-eye"></i></button>
            <button class="btn btn-sm btn-outline-danger" title="Flag as Fraud"><i class="bi bi-flag"></i></button>
          </td>
        `;
        transactionsTableEl.appendChild(tr);
      });
    } catch (err) {
      console.error(err);
    }
  }

  async function fetchUsers() {
    try {
      const res = await fetch('/admin/users');
      if (!res.ok) throw new Error('Failed to fetch users');
      const { users } = await res.json();
      usersTableEl.innerHTML = '';
      users.forEach(user => {
        const tr = document.createElement('tr');
        const statusBadge = user.is_admin
          ? '<span class="badge bg-primary">Admin</span>'
          : user.is_blocked
          ? '<span class="badge bg-danger">Blocked</span>'
          : '<span class="badge bg-success">Active</span>';

        tr.innerHTML = `
          <td>${user.user_id}</td>
          <td>${user.username}</td>
          <td>${user.email}</td>
          <td>${user.joined}</td>
          <td>${statusBadge}</td>
          <td>
            ${
              !user.is_admin
                ? user.is_blocked
                  ? `<button class="btn btn-sm btn-success unblock-btn" data-user="${user.user_id}">Unblock</button>`
                  : `<button class="btn btn-sm btn-warning block-btn" data-user="${user.user_id}">Block</button>`
                : ''
            }
            <button class="btn btn-sm btn-outline-info" title="View Profile"><i class="bi bi-person"></i></button>
          </td>
        `;
        usersTableEl.appendChild(tr);
      });

      // Add event listeners for block/unblock buttons
      document.querySelectorAll('.block-btn').forEach(btn =>
        btn.addEventListener('click', () => blockUser(btn.dataset.user))
      );
      document.querySelectorAll('.unblock-btn').forEach(btn =>
        btn.addEventListener('click', () => unblockUser(btn.dataset.user))
      );
    } catch (err) {
      console.error(err);
    }
  }

  async function blockUser(userId) {
    try {
      const res = await fetch(`/admin/users/${userId}/block`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to block user');
      fetchUsers();
    } catch (err) {
      alert('Error blocking user');
      console.error(err);
    }
  }

  async function unblockUser(userId) {
    try {
      const res = await fetch(`/admin/users/${userId}/unblock`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to unblock user');
      fetchUsers();
    } catch (err) {
      alert('Error unblocking user');
      console.error(err);
    }
  }

  logoutBtn.addEventListener('click', async () => {
    try {
      const res = await fetch('/admin/logout', { method: 'POST' });
      if (res.ok) window.location.href = '/';

      else alert('Logout failed');
    } catch (err) {
      alert('Logout error');
      console.error(err);
    }
  });

  refreshTransactionsBtn.addEventListener('click', fetchRecentTransactions);

  // Initialize dashboard
  fetchDashboardData();
  fetchRecentTransactions();
  fetchUsers();
});
