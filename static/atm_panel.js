function loadATMDashboard() {
    fetch('/atm/mini_statement')
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById('atm-message').innerText = data.error;
            document.getElementById('atm-info').style.display = 'none';
            return;
        }
        document.getElementById('atm-message').innerText = '';
        document.getElementById('atm-info').style.display = 'block';
        document.getElementById('card-number').innerText = data.card_number;
        document.getElementById('account-number').innerText = data.account_number;
        document.getElementById('account-type').innerText = data.account_type;
        document.getElementById('balance').innerText = data.balance.toFixed(2);

        // Mini statement
        const tbody = document.getElementById('mini-statement').getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';
        data.transactions.forEach(tx => {
            let row = tbody.insertRow();
            row.insertCell(0).innerText = tx.type;
            row.insertCell(1).innerText = tx.amount;
            row.insertCell(2).innerText = tx.description;
            row.insertCell(3).innerText = tx.timestamp;
        });
    });
}

// Withdraw cash
document.getElementById('withdraw-form').onsubmit = function(e) {
    e.preventDefault();
    const amount = e.target.amount.value;
    fetch('/atm/withdraw', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('withdraw-result');
        if (data.message) {
            result.innerText = data.message;
            loadATMDashboard();
        } else {
            result.innerText = data.error;
        }
    });
};

// Deposit cash
document.getElementById('deposit-form').onsubmit = function(e) {
    e.preventDefault();
    const amount = e.target.amount.value;
    fetch('/atm/deposit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('deposit-result');
        if (data.message) {
            result.innerText = data.message;
            loadATMDashboard();
        } else {
            result.innerText = data.error;
        }
    });
};

// Transfer funds
document.getElementById('transfer-form').onsubmit = function(e) {
    e.preventDefault();
    const to_account = e.target.to_account.value;
    const amount = e.target.amount.value;
    fetch('/atm/transfer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({to_account, amount})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('transfer-result');
        if (data.message) {
            result.innerText = data.message;
            loadATMDashboard();
        } else {
            result.innerText = data.error;
        }
    });
};

// Change PIN
document.getElementById('change-pin-form').onsubmit = function(e) {
    e.preventDefault();
    const old_pin = e.target.old_pin.value;
    const new_pin = e.target.new_pin.value;
    fetch('/atm/change_pin', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({old_pin, new_pin})
    })
    .then(res => res.json())
    .then(data => {
        let result = document.getElementById('change-pin-result');
        if (data.message) {
            result.innerText = data.message;
            e.target.reset();
        } else {
            result.innerText = data.error;
        }
    });
};

// Logout
document.getElementById('atm-logout-btn').onclick = function() {
    fetch('/atm/logout', {method: 'POST'})
    .then(() => {
        window.location.href = '/';
    });
};

// Initial load
window.onload = loadATMDashboard;
