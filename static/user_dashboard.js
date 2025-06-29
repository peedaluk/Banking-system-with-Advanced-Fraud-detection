function loadDashboard() {
    fetch('/user/dashboard/data')
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById('dashboard-message').innerText = data.error;
            return;
        }
        document.getElementById('welcome').innerText = 'Welcome, ' + data.username;
        document.getElementById('referral-count').innerText = data.referral_count;
 
        // Accounts
        const accountsTable = document.getElementById('accounts-table').getElementsByTagName('tbody')[0];
        accountsTable.innerHTML = '';
        data.accounts.forEach(acc => {
            let row = accountsTable.insertRow();
            row.insertCell(0).innerText = acc.account_id;
            row.insertCell(1).innerText = acc.account_type;
            row.insertCell(2).innerText = acc.balance.toFixed(2);
            row.insertCell(3).innerText = acc.card_number;
            row.insertCell(4).innerText = acc.account_number;
            let delCell = row.insertCell(5);
            let delBtn = document.createElement('button');
            delBtn.innerText = 'Delete';
            delBtn.onclick = function() { openDeleteModal(acc.account_id); };
            delCell.appendChild(delBtn);
        });

        // Transactions
        const txTable = document.getElementById('transactions-table').getElementsByTagName('tbody')[0];
        txTable.innerHTML = '';
        data.transactions.forEach(tx => {
            let row = txTable.insertRow();
            row.insertCell(0).innerText = tx.type;
            row.insertCell(1).innerText = tx.amount;
            row.insertCell(2).innerText = tx.description;
            row.insertCell(3).innerText = tx.timestamp;
            row.insertCell(4).innerText = tx.account_id;
        });
    });
}

// Create account
document.getElementById('create-account-form').onsubmit = function(e) {
    e.preventDefault();
    const account_type = e.target.account_type.value;
    fetch('/user/create_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({account_type})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('create-account-result');
        if (data.message) {
            result.innerHTML = `<b>${data.message}</b><br>
            Account Number: ${data.account_number}<br>
            Card Number: ${data.card_number}<br>
            PIN: <b>${data.pin}</b> (Save this securely!)`;
            loadDashboard();
        } else {
            result.innerText = data.error;
        }
    });
};

// Delete account modal logic
function openDeleteModal(account_id) {
    document.getElementById('delete-modal').style.display = 'block';
    document.getElementById('delete-account-id').value = account_id;
    document.getElementById('delete-account-result').innerText = '';
}
function closeDeleteModal() {
    document.getElementById('delete-modal').style.display = 'none';
}

document.getElementById('delete-account-form').onsubmit = function(e) {
    e.preventDefault();
    const account_id = e.target.account_id.value;
    const card_number = e.target.card_number.value;
    const pin = e.target.pin.value;
    fetch('/user/delete_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({account_id, card_number, pin})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('delete-account-result');
        if (data.message) {
            result.innerText = data.message;
            setTimeout(() => {
                closeDeleteModal();
                loadDashboard();
            }, 1500);
        } else {
            result.innerText = data.error;
        }
    });
};

//logout 
document.getElementById('logout-btn').onclick = function() {
    fetch('/user/logout', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        // Optionally show a message: alert(data.message);
        window.location.href = '/';
    });
};
// Initial load
window.onload = loadDashboard;
