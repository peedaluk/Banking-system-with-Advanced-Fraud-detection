from models.transaction_graph import transaction_graph

def add_transaction_and_run_fraud(
    mysql,
    src_account_id,
    dst_account_id,
    amount,
    txn_type,
    description,
    mail,
    admin_emails
):
    from datetime import datetime
    conn = mysql.connection
    cur = conn.cursor()
    try:
        timestamp = datetime.utcnow()

        # Handle transfer (debit src, credit dst)
        if txn_type == 'transfer_out':
            # Check source balance
            cur.execute("SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE", (src_account_id,))
            src_balance = cur.fetchone()[0]
            if src_balance < amount:
                return {'success': False, 'message': 'Insufficient funds.'}

            # Update balances
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, src_account_id))
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, dst_account_id))

            # Insert transactions
            cur.execute("""
                INSERT INTO transactions (account_id, type, amount, description, related_account_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (src_account_id, 'transfer_out', amount, description, dst_account_id, timestamp))
            cur.execute("""
                INSERT INTO transactions (account_id, type, amount, description, related_account_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (dst_account_id, 'transfer_in', amount, f'Transfer from account {src_account_id}', src_account_id, timestamp))

            # Update in-memory graph
            transaction_graph.add_transaction(src_account_id, dst_account_id, amount, timestamp)

        # Handle withdrawal
        elif txn_type == 'withdrawal':
            cur.execute("SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE", (src_account_id,))
            balance = cur.fetchone()[0]
            if balance < amount:
                return {'success': False, 'message': 'Insufficient funds.'}
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, src_account_id))
            cur.execute("""
                INSERT INTO transactions (account_id, type, amount, description, timestamp)VALUES (%s, %s, %s, %s, %s)""", (src_account_id, 'withdrawal', amount, description, timestamp))
            #transaction_graph.add_transaction(src_account_id, None, amount, timestamp)

        # Handle deposit
        elif txn_type == 'deposit':
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, src_account_id))
            cur.execute("""
                INSERT INTO transactions (account_id, type, amount, description, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (src_account_id, 'deposit', amount, description, timestamp))
            #transaction_graph.add_transaction(src_account_id, src_account_id, amount, timestamp)

        conn.commit() 

        # Run fraud detection
        from models.fraud_detection import detect_suspicious_cycles
        graph = transaction_graph.get_graph()
        suspicious_cycles = detect_suspicious_cycles(graph, alpha=0.1, min_cycle_length=3)
        if suspicious_cycles:
            body = "Suspicious cycles detected:\n\n" + "\n\n".join(
                f"Accounts: {cycle['accounts']}\nTransactions: {cycle['transactions']}" for cycle in suspicious_cycles
            )
            msg = mail.Message(
                subject="Fraud Alert: Suspicious Transaction Cycle Detected",
                recipients=admin_emails,
                body=body
            )
            mail.send(msg)

        return {'success': True, 'message': 'Transaction completed and checked for fraud.'}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()


