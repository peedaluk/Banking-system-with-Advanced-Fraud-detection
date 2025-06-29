function showForm(type) {
    // Toggle buttons
    document.getElementById('btn-user').classList.remove('active');
    document.getElementById('btn-admin').classList.remove('active');
    document.getElementById('btn-atm').classList.remove('active');
    if (document.getElementById('btn-register')) document.getElementById('btn-register').classList.remove('active');
    if (type === 'user') document.getElementById('btn-user').classList.add('active');
    if (type === 'admin') document.getElementById('btn-admin').classList.add('active');
    if (type === 'atm') document.getElementById('btn-atm').classList.add('active');
    if (type === 'register' && document.getElementById('btn-register')) document.getElementById('btn-register').classList.add('active');

    // Toggle forms
    document.getElementById('user-login-form').classList.remove('active');
    document.getElementById('admin-login-form').classList.remove('active');
    document.getElementById('atm-login-form').classList.remove('active');
    if (document.getElementById('register-form')) document.getElementById('register-form').classList.remove('active');
    if (type === 'user') document.getElementById('user-login-form').classList.add('active');
    if (type === 'admin') document.getElementById('admin-login-form').classList.add('active');
    if (type === 'atm') document.getElementById('atm-login-form').classList.add('active');
    if (type === 'register' && document.getElementById('register-form')) document.getElementById('register-form').classList.add('active');
}

// User login
document.getElementById('user-login-form').onsubmit = function(e) {
    e.preventDefault();
    const form = e.target;
    fetch('/user/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: form.username.value,
            password: form.password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('user-login-result').innerText = data.message || data.error;
        if (data.message) window.location.href = '/user/dashboard';
    });
};

// Admin login
document.getElementById('admin-login-form').onsubmit = function(e) {
    e.preventDefault();
    const form = e.target;
    fetch('/admin/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: form.username.value,
            password: form.password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('admin-login-result').innerText = data.message || data.error;
        if (data.message) window.location.href = '/admin/dashboard';
    });
};

// ATM login
document.getElementById('atm-login-form').onsubmit = function(e) {
    e.preventDefault();
    const form = e.target;
    fetch('/atm/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            card_number: form.card_number.value,
            pin: form.pin.value
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('atm-login-result').innerText = data.message || data.error;
        if (data.message) window.location.href = '/atm/panel';
    });
};

// User registration
if (document.getElementById('register-form')) {
    console.log("Register form submit handler attached!");
    document.getElementById('register-form').onsubmit = function(e) {
        e.preventDefault();
        const form = e.target;
        fetch('/user/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: form.username.value,
                email: form.email.value,
                password: form.password.value,
                referral_code: form.referral_code.value
            })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('register-result').innerText = data.message || data.error;
            if (data.message) {
                window.location.href = '/user/dashboard';
            }

        });
    };
} 

// Show user login by default
showForm('user');
