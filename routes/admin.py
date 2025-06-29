from flask import Blueprint, request, jsonify, session, current_app, render_template, redirect

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Helper function to check admin status ---
def is_admin():
    return session.get('is_admin', False)

# --- Admin Dashboard Page ---
@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    if not is_admin():
        return redirect('/login')
    return render_template('admin_dashboard.html')

# --- Dashboard Stats ---
@admin_bp.route('/dashboard/data', methods=['GET'])
def dashboard_data():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions")
    total_txns = cur.fetchone()[0]

    cur.execute("SELECT SUM(balance) FROM accounts")
    total_balance = float(cur.fetchone()[0] or 0)

    cur.close()
    return jsonify({
        'total_users': total_users,
        'total_transactions': total_txns,
        'total_balance': total_balance
    }), 200

# --- List Users ---
@admin_bp.route('/users', methods=['GET'])
def get_users():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, username, email, created_at, is_admin, is_blocked FROM users")
    users = [
        {
            'user_id': row[0],
            'username': row[1],
            'email': row[2],
            'joined': row[3].strftime('%Y-%m-%d'),
            'is_admin': bool(row[4]),
            'is_blocked': bool(row[5])
        }
        for row in cur.fetchall()
    ]
    cur.close()
    return jsonify({'users': users}), 200

# --- List Recent Transactions ---
@admin_bp.route('/transactions', methods=['GET'])
def get_transactions():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.transaction_id, t.type, t.amount, t.description, t.timestamp, a.account_id, a.user_id
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        ORDER BY t.timestamp DESC
        LIMIT 100
    """)
    txns = [
        {
            'transaction_id': row[0],
            'type': row[1],
            'amount': float(row[2]),
            'description': row[3],
            'timestamp': row[4].strftime('%Y-%m-%d %H:%M:%S'),
            'account_id': row[5],
            'user_id': row[6]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    return jsonify({'transactions': txns}), 200

# --- Block/Unblock User ---
@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
def block_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET is_blocked = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': f'User {user_id} blocked.'}), 200

@admin_bp.route('/users/<int:user_id>/unblock', methods=['POST'])
def unblock_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET is_blocked = FALSE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': f'User {user_id} unblocked.'}), 200

# --- Admin Logout ---
@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return jsonify({'message': 'Admin logged out.'}), 200

# --- (Optional) Admin Login (POST /admin/login) ---
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    mysql = current_app.config['MYSQL']

    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, password_hash, is_admin FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    from werkzeug.security import check_password_hash
    if user and check_password_hash(user[1], password) and user[2]:
        session['user_id'] = user[0]
        session['is_admin'] = True
        return jsonify({'message': 'Admin login successful!'}), 200
    else:
        return jsonify({'error': 'Invalid credentials or not an admin'}), 401

# --- Register Blueprint in your main app ---
# from admin_routes import admin_bp
# app.register_blueprint(admin_bp)
