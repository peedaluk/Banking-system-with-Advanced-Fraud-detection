from flask import session, current_app, jsonify
from datetime import datetime

def user_dashboard():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mysql = current_app.config['MYSQL']
    cur = mysql.connection.cursor()

    try:
        # Fetch username
        cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({'error': 'User not found'}), 404
        username = user_row[0]

        # Fetch accounts
        cur.execute("SELECT account_id, account_type, balance, card_number, account_number FROM accounts WHERE user_id = %s", (user_id,))
        accounts = []
        for row in cur.fetchall():
            accounts.append({
                'account_id': row[0],
                'account_type': row[1],
                'balance': float(row[2]),
                'card_number': row[3],
                'account_number': row[4]
            })

        # Fetch recent transactions
        cur.execute("""
            SELECT t.type, t.amount, t.description, t.timestamp, a.account_id, t.related_account_id
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = %s
            ORDER BY t.timestamp DESC
            LIMIT 10
        """, (user_id,))
        transactions = []
        for row in cur.fetchall():
            # Format timestamp consistently
            timestamp = row[3]
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
            transactions.append({
                'type': row[0],
                'amount': float(row[1]),
                'description': row[2],
                'timestamp': timestamp,
                'account_id': row[4],
                'related_account_id': row[5]
            })

        # Fetch referral count
        cur.execute("SELECT COUNT(*) FROM users WHERE parent_id = %s", (user_id,))
        referral_count = cur.fetchone()[0]

        return jsonify({
            'username': username,
            'accounts': accounts,
            'transactions': transactions,
            'referral_count': referral_count
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in user_dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cur.close()
