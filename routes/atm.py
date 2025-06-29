from flask import Blueprint, request, jsonify, session, current_app,render_template,redirect

from models.transaction import add_transaction_and_run_fraud

atm_bp = Blueprint('atm', __name__, url_prefix='/atm')

# --- ATM Login ---
@atm_bp.route('/login', methods=['POST'])
def atm_login():
    data = request.get_json()
    card_number = data.get('card_number')
    pin = data.get('pin')
    mysql = current_app.config['MYSQL']
    bcrypt = current_app.config['BCRYPT']
    cur = mysql.connection.cursor()
    cur.execute("SELECT account_id, pin_hash FROM accounts WHERE card_number = %s", (card_number,))
    account = cur.fetchone()
    cur.close()

    if account and bcrypt.check_password_hash(account[1], pin):
        session['atm_account_id'] = account[0]
        return jsonify({'message': 'ATM login successful!'}), 200
    else:
        return jsonify({'error': 'Invalid card number or PIN'}), 401


# --- ATM Logout ---
@atm_bp.route('/logout', methods=['POST'])
def atm_logout():
    session.pop('atm_account_id', None)
    return jsonify({'message': 'ATM session ended.'}), 200

def is_atm_logged_in():
    return 'atm_account_id' in session

@atm_bp.route('/panel', methods=['GET'])
def atm_panel():
    if('atm_account_id' not in session):
        return redirect('/login')
    return render_template('atm_panel.html')

# --- Cash Withdrawal ---
@atm_bp.route('/withdraw', methods=['POST'])
def atm_withdraw():
    if not is_atm_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    amount = float(data.get('amount'))
    account_id = session['atm_account_id']

    result = add_transaction_and_run_fraud(
        mysql=current_app.config['MYSQL'],
        src_account_id=account_id,
        dst_account_id= None,
        amount=amount,
        txn_type='withdrawal',
        description=f'withdrawl from {account_id}',
        mail=current_app.extensions['mail'],
        admin_emails=["admin@example.com"]
    )
    if result['success']:
        return jsonify({'message': f'withdrwl of {amount} from {account_id} is succesful'}), 200
    else:
        return jsonify({'error': result['message']}), 400

# --- Cash Deposit ---
@atm_bp.route('/deposit', methods=['POST'])
def atm_deposit():
    if not is_atm_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    amount = float(data.get('amount'))
    account_id = session['atm_account_id']

    result = add_transaction_and_run_fraud(
        mysql=current_app.config['MYSQL'],
        src_account_id=account_id,
        dst_account_id= None,
        amount=amount,
        txn_type='deposit',
        description=f'deposit to {account_id}',
        mail=current_app.extensions['mail'],
        admin_emails=["admin@example.com"]
    )

    if result['success']:
        return jsonify({'message': f'deposit of {amount} to {account_id} is succesful'}), 200
    else:
        return jsonify({'error': result['message']}), 400


# --- Cash Transfer
@atm_bp.route('/transfer', methods=['POST'])
def atm_transfer():
    if not is_atm_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    amount = float(data.get('amount'))
    to_account = data.get('to_account')
    from_account_id = session['atm_account_id']
    mysql = current_app.config['MYSQL']
    mail = current_app.extensions['mail']

    # Find destination account
    cur = mysql.connection.cursor()
    cur.execute("SELECT account_id FROM accounts WHERE account_number = %s", (to_account,))
    to_acc = cur.fetchone()
    cur.close()
    if not to_acc:
        return jsonify({'error': 'Destination account not found'}), 404
    to_account_id = to_acc[0]

    # Call the utility function
    result = add_transaction_and_run_fraud(
        mysql=mysql,
        src_account_id=from_account_id,
        dst_account_id=to_account_id,
        amount=amount,
        txn_type='transfer_out',
        description=f'ATM transfer to {to_account}',
        mail=mail,
        admin_emails=["admin@example.com"]
    )

    if result['success']:
        return jsonify({'message': f'Transfer of ₹{amount} to account {to_account} successful.'}), 200
    else:
        return jsonify({'error': result['message']}), 400


# --- Mini Statement ---
@atm_bp.route('/mini_statement', methods=['GET'])
def atm_mini_statement():
    if 'atm_account_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    account_id = session['atm_account_id']
    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()

    # Fetch account info
    cur.execute("SELECT card_number, account_number, account_type, balance FROM accounts WHERE account_id = %s", (account_id,))
    acc = cur.fetchone()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404

    card_number, account_number, account_type, balance = acc

    # Fetch all recent transactions for this account (limit 10)
    cur.execute("""
        SELECT type, amount, description, timestamp
        FROM transactions
        WHERE account_id = %s
        ORDER BY timestamp DESC
        LIMIT 10
    """, (account_id,))
    transactions = [
        {
            'type': row[0],
            'amount': float(row[1]),
            'description': row[2],
            'timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S')
        }
        for row in cur.fetchall()
    ]

    cur.close()
    return jsonify({
        'card_number': card_number,
        'account_number': account_number,
        'account_type': account_type,
        'balance': float(balance),
        'transactions': transactions
    })