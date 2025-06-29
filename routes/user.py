from flask import Blueprint, request, current_app, session, jsonify,render_template,redirect
import random
from models.user_dashboard import user_dashboard

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/register', methods=['POST'])
def register():
    mysql = current_app.config['MYSQL']
    bcrypt = current_app.config['BCRYPT']

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    referral_code = data.get('referral_code')  # Optional

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    parent_id = None
    if referral_code:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE referral_code = %s", (referral_code,))
        parent = cur.fetchone()
        cur.close()
        if parent:
            parent_id = parent[0]
        else:
            return jsonify({'error': 'Invalid referral code'}), 400

    # Generate a unique referral code for the new user
    import uuid
    new_referral_code = str(uuid.uuid4())[:8]

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, email, password_hash, referral_code, parent_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, pw_hash, new_referral_code, parent_id))
        mysql.connection.commit()
        cur.execute("SELECT user_id WHERE username = %s",(username,))
        user_id = cur.fetchone()
        session['user_id'] = user_id
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()

@user_bp.route('/login', methods=['POST'])
def login():
    mysql = current_app.config['MYSQL']
    bcrypt = current_app.config['BCRYPT']

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[1], password):
        session['user_id'] = user[0]
        return jsonify({'message': 'Login successful!', 'user_id': user[0]}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully.'}), 200

@user_bp.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, email FROM users WHERE user_id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    if user:
        return jsonify({'username': user[0], 'email': user[1]}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@user_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('user_dashboard.html')

@user_bp.route('/dashboard/data', methods=['GET'])
def dashboard_data():
    # Your code to fetch and return JSON data
    return user_dashboard()



@user_bp.route('/create_account', methods=['POST'])
def create_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    account_type = data.get('account_type', 'savings').lower()
    if account_type not in ['savings', 'current']:
        return jsonify({'error': 'Invalid account type'}), 400

    user_id = session['user_id']
    bcrypt = current_app.config['BCRYPT']
    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()

    # Generate unique 10-digit account number
    account_number = str(random.randint(1000000000, 9999999999))

    # Generate unique 16-digit card number (for demo, random; in real life, use Luhn algorithm)
    card_number = str(random.randint(4000000000000000, 4999999999999999))

    # Generate random 4-digit PIN and hash it
    pin = str(random.randint(1000, 9999))
    pin_hash = bcrypt.generate_password_hash(pin).decode('utf-8')

    try:
        cur.execute(
            "INSERT INTO accounts (user_id, account_type, account_number, balance, card_number, pin_hash) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, account_type, account_number, 0.0, card_number, pin_hash)
        )
        mysql.connection.commit()
        return jsonify({
            'message': 'Account created successfully!',
            'account_number': account_number,
            'account_type': account_type,
            'card_number': card_number,
            'pin': pin  # Show PIN once; user should note it down!
        }), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()

@user_bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    account_id = data.get('account_id')
    card_number = data.get('card_number')
    pin = data.get('pin')
    user_id = session['user_id']
    bcrypt = current_app.config['BCRYPT']
    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()

    try:
        # Fetch account and verify ownership
        cur.execute("""
            SELECT balance, card_number, pin_hash
            FROM accounts
            WHERE account_id = %s AND user_id = %s
        """, (account_id, user_id))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Account not found or unauthorized'}), 404

        balance, db_card_number, db_pin_hash = row

        # First, check card number and PIN
        if not card_number or card_number != db_card_number:
            return jsonify({'error': 'Card number does not match'}), 400

        if not pin or not bcrypt.check_password_hash(db_pin_hash, pin):
            return jsonify({'error': 'Invalid PIN'}), 400

        # Then, check balance
        if float(balance) != 0.0:
            return jsonify({'error': 'Account balance must be zero to delete'}), 400

        # Delete account (or soft-delete if you prefer)
        cur.execute("DELETE FROM accounts WHERE account_id = %s AND user_id = %s", (account_id, user_id))
        mysql.connection.commit()
        return jsonify({'message': 'Account deleted successfully!'}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
