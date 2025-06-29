document.addEventListener('DOMContentLoaded', () => {
    // System stats
    fetch('/admin/dashboard')
        .then(res => res.json())
        .then(data => {
            document.getElementById('stats').innerHTML = `
                <h3>System Stats</h3>
                <ul>
                    <li>Total Users: ${data.total_users}</li>
                    <li>Total Transactions: ${data.total_transactions}</li>
                    <li>Total Balance: ₹${data.total_balance.toFixed(2)}</li>
                </ul>
            `;
        });

    // Fraud cycles (example, if you have such an endpoint)
    fetch('/admin/fraud-cycles')
        .then(res => res.json())
        .then(data => {
            let html = '<h3>Detected Fraud Cycles</h3>';
            if (data.cycles && data.cycles.length) {
                data.cycles.forEach((cycle, i) => {
                    html += `<div>Cycle ${i + 1}: ${cycle.accounts.join(' → ')}</div>`;
                });
            } else {
                html += '<div>No suspicious cycles detected.</div>';
            }
            document.getElementById('fraud-cycles').innerHTML = html;
        });

    // Parameter tuning form (example)
    document.getElementById('parameter-tuning').innerHTML = `
        <h3>Parameter Tuning</h3>
        <form id="param-form">
            α (Amount similarity): <input type="number" step="0.01" name="alpha" value="0.1"><br>
            Max Cycle Length: <input type="number" name="max_cycle" value="6"><br>
            <button type="submit">Update</button>
        </form>
    `;
    document.getElementById('param-form').onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        fetch('/admin/update-params', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                alpha: formData.get('alpha'),
                max_cycle: formData.get('max_cycle')
            })
        }).then(res => res.json())
          .then(data => alert(data.message));
    };
});
